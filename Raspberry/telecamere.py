import cv2 as cv
import imutils
import numpy as np
from lettere import letters
from colori import colors
import queue as Queue
from seriale import SERIALEPICO


class CAMERAS:
    def __init__(self, exposure, cap, nome):
        self.let = letters()
        self.col = colors()
        
        self.exposuretime = exposure #va da 78 a 1250
        self.nome = nome
        self.check = True
        
        self.cam = cap
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposuretime)

        
        if not self.cam.isOpened():
            print("Telecamera", nome, " Error")
    
    def main(self, cam_q, vittima):
        try:
            ser = SERIALEPICO()
            while True:
                
                try:
                    self.check = cam_q.get_nowait()
                except Queue.Empty:
                    self.check = False
                    pass
                
                self.cam.grab()
                ret, frame = self.cam.read()
                
                frame = frame[200:550, 200:1280]
                frame = cv.resize(frame, (320, 240), interpolation= cv.INTER_LINEAR)
            
                blur = cv.GaussianBlur(frame, (7,7), 0)
                
#                 self.check = True
                
                if self.check == True:
                    cframe, n_d = self.col.find(blur, frame)
                    cv.imshow('colori', cframe)
                    if n_d == -1:
                        lframe, n_d = self.let.find(blur, frame)
                        cv.imshow('lettere', lframe)
                    try:
                        vittima.put_nowait(n_d)
                    except Queue.Full:
                        None
                    
                    print(n_d)
                    ser.askK(n_d, self.nome)
            
                
                cv.imshow(self.nome, frame)
#                 cv.imshow('thresh', thresh)

                self.check = False
            
                
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            None
            self.close()
    
    def close(self):
        self.cam.release()
        cv2.closeAllWindows()

if __name__ == '__main__':
    camdx = CAMERAS(70, -1, 'DX')
    camdx.main(True)
