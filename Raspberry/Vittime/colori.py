import cv2 as cv
import numpy as np

class colors:
    def __init__(self, nome):
        self.nome = nome
        self.areamin = 1200
        
        self.low_g = np.array([40, 90, 35])
        self.high_g = np.array([100, 240, 200])
        
        self.low_y = np.array([20, 100, 100])
        self.high_y = np.array([30, 255, 255])
        
        self.low_r = np.array([0, 50, 50])
        self.high_r = np.array([10, 255, 255])
        self.low_r2 = np.array([170, 50, 50])
        self.high_r2 = np.array([180, 255, 255])
        
        self.col_N = -1
        
    def find(self, blur, frame):
        
        self.col_N = -1
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, self.low_g, self.high_g)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > self.areamin:
               print("Telecamera", self.nome, "VERDE")
               self.col_N = 0
               return hsv, self.col_N
                
        mask = cv.inRange(hsv, self.low_y, self.high_y)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > self.areamin:
               print("Telecamera", self.nome, "GIALLO")
               self.col_N = 1
               return hsv, self.col_N
            
        rmask = cv.inRange(hsv, self.low_r, self.high_r)
        rmask += cv.inRange(hsv, self.low_r2, self.high_r2)
        contours, hierarchy = cv.findContours(rmask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > self.areamin:
               print("Telecamera", self.nome, "ROSSO")
               self.col_N = 1
               return rmask, self.col_N
        
#         if self.col_N == -1:
#             print("Telecamera", self.nome, "NO COLOR")
        return hsv, self.col_N
