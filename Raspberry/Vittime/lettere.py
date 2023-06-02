import cv2 as cv
import numpy as np

class letters:
    def __init__(self, nome):
        self.nome = nome
        self.low_b = 0
        self.high_b = 20
        self.def_N = 0
    
    def find(self, blur, frame):
        
        gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
        thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 29, 23)
        mask = cv.inRange(thresh, self.low_b, self.high_b)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # trova i contorni
        self.def_N = -1
        if len(contours) != 0:  
            cnt = max(contours, key=cv.contourArea)
            if cv.contourArea(cnt) > 1200:
                hull = cv.convexHull(cnt, returnPoints = False)
                try:
                    defects = cv.convexityDefects(cnt, hull)
                    count = 0
                    if defects is not None:
                        
                        for i in range(defects.shape[0]):
                            s,e,f,d = defects[i,0]
                            start = tuple(cnt[s][0])
                            end = tuple(cnt[e][0])
                            far = tuple(cnt[f][0])
                            dist = start[0] - end[0]
                            
                            if abs(dist>30):
                                count += 1
                                cv.line(frame,start,end,[0,255,0],2)
                                cv.circle(frame,far,5,[0,0,255],-1)
                    
                        if count == 0:
                            print("Telecamera", self.nome, "S")
                            self.def_N = 1
                        elif count == 1:
                            print("Telecamera", self.nome, "U")
                            self.def_N = 0
                        elif count == 2:
                            print("Telecamera", self.nome, "H")
                            self.def_N = 3
                        else:
                            print("Telecamera", self.nome, "NO LETTER")
#                         cv.drawContours(frame, [hull], -1, (255, 255, 0), 2)
                except:
                    print("errore concavità")
        else:
            print("NO LETTER")
        return mask, self.def_N
