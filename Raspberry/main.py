import RPi.GPIO as GPIO
import board
import busio
import math
import time
from adafruit_apds9960.apds9960 import APDS9960
from adafruit_apds9960 import colorutility
i2c = board.I2C()

delay = 1.2
avanti = 190
dietro = 100
impulsi =1250
muro = 130
apds = APDS9960(i2c)
apds.enable_color = True


from laser import VL6180
from giroscopio import BNO055
# from led import LED
# from telecamere import cameras
# from lettere import letters
from seriale import SerialeATmega

laser = VL6180()
bno = BNO055()
# led = LED() dvcsxa
# cam = cameras()
# let = letters()
ser = SerialeATmega()

laser_MM = [0, 0, 0, 0, 0]

ang_attuale = 0
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if bno.begin() is not True:
    print("Error initializing device")
    exit()

while True:
#     cam.read()
    laser_MM = laser.read(2)
    if (((laser_MM[1] > muro) and (laser_MM[2] < muro)) or ((laser_MM[3] < muro) and (laser_MM[4] > muro))):# laser davanti vuoto dietro muro 
        
        ser.write(11)
        
        while(((laser_MM[1] > muro) or (laser_MM[4] > muro))and((GPIO.input(12)))): #vadovanti finche non meschianto o trovo buco
            
            laser.read()
            print("trovo buco")
        print("so fora")
        ser.write(15)
        data = 0
        #time.sleep(0.25)
        while(data < dietro):
            print("torno indrio1")
            ser.clean()
            #time.sleep(0.25)
#         if ser.read() != None:
            data = ser.read()
            print(data)
        ser.write(10)
#         laser_MM = laser.read(2)
#         if(laser_MM[1] < muro):
#             ser.write(14)
#         elif(laser_MM[4] < muro):
#             ser.write(12)
#         else:
#             ser.write(12)
#             time.sleep(delay)
# 
#         time.sleep(delay)
#         
#         ser.write(10)
        
    elif (((laser_MM[1] < muro) and (laser_MM[2] > muro)) or ((laser_MM[3] < muro) and (laser_MM[4] < muro))):
        
        ser.write(11)
#         time.sleep(0.1)
        while(((laser_MM[2] > muro) or (laser_MM[3] > muro))and(GPIO.input(12))):
            
            laser.read()
            print("passo buco")
        ser.write(11)
        data = 0
             
        while((data < avanti)and(GPIO.input(12))):
            laser.read()
            print("passo buco")
            
        ser.write(10)
    
    if (GPIO.input(12)):
        ser.write(15)
        while(data < dietro):
            print("torno indrio3")
            ser.clean()
            #time.sleep(0.25)
#         if ser.read() != None:
            data = ser.read()
            print(data)
        ser.write(10)
        
    
#     if ((laser_MM[1] < muro) and (laser_MM[2] < muro)):
#         ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/175))*180/math.pi
#         
#         while (ang_DX > 3.0):
#             print("Raddrizzo")
#             laser_MM = laser.read()
#             ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/175))*180/math.pi
# #             gira
#         
#         while (ang_DX < -3.0):
#             print("Raddrizzo")
#             laser_MM = laser.read()
#             ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/175))*180/math.pi
# #             gira
#         
#     elif ((laser_MM[3] < muro) and (laser_MM[4] < muro)):
#         ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/175))*180/math.pi
#         
#         while (ang_SX > 3.0):
#             print("Raddrizzo")
#             laser_MM = laser.read()
#             ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/175))*180/math.pi
# #             gira
#         
#         while (ang_SX < -3.0):
#             print("Raddrizzo")
#             laser_MM = laser.read()
#             ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/175))*180/math.pi
# #             gira
    
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
            ser.write(12)
#             time.sleep(delay)
#             ser.write(10)
            while (bno_ANG < 85) or (bno_ANG > 350):
                try:
                    bno_ANG = bno.readAngle()
                except:
                    print("eeror")
                print(bno_ANG)
#                 time.sleep(0.01)
            ser.write(10)
            
        elif direzione == 4:
            print("Ruoto di 90 gradi a sinistra")
            ser.write(14)
#             time.sleep(delay)
#             ser.write(10)
            while (bno_ANG > 275) or (bno_ANG < 10):
                try:
                    bno_ANG = bno.readAngle()
                except:
                    print("eeror")
                print(bno_ANG)
#                 time.sleep(0.25)
            ser.write(10)
    
        elif direzione == 3:
            print("Ruoto di 180 gradi a destra")
            ser.write(12)
#             time.sleep(delay*2 - 0.3)
#             ser.write(10)
            while (bno_ANG < 170) or (bno_ANG > 190):
              
                bno_ANG = bno.readAngle()
                print(bno_ANG)
                
#                 ser.write(12)
    ser.write(10)
    time.sleep(0.5)
    ser.write(11)
#     time.sleep(0.1)
    data = 0
#     time.sleep(0.25)
    while((data < impulsi)and(not(GPIO.input(12)))):
        ser.clean()
        print("vado avanti")
        data = ser.read()
        print(data)
        r, g, b, c = apds.color_data
        if (colorutility.calculate_lux(r, g, b))<25:
            print("nero")
            time.sleep(0.8)
            print("Ruoto di 180 gradi a destra")
            ser.write(12)
#             time.sleep(delay*2 - 0.3)
#             ser.write(10)
            while (bno_ANG < 170) or (bno_ANG > 190):
              
                bno_ANG = bno.readAngle()
                print(bno_ANG)
            ser.write(11)
            time.sleep(0.5)
            break
        
#         if (not(GPIO.input(12))):
#                 ser.clean()
#                 time.sleep(0.25)
#     #         if ser.read() != None:
#                 data = ser.read()
#                 print(data)
#         else:
#             print("torno indrio3")
#             ser.write(15)
#             data = 0
#             time.sleep(0.05)
#             while(data < dietro):
#                 ser.clean()
#                 time.sleep(0.25)
#     #         if ser.read() != None:
#                 data = ser.read()
#                 print(data)
#             break
#         if ser.read() != None:
        
    ser.write(10)
    if (not(GPIO.input(12))):
        ser.write(15)
        while(data < dietro):
            print("torno indrio4")
            ser.clean()
            #time.sleep(0.25)
#         if ser.read() != None:
            data = ser.read()
            print(data)
        ser.write(10)
    
    time.sleep(3)
