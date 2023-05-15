import cv2 as cv
import numpy as np

class letters:
    def __init__(self):
        self.low_b = np.array([0, 0, 0])
        self.high_b = np.array([20, 20, 20])
        self.def_N = 0
    
    def find(self, blur, frame):
        
        gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
        thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 29, 11)
        mask = cv.inRange(thresh, 0, 20)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        self.def_N = -1
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > 800:
                hull = cv.convexHull(cnt, returnPoints = False)
                try:
                    defects = cv.convexityDefects(cnt, hull)
                    countx = 0
                    county = 0
                    if defects is not None:
                        for i in range(defects.shape[0]):
                            s,e,f,d = defects[i,0]
                            start = tuple(cnt[s][0])
                            end = tuple(cnt[e][0])
                            
                            dx = abs(start[0] - end[0])
                            dy = abs(start[1] - end[1])
                            
                            if dx > 25:
                                countx += 1
                            if dy > 50:
                                county += 1
                                
                        if countx == 0:
                            print("S")
                            self.def_N = 1
                        elif countx == 1:
                            print("U")
                            self.def_N = 0
                        elif countx == 2:
                            print("H")
                            self.def_N = 3
                        else:
                            print("NO LETTER")
                except:
                    print("errore concavità")
            else:
                print("NO LETTER")
        else:
            print("NO LETTER")
        return mask, self.def_N
