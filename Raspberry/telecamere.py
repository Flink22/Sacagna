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
        self.cam = 0;
        
        self.cam = cv.VideoCapture(self.cam)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposuretime)
        
        if not self.cam.isOpened():
            print("Telecamera SX Error")
    
    def main(self, check = True):
        try:
            while True:
                
                #queue get no wait
                
                ret, frame = self.cam.read()
                
                frame = frame[200:700, 200:1080]
                frame = cv.resize(frame, (320, 240), interpolation= cv.INTER_LINEAR)
                
                blur = cv.GaussianBlur(frame, (7,7), 0)
                
                if check == True:
                    cframe, n_d = self.col.find(blur, frame)
                    if n_d == -1:
                        lframe, n_d = self.let.find(blur, frame)
                        cv.imshow('lettere', lframe)
                    print(n_d)
                
                
                cv.imshow('colori', cframe)
                cv.imshow('frame', frame)
#                 cv.imshow('thresh', thresh)
                
                check = True 

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            None
            self.close()
    
    def close(self):
        self.cam.release()

if __name__ == '__main__':
    tel = cameras()
    tel.main()
