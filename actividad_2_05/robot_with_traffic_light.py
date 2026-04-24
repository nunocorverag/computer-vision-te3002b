import cv2
import numpy as np
import threading
import time
import sys
import os

import grpc
sys.path.insert(0, '../actividad_2_04')
import te3002b_pb2
import te3002b_pb2_grpc
import google.protobuf.empty_pb2

from actividad_2_05 import TrafficLightDetection

class CenterLineDetector:
    def __init__(self):
        self.cameraWidth = 320
        self.cameraHeight = 240
        self.debug_mask = None
        self.last_center = (self.cameraWidth // 2, int(self.cameraHeight * 0.875))
        self.max_jump_distance = 75  

    def detect_center_line(self, image):
        h, w = image.shape[:2]

        y_start = int(h * 0.75) 
        x_start = int(w * 0.25) 
        x_end = int(w * 0.75)   
        roi = image[y_start:h, x_start:x_end]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
        _, mask = cv2.threshold(
            blurred, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        kernel = np.ones((5, 5), np.uint8) 
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        self.debug_mask = mask

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        best_candidate = None
        best_score = float('inf')
        cx_screen_center = w / 2.0

        for c in contours:
            area = cv2.contourArea(c)
            
            if area < 250: 
                continue

            _, _, _, h_box = cv2.boundingRect(c)
            if h_box < 15:
                continue

            moments = cv2.moments(c)
            if moments["m00"] == 0:
                continue

            cx = int(moments["m10"] / moments["m00"]) + x_start
            cy = int(moments["m01"] / moments["m00"]) + y_start

            dist_to_center = abs(cx - cx_screen_center)
            dist_to_last = ((cx - self.last_center[0])**2 + (cy - self.last_center[1])**2)**0.5

            if dist_to_last > self.max_jump_distance:
                continue

            score = (dist_to_center * 0.2) + (dist_to_last * 0.8)

            if score < best_score:
                best_score = score
                best_candidate = (cx, cy)

        if best_candidate is not None:
            self.last_center = best_candidate

        return self.last_center

class RobotWithTrafficLight():
    def __init__(self):
        self._addr="127.0.0.1"
        self.channel=grpc.insecure_channel(self._addr+':7072')
        self.stub = te3002b_pb2_grpc.TE3002BSimStub(self.channel)

        self.cv_image = None 
        self.result=None
        self.datacmd=te3002b_pb2.CommandData()
        self.dataconfig=te3002b_pb2.ConfigurationData()
        self.twist=[0,0,0,0,0,0]
        self.running = True
        self.timer_delta=0.025
        self.running_time=0.0
        
        self.line_detector = CenterLineDetector()
        self.traffic_detector = TrafficLightDetection()
        self.frame_counter = 0

    def callback(self):
        self.dataconfig.resetRobot = True
        self.dataconfig.mode = 1
        self.dataconfig.cameraWidth = 360
        self.dataconfig.cameraHeight = 240
        self.dataconfig.resetCamera = False
        self.dataconfig.scene = 2026
        self.dataconfig.cameraLinear.x = 0
        self.dataconfig.cameraLinear.y = 0
        self.dataconfig.cameraLinear.z = 0
        self.dataconfig.cameraAngular.x  = 0
        self.dataconfig.cameraAngular.y  = 0
        self.dataconfig.cameraAngular.z  = 0
        
        req=google.protobuf.empty_pb2.Empty()
        self.twist=[0.0,0.0,0.0,0.0,0.0,0]
        self.stub.SetConfiguration(self.dataconfig)
        self.dataconfig.resetRobot = False
        time.sleep(0.25)
        self.stub.SetConfiguration(self.dataconfig)

        while self.running:
            self.result = self.stub.GetImageFrame(req)
            img_buffer=np.frombuffer(self.result.data, np.uint8)
            img_in=cv2.imdecode(img_buffer, cv2.IMREAD_COLOR)
            
            if img_in is not None:
                img=self.add_noise_to_image(img_in, 3)
            else:
                img = img_in

            new_width = 320
            new_height = 240
            new_dim = (new_width, new_height)
            self.cv_image = cv2.resize(img, new_dim, interpolation=cv2.INTER_LANCZOS4)
 
            # Detectar semáforo
            traffic_state = self.traffic_detector.detect_state(self.cv_image)
            
            # Detectar línea
            best_candidate = self.line_detector.detect_center_line(self.cv_image)
            
            # Lógica de control basada en semáforo
            speed = 0.0
            turn = 0.0
            
            if traffic_state == 'red':
                # Detenerse en rojo
                speed = 0.0
                turn = 0.0
            elif traffic_state == 'yellow':
                # Reducir velocidad en amarillo
                speed = 0.015
                if best_candidate is not None:
                    cx, cy = best_candidate
                    center_of_screen = new_width / 2.0
                    error = center_of_screen - cx
                    kp = 0.005
                    turn = error * kp
            else:  # green o none
                # Velocidad normal
                speed = 0.025
                if best_candidate is not None:
                    cx, cy = best_candidate
                    center_of_screen = new_width / 2.0
                    error = center_of_screen - cx
                    kp = 0.005
                    turn = error * kp

            # Visualización
            if best_candidate is not None:
                cx, cy = best_candidate
                cv2.circle(self.cv_image, (int(cx), int(cy)), 5, (0, 0, 255), -1)

            # Mostrar estado del semáforo
            color_map = {
                'red': (0, 0, 255),
                'yellow': (0, 255, 255),
                'green': (0, 255, 0),
                'none': (128, 128, 128)
            }
            color = color_map.get(traffic_state, (255, 255, 255))
            cv2.putText(self.cv_image, f"Traffic: {traffic_state.upper()}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(self.cv_image, f"Speed: {speed:.3f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Enviar comandos
            self.twist = [speed, 0.0, 0.0, 0.0, 0.0, turn]
            self.datacmd.linear.x=self.twist[0]
            self.datacmd.linear.y=self.twist[1]
            self.datacmd.linear.z=self.twist[2]
            self.datacmd.angular.x=self.twist[3]
            self.datacmd.angular.y=self.twist[4]
            self.datacmd.angular.z=self.twist[5]
            self.stub.SetCommand(self.datacmd)

            # Mostrar vista principal
            cv2.imshow('Robot with Traffic Light', self.cv_image)
            
            # Mostrar máscara de línea
            if self.line_detector.debug_mask is not None:
                cv2.imshow('Line Mask', self.line_detector.debug_mask)

            # Log cada 50 frames
            self.frame_counter += 1
            if self.frame_counter % 50 == 0:
                print(f"Frame {self.result.seq}: Traffic={traffic_state}, Speed={speed:.3f}")

            cv2.waitKey(1)
            time.sleep(self.timer_delta-0.001)
            self.running_time=self.running_time+self.timer_delta

    def add_noise_to_image(self,image, kernel_s, noise_level=5):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        noise = np.random.randint(-noise_level, noise_level + 1, v.shape, dtype='int16')
        v_noisy = v.astype('int16') + noise
        v_noisy = np.clip(v_noisy, 0, 255).astype('uint8')
        hsv_noisy = cv2.merge([h, s, v_noisy])
        noisy_image = cv2.cvtColor(hsv_noisy, cv2.COLOR_HSV2BGR)
        noisy_image = cv2.GaussianBlur(noisy_image, (kernel_s, kernel_s), 0)
        alpha = 0.55
        beta = 55
        output_image = cv2.convertScaleAbs(noisy_image, alpha=alpha, beta=beta)
        return output_image

def main(args=None):
    robot_node = RobotWithTrafficLight()
    thread = threading.Thread(target=robot_node.callback)
    thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Deteniendo el robot...")
        robot_node.running = False
        thread.join()
        cv2.destroyAllWindows()
        print("Robot detenido de forma segura.")

if __name__ == "__main__":
    main()
