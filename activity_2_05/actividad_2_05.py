import time
import sys
import math
import numpy as np
import cv2

class TrafficLightDetection:
    def __init__(self):
        self.cameraWidth = 320
        self.cameraHeight = 240
        
        self.red_lower1 = np.array([0, 50, 50])
        self.red_upper1 = np.array([10, 255, 255])
        self.red_lower2 = np.array([170, 50, 50])
        self.red_upper2 = np.array([180, 255, 255])
        
        self.yellow_lower = np.array([20, 80, 80])
        self.yellow_upper = np.array([30, 255, 255])
        
        self.green_lower = np.array([35, 50, 50])
        self.green_upper = np.array([85, 255, 255])
        
        self.min_area = 30
        
    def detect_state(self, image):
        if image is None:
            return "none"
        
        h, w = image.shape[:2]
        roi = image[:, :w//2]
        
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
        
        mask_red1 = cv2.inRange(hsv, self.red_lower1, self.red_upper1)
        mask_red2 = cv2.inRange(hsv, self.red_lower2, self.red_upper2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        
        mask_yellow = cv2.inRange(hsv, self.yellow_lower, self.yellow_upper)
        mask_green = cv2.inRange(hsv, self.green_lower, self.green_upper)
        
        kernel = np.ones((3, 3), np.uint8)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
        
        mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)
        mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_CLOSE, kernel)
        
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
        
        red_info = self._analyze_color(mask_red, roi)
        yellow_info = self._analyze_color(mask_yellow, roi)
        green_info = self._analyze_color(mask_green, roi)
        
        detections = []
        
        if red_info['area'] > self.min_area and red_info['circularity'] > 0.3:
            detections.append(('red', red_info['area'], red_info['y_pos']))
        
        if yellow_info['area'] > self.min_area and yellow_info['circularity'] > 0.3:
            detections.append(('yellow', yellow_info['area'], yellow_info['y_pos']))
        
        if green_info['area'] > self.min_area and green_info['circularity'] > 0.3:
            detections.append(('green', green_info['area'], green_info['y_pos']))
        
        if not detections:
            return "none"
        
        if len(detections) > 1:
            detections.sort(key=lambda x: x[2])
            
            for color, area, y_pos in detections:
                if color == 'red' and y_pos < roi.shape[0] * 0.4:
                    return 'red'
                elif color == 'yellow' and 0.3 < y_pos / roi.shape[0] < 0.7:
                    return 'yellow'
                elif color == 'green' and y_pos > roi.shape[0] * 0.5:
                    return 'green'
        
        detections.sort(key=lambda x: x[1], reverse=True)
        return detections[0][0]
    
    def _analyze_color(self, mask, image):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_area = 0
        y_positions = []
        circularities = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    
                    if circularity > 0.2:
                        total_area += area
                        circularities.append(circularity)
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cy = int(M["m01"] / M["m00"])
                            y_positions.append(cy)
        
        avg_y = np.mean(y_positions) if y_positions else image.shape[0] // 2
        avg_circ = np.mean(circularities) if circularities else 0.0
        
        return {
            'area': total_area,
            'y_pos': avg_y,
            'circularity': avg_circ
        }
