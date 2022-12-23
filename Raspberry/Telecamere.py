import cv2 as cv
import subprocess
import numpy as np

errcount = 0
exposuretime = 150 #va da 78 a 1250
low_b = np.array([0, 0, 0])
high_b = np.array([20, 20, 20])

camdx = cv.VideoCapture(0)
camdx.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
camdx.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
command = "v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=" + str(exposuretime)
output = subprocess.call(command, shell=True)

if not camdx.isOpened():
    print("Telecamera DX Error")
    errcount += 1
    exit()

if errcount == 0:
    for i in range (0, 3):
        ret, frame_dx = camdx.read()
    
    frame_dx = frame_dx[110:610, 280:1000]
    frame_dx = cv.resize(frame_dx, (320, 240), interpolation= cv.INTER_LINEAR)
    
    blur_dx = cv.GaussianBlur(frame_dx,(5,5),0)
    ret,thresh_dx = cv.threshold(blur_dx,100,255,cv.THRESH_BINARY)
    mask_dx = cv.inRange(thresh_dx, low_b, high_b)
    
    contours_dx, hierarchy = cv.findContours(mask_dx, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    if len(contours_dx) != 0:
        cnt_dx = max(contours_dx, key=cv.contourArea)
                
        hull = cv.convexHull(cnt_dx)
        hull_dx = cv.convexHull(cnt_dx, returnPoints = False)
        defects = cv.convexityDefects(cnt_dx, hull_dx)
        
        p=0

        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = tuple(cnt_dx[s][0])
            end = tuple(cnt_dx[e][0])
            far = tuple(cnt_dx[f][0])
            dist = start[0] - end[0]
            if dist<0 :
                dist *= -1
            if dist>30 :
                p += 1
            cv.line(frame_dx,start,end,[0,255,0],2)
            cv.circle(frame_dx,far,5,[0,0,255],-1)
        
        print(p)
        
        
        cv.drawContours(frame_dx, [cnt_dx], 0, (255,0,0), 2)
        cv.drawContours(frame_dx, [hull], -1, (255, 255, 0), 2)

        cv.imshow('image', frame_dx)
        cv.imshow('thresh', thresh_dx)
        cv.imshow('mask', mask_dx)

if cv.waitKey(0) == ord('q'): # premere q per uscire
    camdx.release()
    cv.destroyAllWindows()