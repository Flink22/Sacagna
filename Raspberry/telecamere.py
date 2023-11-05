import cv2 as cv
import imutils
import numpy as np
import time
from lettere import letters
from colori import colors
import queue as Queue
from seriale import SERIALEPICO


class CAMERAS:
    def __init__(self, exposure, cap, nome):
        self.nome = nome
        self.let = letters(self.nome)
        self.col = colors(self.nome)
        
        self.colori = 'Colori ' + self.nome
        self.lettere = 'Lettere ' + self.nome
        self.exposuretime = exposure #va da 78 a 1250
        self.check = True
        
        self.cam = cv.VideoCapture(cap)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, 320)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
        self.cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposuretime)
        
        self.DIM = (320, 240)
        self.K = np.array([[186.633562908702, 0.0, 159.63860971953468], [0.0, 187.26140638525635, 117.48987259205484], [0.0, 0.0, 1.0]])
        self.D = np.array([[-0.20091504350368597], [0.0592029139269305], [-0.08776110683616245], [0.0645164299406898]])
        balance=0.8
        scale_factor = 1.0
        
        self.K_new = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(self.K, self.D, self.DIM, np.eye(3), balance=balance)
        self.map1, self.map2 = cv.fisheye.initUndistortRectifyMap(self.K, self.D, np.eye(3), self.K_new, self.DIM, cv.CV_32FC1)
        
        if not self.cam.isOpened():
            print("Telecamera", self.nome, " Error")
        else:
            print("Telecamera", self.nome, "INIT finito")
    
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
                
                undistorted_frame = cv.remap(frame, self.map1, self.map2, interpolation = cv.INTER_LINEAR, borderMode = cv.BORDER_CONSTANT)
                
                undistorted_frame = undistorted_frame[40:200, 10:320]
                undistorted_frame = cv.resize(undistorted_frame, (320, 240), interpolation = cv.INTER_LINEAR)
                
                blur = cv.GaussianBlur(undistorted_frame, (5, 5), 0)
                
#                 self.check = True
                if self.check:
                    start = time.time()
                    cframe, n_d = self.col.find(blur, undistorted_frame)
                    cv.imshow(self.colori, cframe)
                    if n_d == -1:
                        lframe, n_d = self.let.find(blur, frame)
                        cv.imshow(self.lettere, lframe)
                        
                    if n_d != -1:
                        try:
                            vittima.put_nowait(n_d)
                        except Queue.Full:
                            None
                        temp = time.time() - start
                        ser.askK(n_d, self.nome)
                        print("Telecamera", self.nome, n_d, "KIT in", temp)            
                
                cv.imshow(self.nome, undistorted_frame)
#                 cv.imshow('thresh', thresh)

                self.check = False
            
                
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            self.close()
    
    def close(self):
        self.cam.release()
        cv.closeAllWindows()

if __name__ == '__main__':
    camdx = CAMERAS(70, -1, 'DX')
    camdx.main(True)
