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

# from oldmain import LOGICA
import Main as main
from telecamere import CAMERAS

exposure = 100 # 100

def testDevice(source):
   cap = cv.VideoCapture(source) 
   if cap is None or not cap.isOpened():
       print('Warning: unable to open video source: ', source)

if __name__ == "__main__":
        
    GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    
    _exit = multiprocessing.Event()
#     
#     for i in range (10):
#         testDevice(i)
    
    capsx = cv.VideoCapture(6)
    capdx = cv.VideoCapture(1)
    
    camsx = CAMERAS(exposure, capsx, 'SX')
    camdx = CAMERAS(exposure, capdx, 'DX')
#     lg = LOGICA()
    
    camdx_q = multiprocessing.Queue(1)
    camsx_q = multiprocessing.Queue(1)
    vittima = multiprocessing.Queue(1)
    
#     tel_sx = multiprocessing.Process(target=camsx.main, args=(camsx_q,vittima))
#     tel_dx = multiprocessing.Process(target=camdx.main, args=(camdx_q,vittima))
    
    try:
#         tel_dx.start()
#         tel_sx.start()
        
        while(GPIO.input(22)):
            time.sleep(0.1)
        
        main.main(camdx_q, camsx_q, vittima)
        
        tel_dx.join()
        tel_sx.join()
        
    except KeyboardInterrupt:
        tel_dx.join()
        tel_sx.join()
