import cv2 as cv
import subprocess
import numpy as np

class TELECAMERE:
  
  exposuretime = 100 #va da 0 a 255
  
  low_b = (0, 0, 0)
  high_b = (20, 20, 20)
  
  low_r = (0, 160, 120)
  high_r = (15, 255, 255)
  
  low_g = (40, 90, 35)
  high_g = (100, 240, 200)
  
  low_y = (40, 90, 35)
  high_y = (100, 240, 200)
  
  dx = 0
  sx = 1
  
  def __init__(self):
    camdx = cv.VideoCapture(dx)
    camdx.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    camdx.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    camdx.set(cv.CAP_PROP_EXPOSURE, exposuretime)
    
    camsx = cv.VideoCapture(sx)
    camsx.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    camsx.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    camsx.set(cv.CAP_PROP_EXPOSURE, exposuretime)

  def main(self):
    try:
			cam_attuale = 0
      while(self.attivo):
        if cam_attuale == 0:
					frame = camdx.read()
					cam_attuale = 1
				else:
					frame = camsx.read()
					cam_attuale = 0
				
				cut = frame[110:610, 280:1000]
				resize = cv.resize(cut, (320, 240), interpolation= cv.INTER_LINEAR)
				blur = cv.GaussianBlur(resize,(5,5),0)
				ret,thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 19)
				
				nkit = 0
				nkit = self.ricColori(thresh)
				if nkit == -1:
					self.ricLettere(thresh)

	def ricLettere(self, input):
		contours hierarchy = cv.findContours(input, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    if len(contours) != 0:
        cnt = max(contours, key=cv.contourArea)
                
        hull = cv.convexHull(cnt)
        hull = cv.convexHull(cnt, returnPoints = False)
        defects = cv.convexityDefects(cnt, hull)
        
        defects_n = 0

        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = tuple(cnt_dx[s][0])
            end = tuple(cnt_dx[e][0])
            far = tuple(cnt_dx[f][0])
            dist = start[0] - end[0]
            if dist<0 :
                dist *= -1
            if dist>30 :
                defects_n += 1
