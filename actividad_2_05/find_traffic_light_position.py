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

class PositionLogger():
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
        self.frame_counter = 0
        
        # Posición estimada (integración de velocidades)
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0

    def callback(self):
        self.dataconfig.resetRobot = True
        self.dataconfig.mode = 2
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
        res=self.stub.SetConfiguration(self.dataconfig)
        self.dataconfig.resetRobot = False
        time.sleep(0.25)
        res=self.stub.SetConfiguration(self.dataconfig)

        print("="*60)
        print("LOGGER DE POSICIÓN - Buscando semáforo")
        print("="*60)
        print("Formato: Frame | Tiempo | Posición (x, y, z) | Rotación (x, y, z)")
        print("="*60)

        while self.running:
            frame = self.stub.GetImageFrame(req)
            img_buffer=np.frombuffer(frame.data, np.uint8)
            img_in=cv2.imdecode(img_buffer, cv2.IMREAD_COLOR)
            img = img_in
            if img_in is not None:
                img=self.add_noise_to_image(img_in, 3)

            new_width = 320
            new_height = 240
            new_dim = (new_width, new_height)
            self.cv_image = cv2.resize(img, new_dim, interpolation=cv2.INTER_LANCZOS4)
    
            # Comandos de velocidad para recorrer
            self.twist=[0.01,0.0,0.0,0.0,0.0,-0.001]
            self.datacmd.linear.x=self.twist[0]
            self.datacmd.linear.y=self.twist[1]
            self.datacmd.linear.z=self.twist[2]
            self.datacmd.angular.x=self.twist[3]
            self.datacmd.angular.y=self.twist[4]
            self.datacmd.angular.z=self.twist[5]
            self.stub.SetCommand(self.datacmd)

            # Estimar posición integrando velocidades
            # En coordenadas del robot (frame local)
            cos_theta = np.cos(self.rot_z)
            sin_theta = np.sin(self.rot_z)
            
            # Transformar velocidad local a global
            vx_global = self.twist[0] * cos_theta - self.twist[1] * sin_theta
            vy_global = self.twist[0] * sin_theta + self.twist[1] * cos_theta
            
            # Integrar posición
            self.pos_x += vx_global * self.timer_delta
            self.pos_y += vy_global * self.timer_delta
            self.pos_z += self.twist[2] * self.timer_delta
            
            # Integrar rotación
            self.rot_x += self.twist[3] * self.timer_delta
            self.rot_y += self.twist[4] * self.timer_delta
            self.rot_z += self.twist[5] * self.timer_delta
            
            # Log cada 25 frames (aproximadamente cada segundo)
            self.frame_counter += 1
            if self.frame_counter % 25 == 0:
                print(f"Frame {frame.seq:5d} | "
                      f"T: {self.running_time:6.2f}s | "
                      f"Pos: ({self.pos_x:7.3f}, {self.pos_y:7.3f}, {self.pos_z:7.3f}) | "
                      f"Rot: ({self.rot_x:6.3f}, {self.rot_y:6.3f}, {self.rot_z:6.3f})")

            # Mostrar imagen con overlay de posición
            cv2.putText(self.cv_image, f"Pos: ({self.pos_x:.2f}, {self.pos_y:.2f})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(self.cv_image, f"Rot Z: {self.rot_z:.2f}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(self.cv_image, f"Time: {self.running_time:.1f}s", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow('Position Logger', self.cv_image)
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
    robot_node = PositionLogger()
    thread = threading.Thread(target=robot_node.callback)
    thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("Deteniendo logger...")
        print("="*60)
        robot_node.running = False
        thread.join()
        cv2.destroyAllWindows()
        print("Logger detenido")

if __name__ == "__main__":
    main()
