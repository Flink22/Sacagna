import RPi.GPIO as GPIO
import board
import busio
import math
import time

delay = 1.2
avanti = 190
dietro = 100
impulsi = 2740
muro = 170


from laser import VL6180
from giroscopio import BNO055
from colore import APDS9960
from led import LED
from seriale import SERIALEPICO
from finecorsa import FINECORSA
from movimenti import MOVIMENTI

ser = SERIALEPICO()
ser.writeMot()

bno = BNO055()
laser = VL6180()
apds = APDS9960()
led = LED()
fc = FINECORSA()

mv = MOVIMENTI()

ang_attuale = 0
led.blink(1)

if bno.begin() is not True:
    print("Error initializing BNO")
    exit()

if apds.begin() is not True:
    print("Error initializing APDS")
    exit()

while True:
    
    if (((laser.read(1) > muro) and (laser.read(2) < muro)) or ((laser.read(3) < muro) and (laser.read(4) > muro))):# laser davanti vuoto dietro muro 
        
        ser.writeMot(1.0, 1.0, 1, 1)
        Fc_avanti = fc.read()
        
        while(((laser.read(1) > muro) or (laser.read(4) > muro))and(Fc_avanti[1])): #vadovanti finche non meschianto o trovo buco
            
            Fc_avanti = fc.read()
            print("trovo buco")
            
        ser.writeMot()
        print("so fora")
        
        print("torno indrio1")
        mv.indietro()
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
        
#     elif (((laser_MM[1] < muro) and (laser_MM[2] > muro)) or ((laser_MM[3] < muro) and (laser_MM[4] < muro))):
#         
#         ser.write(11)
# #         time.sleep(0.1)
#         Fc_avanti = fc.read()
#         while(((laser_MM[2] > muro) or (laser_MM[3] > muro))and(Fc_avanti[1])): 
#             Fc_avanti = fc.read()
#             laser.read()
#             print("passo buco")
#             ser.write(11)
#             data = 0
#              
#             while((data < avanti)and(Fc_avanti[1])):#(not)
#                 Fc_avanti = fc.read()
#                 laser.read()
#                 data = ser.read()
#                 print("passo buco")
#                 
#         ser.write(10)
#         time.sleep(0.7)

    Fc_avanti = fc.read()
    if not(Fc_avanti[1]):
        print("torno indrio3")
        mv.indietro()
        
    
    #RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO
        
    if ((laser.read(1) < muro) and (laser.read(2) < muro)): #RADDRIZZO DX
        ang_DX = (math.atan((laser.read(1) - laser.read(2))/175))*180/math.pi
        
        if (ang_DX < -5.0) or (ang_DX > 5.0):
            print("raddrizzo DX", ang_DX)
            bno.begin()
            bno_ANG = bno.readAngleRot()
            if (ang_DX > 0):
                ser.writeMot(0.3, 0.3, 1, 0)
                ang_DX = ang_DX - 2
                while (bno_ANG < ang_DX) or (bno_ANG > 350):
                    bno_ANG = bno.readAngleRot()
            
            else:
                ang_DX = ang_DX + 362
                ser.writeMot(0.3, 0.3, 0, 1)
                while (bno_ANG < 10) or (bno_ANG > ang_DX):
                    bno_ANG = bno.readAngleRot()
        
        ser.writeMot()
    
    elif ((laser.read(3) < muro) and (laser.read(4) < muro)): #RADDRIZZO SX
        ang_SX = (math.atan((laser.read(4) - laser.read(3))/175))*180/math.pi
        
        if (ang_SX < -5.0) or (ang_SX > 5.0):
            print("raddrizzo SX", ang_SX)
            bno.begin()
            bno_ANG = bno.readAngleRot()
            if (ang_SX > 0):
                ang_DX = ang_DX - 2
                ser.writeMot(0.7, 0.7, 0, 1)
                while (bno_ANG < ang_SX) or (bno_ANG > 350):
                    bno_ANG = bno.readAngleRot()
            
            else:
                ang_SX = ang_SX + 362
                ser.writeMot(0.7, 0.7, 1, 0)
                while (bno_ANG < 10) or (bno_ANG > ang_SX):
                    bno_ANG = bno.readAngleRot()
        
        ser.writeMot()
    
    #RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO   
    
    
    #SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE
    if ((laser.read(1) > muro) and (laser.read(2) > muro)):
        direzione = 2
        ang_attuale += 90
    elif laser.read(0) > muro:
        direzione = 1
        ang_attuale += 0
    elif ((laser.read(3) > muro) and (laser.read(4) > muro)):
        direzione = 4
        ang_attuale += 270
    else:
        direzione = 3
        ang_attuale += 180
    
    if ang_attuale >= 360:
        ang_attuale -= 360
    elif ang_attuale < 0:
        ang_attuale += 360
    
    #SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE#SCELGO DIREZIONE
    
    time.sleep(0.25)
    bno.begin()
    if direzione == 1:
        print("Vado dritto")
    else:
        bno_ANG = bno.readAngleRot()
        if direzione == 2:
            print("Ruoto di 90 gradi a destra")
            ser.writeMot(0.7, 0.7, 1, 0)
            while (bno_ANG < 85) or (bno_ANG > 350):
                bno_ANG = bno.readAngleRot()
                print(bno_ANG)
            ser.writeMot()
            
        elif direzione == 4:
            print("Ruoto di 90 gradi a sinistra")
            ser.writeMot(0.7, 0.7, 0, 1)
            while (bno_ANG > 275) or (bno_ANG < 10):
                bno_ANG = bno.readAngleRot()
                print(bno_ANG)
            ser.writeMot()
    
        elif direzione == 3:
            print("Ruoto di 180 gradi a destra")
            ser.writeMot(0.7, 0.7, 1, 0)
            while (bno_ANG < 173) or (bno_ANG > 190):
                bno_ANG = bno.readAngleRot()
                print(bno_ANG)
            ser.writeMot()
    time.sleep(0.25)
    
    mv.avanti()
    
    if (apds.readC()<50):
        print("Negro")
        mv.indietro(7)
        yNow = yStart
        xNow = xStart
        ang_attuale += 180
        
        bno.begin()
        print("Ruoto di 180 gradi a destra")
        ser.writeMot(0.7, 0.7, 1, 0)
        bno_ANG = bno.readAngleRot()
        while (bno_ANG < 173) or (bno_ANG > 190):
            bno_ANG = bno.readAngleRot()
            print(bno_ANG)
        ser.writeMot()
        
    elif(apds.readB()<10):
        print("Blu")
    
    if not(Fc_avanti[1]):
        mv.indietro(5)   

    time.sleep(3)
