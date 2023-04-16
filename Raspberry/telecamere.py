import cv2 as cv
import numpy as np
from lettere import letters
from colori import colors
import queue as Queue
import multiprocessing

class cameras:
    def __init__(self):
        self.let = letters()
        self.col = colors()
        
        self.exposuretime = 500 #va da 78 a 1250
        self.cam = 1;
        
        self.camdx = cv.VideoCapture(0)
        self.camdx.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.camdx.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.camdx.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
        self.camdx.set(cv.CAP_PROP_EXPOSURE, self.exposuretime)
        
        if not self.camdx.isOpened():
            print("Telecamera DX Error")
    
    def read(self, check=True, on=True):
        try:
            while on == True:
                
                ret, frame = self.camdx.read()
                
                frame = frame[200:720, 200:1080]
                frame = cv.resize(frame, (320, 240), interpolation= cv.INTER_LINEAR)
                
                blur = cv.GaussianBlur(frame,(7,7),0)
                ret,thresh = cv.threshold(blur,100,255,cv.THRESH_BINARY)
                
                if check == True:
                    lframe, n_d = self.let.find(thresh, frame)
                    if n_d == -1:
                        col.find(thresh)
                    
                    if n_d == 0:
                
                cv.imshow('lettere', l)
                cv.imshow('frame', frame)
#                 cv.imshow('thresh', thresh)
                
                check = 0

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            None
            self.close()
    
    def close(self):
        self.camdx.release()

if __name__ == '__main__':
    tel = cameras()
    tel.read()
