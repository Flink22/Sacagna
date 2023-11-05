import multiprocessing
# from multiprocessing import *
import threading
import queue as Queue

import shutil
import os
import sys
import RPi.GPIO as GPIO
import time
import cv2 as cv
from colore import APDS9960


exposure = 20 # 100

def testDevice(source):
   cap = cv.VideoCapture(source) 
   if cap is None or not cap.isOpened():
       print('Warning: unable to open video source: ', source)

if __name__ == "__main__":
    
    import Main as main
    from telecamere import CAMERAS
    
#     for i in range (8):
#         testDevice(i)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    
    _exit = multiprocessing.Event()

    capsx = 4
    capdx = 0
    
    camsx = CAMERAS(exposure, capsx, 'SX')
    camdx = CAMERAS(exposure, capdx, 'DX')
    
    camdx_q = multiprocessing.Queue(1)
    camsx_q = multiprocessing.Queue(1)
    vittima = multiprocessing.Queue(1)
    
    tel_sx = multiprocessing.Process(target=camsx.main, args=(camsx_q,vittima))
    tel_dx = multiprocessing.Process(target=camdx.main, args=(camdx_q,vittima))
    
    apds = APDS9960()
    
    try:
        tel_dx.start()
        tel_sx.start()
        
        apds.begin()
        while(GPIO.input(22)):
            print(apds.read())
            time.sleep(0.05)
        
        out = main.main(camdx_q, camsx_q, vittima)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        
        while(GPIO.input(22)):
            time.sleep(0.05)
        
        out = main.main(camdx_q, camsx_q, vittima)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        
        while(GPIO.input(22)):
            time.sleep(0.05)
        
        out = main.main(camdx_q, camsx_q, vittima)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        
        while(GPIO.input(22)):
            time.sleep(0.05)
        
        out = main.main(camdx_q, camsx_q, vittima)
        
        tel_dx.join()
        tel_sx.join()
        print("FINE")
        
    except KeyboardInterrupt:
        print("FINE")
        tel_dx.close()
        tel_sx.close()
        tel_dx.join()
        tel_sx.join()
