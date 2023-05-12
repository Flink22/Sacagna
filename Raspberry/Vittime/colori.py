import cv2 as cv
import numpy as np

class colors:
    def __init__(self):
        
        self.areamin = 3000
        
        self.low_g = np.array([0, 200, 0])
        self.high_g = np.array([0, 255, 0])
        self.low_g2 = np.array([200, 200, 0])
        self.high_g2 = np.array([255, 255, 0])
        
        self.low_y = np.array([0, 200, 200])
        self.high_y = np.array([0, 255, 255])
        
        self.low_r = np.array([0, 0, 200])
        self.high_r = np.array([0, 0, 255])
        
        self.col_N = 0
        
    def find(self, blur, frame):
        
        self.col_N = -1
        
        ret,thresh1 = cv.threshold(blur, 60, 255, cv.THRESH_BINARY)
        mask = cv.inRange(thresh1, self.low_g, self.high_g)
        mask2 = cv.inRange(thresh1, self.low_g2, self.high_g2)
        mask += mask2
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > self.areamin:
               print("VERDE")
               self.col_N = 0
               return thresh1, self.col_N
        
        ret,thresh2 = cv.threshold(blur, 130, 255, cv.THRESH_BINARY)
        
        mask = cv.inRange(thresh2, self.low_y, self.high_y)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > 5000:
               print("GIALLO")
               self.col_N = 1
               return thresh2, self.col_N
            
        mask = cv.inRange(thresh2, self.low_r, self.high_r)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > self.areamin:
               print("ROSSO")
               self.col_N = 1
               return thresh2, self.col_N
        
        if self.col_N == -1:
            print("NO COLOR")
        return thresh1, self.col_N
