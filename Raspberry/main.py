import RPi.GPIO as gpio
import board
import busio
import math
import time

from laser import VL6180
from giroscopio import BNO055
from led import LED
from telecamere import cameras
from lettere import letters
from seriale import SerialeATmega

laser = VL6180()
bno = BNO055()
led = LED()
cam = cameras()
let = letters()
ser = SerialeATmega()

laser_MM = [0, 0, 0, 0, 0]
muro = 120
ang_attuale = 0

if bno.begin() is not True:
    print("Error initializing device")
    exit()

while True:
#     cam.read()
    laser_MM = laser.read(2)
    
    if (((laser_MM[1] > muro) and (laser_MM[2] < muro)) or ((laser_MM[3] < muro) and (laser_MM[4] > muro))):
        
        ser.write(11)
        time.sleep(0.1)
        while((laser_MM[1] > muro) or (laser_MM[4] > muro)):
            
            laser.read()
            print("trovo buco")
        print("so fora")
        ser.write(15)
        data = 0
        while(data < 205):
            ser.clean()
            time.sleep(0.25)
#         if ser.read() != None:
            data = ser.read()
            print(data)
        ser.write(10)
        
    elif (((laser_MM[1] < muro) and (laser_MM[2] > muro)) or ((laser_MM[3] < muro) and (laser_MM[4] < muro))):
        
        ser.write(11)
        time.sleep(0.1)
        while((laser_MM[2] > muro) or (laser_MM[3] > muro) ):
            
            laser.read()
            print("passo buco")
        ser.write(11)
        data = 0
        while(data < 205):
            ser.clean()
            time.sleep(0.25)
#         if ser.read() != None:
            data = ser.read()
            print(data)
        ser.write(10)
    
    if ((laser_MM[1] < muro) and (laser_MM[2] < muro)):
        ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/175))*180/math.pi
        
        while (ang_DX > 3.0):
            print("Raddrizzo")
            laser_MM = laser.read()
            ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/175))*180/math.pi
#             gira
        
        while (ang_DX < -3.0):
            print("Raddrizzo")
            laser_MM = laser.read()
            ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/175))*180/math.pi
#             gira
        
    elif ((laser_MM[3] < muro) and (laser_MM[4] < muro)):
        ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/175))*180/math.pi
        
        while (ang_SX > 3.0):
            print("Raddrizzo")
            laser_MM = laser.read()
            ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/175))*180/math.pi
#             gira
        
        while (ang_SX < -3.0):
            print("Raddrizzo")
            laser_MM = laser.read()
            ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/175))*180/math.pi
#             gira
    
    if ((laser_MM[1] > muro) and (laser_MM[2] > muro)):
        direzione = 2
        ang_attuale += 90
    elif laser_MM[0] > muro:
        direzione = 1
        ang_attuale += 0
    elif ((laser_MM[3] > muro) and (laser_MM[4] > muro)):
        direzione = 4
        ang_attuale += 270
    else:
        direzione = 3
        ang_attuale += 180
    
    if ang_attuale > 360:
        ang_attuale -= 360
    elif ang_attuale < 0:
        ang_attuale += 360
        
    ser.write(10)
    
    bno.begin()
    if direzione == 1:
        print("Vado dritto")
        bno_ANG = bno.readAngle()
        time.sleep(0.5)
    else:
        bno_ANG = bno.readAngle()
        if direzione == 2:
            print("Ruoto di 90 gradi a destra")
            while (bno_ANG < 85) or (bno_ANG > 350):
                try:
                    bno_ANG = bno.readAngle()
                except:
                    print("eeror")
                time.sleep(0.25)
                print(bno_ANG)
                ser.write(12)
            
        elif direzione == 4:
            print("Ruoto di 90 gradi a sinistra")
            while (bno_ANG > 275) or (bno_ANG < 10):
                try:
                    bno_ANG = bno.readAngle()
                except:
                    print("eeror")
                print(bno_ANG)
                time.sleep(0.25)
                ser.write(14)
    
        elif direzione == 3:
            print("Ruoto di 180 gradi a destra")
            while (bno_ANG < 175) or (bno_ANG > 350):
                try:
                    bno_ANG = bno.readAngle()
                except:
                    print("eeror")
                print(bno_ANG)
                time.sleep(0.25)
                ser.write(12)
        
    ser.write(11)
    time.sleep(0.1)
    data = 0
    while(data < 1370):
        ser.clean()
        time.sleep(0.25)
#         if ser.read() != None:
        data = ser.read()
        print(data)
    ser.write(10)
    
    time.sleep(1)
