import RPi.GPIO as GPIO
import board
import busio
import math
import time
import sys
from os.path import join

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
    print('Error initializing BNO')
    exit()

if apds.begin() is not True:
    print('Error initializing APDS')
    exit()

board = [['0' for i in range(12)] for i in range(12)]
#posizione partenza roboto in matrice
xStart = 6
yStart = 6

xNow = 6
yNow = 6

xarrivo = 6
yarrivo = 6
# variabili test


#se vuoto valore 0
#se muro valore !


board[yStart][xStart] = '1'
#cambiare in base a quando grande e' la mappa x2
for i in range(12):
    for j in range(12):
        if i%2 != 0:
            board[i][j] = '-'
        if j%2 != 0:
            board[i][j] = '-'
        if j%2 != 0 and i%2 != 0:
            board[i][j] = '$'




robot = board[yNow][xNow]

ang_attuale = 0
dire = 1

while True:
    
     #RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO
        
    if ((laser.read(1) < muro) and (laser.read(2) < muro)): #RADDRIZZO DX
        ang_DX = (math.atan((laser.read(1) - laser.read(2))/175))*180/math.pi
        
        if (ang_DX < -5.0) or (ang_DX > 5.0):
            print('raddrizzo DX', ang_DX)
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
            print('raddrizzo SX', ang_SX)
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
    
    #FINE FINE RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO   
    
    if ang_attuale == 0:
        dire = 1
    if ang_attuale == 90:
        diree = 2
    if ang_attuale == 180:
        dire = 3
    if ang_attuale == 270:
        dire = 4


    if dire == 1:
        if ((laser.read(1) < muro) and (laser.read(2) < muro)):
            if (board[yNow][xNow + 1] != '!'):
                print()
                #check telecamera destra
            board[yNow][xNow + 1] = '!'
            
        elif laser.read(0) > muro:
            board[yNow - 1][xNow] = '?'

        elif ((laser.read(3) > muro) and (laser.read(4) > muro)):
            if (board[yNow][xNow - 1] != '!'):
                print()
                #check telecamera sinistra
            board[yNow][xNow - 1] = '!'


    if dire == 2:
        if ((laser.read(1) < muro) and (laser.read(2) < muro)):
            if (board[yNow + 1][xNow] != '!'):
                print()
                #check telecamera destra
            board[yNow + 1][xNow] = '!'

        elif laser.read(0) > muro:
            board[yNow][xNow + 1] = '?'

        elif ((laser.read(3) > muro) and (laser.read(4) > muro)):
            if (board[yNow - 1][xNow] != '!'):
                print()
                #check telecamera sinistra
            board[yNow - 1][xNow] = '!'


    if dire == 3:
        if ((laser.read(1) < muro) and (laser.read(2) < muro)):
            if (board[yNow][xNow - 1] != '!'):
                print()
                #check telecamera destra
            board[yNow][xNow - 1] = '!'
            
        elif laser.read(0) > muro:
            board[yNow + 1][xNow] = '?'
            
        elif ((laser.read(3) > muro) and (laser.read(4) > muro)):
            if (board[yNow][xNow + 1] != '!'):
                print()
                #check telecamera sinistra
            board[yNow][xNow + 1] = '!'


    if dire == 4:
        if ((laser.read(1) < muro) and (laser.read(2) < muro)):
            if (board[yNow - 1][xNow] != '!'):
                print()
                #check telecamera destra
            board[yNow - 1][xNow] = '!'

        elif laser.read(0) > muro:
            board[yNow][xNow - 1] = '?'

        elif ((laser.read(3) > muro) and (laser.read(4) > muro)):
            if (board[yNow + 1][xNow] != '!'):
                print()
                #check telecamera sinitra
            board[yNow + 1][xNow] = '!'
     
    
    
    #SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione
    
    #     scelgo via
    if dire == 1:
        if (board[yNow][xNow + 1] != '!') and (board[yNow][xNow + 1] != '?') and (board[yNow][xNow + 2] != 4):
            xNow += 2
            direzione = 2
            ang_attuale += 90
        elif (board[yNow - 1][xNow] != '!') and (board[yNow - 1][xNow] != '?') and (board[yNow - 2][xNow] != 4):
            yNow -= 2
            direzione = 1
        elif (board[yNow][xNow - 1] != '!') and (board[yNow][xNow - 1] != '?') and (board[yNow][xNow - 2] != 4):
            xNow -= 2
            direzione = 4
            ang_attuale += 270
        else:
            direzione = 3
            ang_attuale += 180
    if dire == 2:
        if (board[yNow + 1][xNow] != '!') and (board[yNow + 1][xNow] != '?') and (board[yNow +2][xNow] != 4):
            yNow -= 2
            direzione = 2
            ang_attuale += 90
        elif (board[yNow ][xNow + 1] != '!') and (board[yNow ][xNow + 1] != '?') and (board[yNow][xNow + 2] != 4):
            xNow += 2
            direzione = 1
        elif (board[yNow][xNow - 1] != '!') and (board[yNow][xNow - 1] != '?') and (board[yNow][xNow - 2] != 4):
            xNow -= 2
            direzione = 4
            ang_attuale += 270
        else:
            direzione = 3
            ang_attuale += 180
    if dire == 3:
        if (board[yNow][xNow - 1] != '!') and (board[yNow][xNow - 1] != '?') and (board[yNow -2][xNow - 2] != 4):
            xNow -= 2
            direzione = 2
            ang_attuale += 90
        elif (board[yNow + 1][xNow] != '!') and (board[yNow + 1][xNow] != '?') and (board[yNow + 2][xNow] != 4):
            yNow += 2
            direzione = 1
        elif (board[yNow][xNow + 1] != '!') and (board[yNow][xNow + 1] != '?') and (board[yNow][xNow + 2] != 4):
            xNow += 2
            direzione = 4
            ang_attuale += 270
        else:
            direzione = 3
            ang_attuale += 180
            
    if dire == 4:
        if (board[yNow - 1][xNow] != '!') and (board[yNow - 1][xNow] != '?') and (board[yNow -2][xNow] != 4):
            yNow -= 2
            direzione = 2
            ang_attuale += 90
        elif (board[yNow][xNow - 1] != '!') and (board[yNow][xNow - 1] != '?') and (board[yNow ][xNow - 2] != 4):
            xNow -= 2
            direzione = 1
        elif (board[yNow + 1][xNow] != '!') and (board[yNow + 1][xNow] != '?') and (board[yNow + 2][xNow] != 4):
            yNow += 2
            direzione = 4
            ang_attuale += 270
        else:
            direzione = 3
            ang_attuale += 180
    
    if ang_attuale >= 360:
        ang_attuale -= 360
    elif ang_attuale < 0:
        ang_attuale += 360
    
    #SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione
    
    time.sleep(0.25)
    bno.begin()
    if direzione == 1:
        print('Vado dritto')
    else:
        bno_ANG = bno.readAngleRot()
        if direzione == 2:
            print('Ruoto di 90 gradi a destra')
            ser.writeMot(0.7, 0.7, 1, 0)
            while (bno_ANG < 85) or (bno_ANG > 350):
                bno_ANG = bno.readAngleRot()
                print(bno_ANG)
            ser.writeMot()
            
        elif direzione == 4:
            print('Ruoto di 90 gradi a sinistra')
            ser.writeMot(0.7, 0.7, 0, 1)
            while (bno_ANG > 275) or (bno_ANG < 10):
                bno_ANG = bno.readAngleRot()
                print(bno_ANG)
            ser.writeMot()
    
        elif direzione == 3:
            print('Ruoto di 180 gradi a destra')
            ser.writeMot(0.7, 0.7, 1, 0)
            while (bno_ANG < 173) or (bno_ANG > 190):
                bno_ANG = bno.readAngleRot()
                print(bno_ANG)
            ser.writeMot()
    time.sleep(0.25)
    
    mv.avanti()
    
    if (apds.readC()<50):
        print('Negro')
        mv.indietro(7)
        board[yNow][xNow] = '4'
        yNow = yStart
        xNow = xStart
        ang_attuale += 180
        
        bno.begin()
        print('Ruoto di 180 gradi a destra')
        ser.writeMot(0.7, 0.7, 1, 0)
        bno_ANG = bno.readAngleRot()
        while (bno_ANG < 173) or (bno_ANG > 190):
            bno_ANG = bno.readAngleRot()
            print(bno_ANG)
        ser.writeMot()
        
    elif(apds.readB()<10):
        print('Blu')
        
    Fc_avanti = fc.read()
    if not(Fc_avanti[1]):
        mv.indietro(5)
    
    if yStart != yNow or xStart != xNow :
        
        yStart = yNow
        xStart = xNow
        board[yNow][xNow] = '1'
    for i in range(12):
        for j in range(12):
            print(' ',board[i][j], end = '')
        
        print()
        print()
        

# base bianca=2 /base blu=3 /base nera =4 


    time.sleep(3)
