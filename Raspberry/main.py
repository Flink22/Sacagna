import RPi.GPIO as GPIO
import board
import busio
import math
import time
import sys
import queue as Queue

from os.path import join

def main(camdx_q, camsx_q, vittima):
    
    delay = 1.2
    avanti = 190
    dietro = 100
    impulsi = 2740
    muro = 150

    mappa = 80

    xStart = xNow = xend = 40
    yStart = yNow = yend = 40
    
    ang_attuale = 0
    dire = 1
               


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
    
    led.blink(1)

    if bno.begin() is not True:
        print('Error initializing BNO')
        exit()

    if apds.begin() is not True:
        print('Error initializing APDS')
        exit()

    board = [['0' for i in range(mappa)] for i in range(mappa)]
    check = [['0' for i in range(mappa)] for i in range(mappa)]
    #posizione partenza roboto in matrice
    # xStart = 
    # yStart = 
    # 
    # xNow = 
    # yNow = 
    # 
    # xarrivo = 
    # yarrivo = 
    # variabili test


    #se vuoto valore 0
    #se muro valore !


    board[yStart][xStart] = '1'
    #cambiare in base a quando grande e' la mappa x2
    for i in range(mappa):
        for j in range(mappa):
            if i%2 != 0:
                board[i][j] = '-'
            if j%2 != 0:
                board[i][j] = '-'
            if j%2 != 0 and i%2 != 0:
                board[i][j] = '$'

    GPIO.setup(26,GPIO.OUT)
    GPIO.output(26,GPIO.HIGH)

    robot = board[yNow][xNow]
    
                                                                                                                            
    while True:
        
        if ang_attuale>360:
            ang_attuale -= 360
        
        x=int(math.cos(math.radians(ang_attuale)))
        y=int(math.sin(math.radians(ang_attuale)))
        
         #RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO
            
        if ((laser.read(1) < muro) and (laser.read(2) < muro)): #RADDRIZZO DX
            ang_DX = (math.atan((laser.read(1) - laser.read(2))/175))*180/math.pi
            
            if (ang_DX < -4.0) or (ang_DX > 4.0):
                print('raddrizzo DX', ang_DX)
                bno.begin()
                bno_ANG = bno.readAngleRot()
                if (ang_DX > 0):
                    ser.writeMot(0.3, 0.3, 1, 0)
                    ang_DX = ang_DX - 3
                    while (bno_ANG < ang_DX) or (bno_ANG > 350):
                        bno_ANG = bno.readAngleRot()
                
                else:
                    ang_DX = ang_DX + 363
                    ser.writeMot(0.3, 0.3, 0, 1)
                    while (bno_ANG < 10) or (bno_ANG > ang_DX):
                        bno_ANG = bno.readAngleRot()
            
            ser.writeMot()
        
        elif ((laser.read(3) < muro) and (laser.read(4) < muro)): #RADDRIZZO SX
            ang_SX = (math.atan((laser.read(4) - laser.read(3))/175))*180/math.pi
            
            if (ang_SX < -4.0) or (ang_SX > 4.0):
                print('raddrizzo SX', ang_SX)
                bno.begin()
                bno_ANG = bno.readAngleRot()
                if (ang_SX > 0):
                    ang_SX = ang_SX - 3
                    ser.writeMot(0.3, 0.3, 0, 1)
                    while (bno_ANG < ang_SX) or (bno_ANG > 350):
                        bno_ANG = bno.readAngleRot()
                
                else:
                    ang_SX = ang_SX + 363-3
                    ser.writeMot(0.3, 0.3, 1, 0)
                    while (bno_ANG < 10) or (bno_ANG > ang_SX):
                        bno_ANG = bno.readAngleRot()
            
            ser.writeMot()
        
        #FINE FINE RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO   
        
        GPIO.output(26,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(26,GPIO.HIGH)
        
        
      
        if ((laser.read(1) < muro) and (laser.read(2) < muro)):
            if board[yStart][xStart] != '2':
                print()
                try:
                    camdx_q.put_nowait(True)
                except Queue.Full:
                    None
                time.sleep(0.5)
                try:
                    vit = vittima.get_nowait()
                except Queue.Empty:
                    vit = -1
                    pass
                if vit>=0:
                    led.blink(5)
            board[yNow + y][xNow + x] = '!'
            
        if laser.read(0) < muro:
            board[yNow - x][xNow + y] = '?'
            if board[yStart][xStart] != '2':
                bno.begin()
                bno_ANG = bno.readAngleRot()
                print('Ruoto di 90 gradi a destra')
                ser.writeMot(1.0, 1.0, 1, 0)
                while (bno_ANG < 85) or (bno_ANG > 350):
                    bno_ANG = bno.readAngleRot()
                    #print(bno_ANG)
                ser.writeMot()
                try:
                    camsx_q.put_nowait(True)
                except Queue.Full:
                    None
                time.sleep(0.5)
                try:
                    vit = vittima.get_nowait()
                except Queue.Empty:
                    vit = -1
                    pass
                if vit>=0:
                    led.blink(5)
                
                bno.begin()
                bno_ANG = bno.readAngleRot()
                print('Ruoto di 90 gradi a sinistra')
                ser.writeMot(1.0, 1.0, 0, 1)
                while (bno_ANG > 275) or (bno_ANG < 10):
                    bno_ANG = bno.readAngleRot()
                    #print(bno_ANG)
                ser.writeMot()

        if ((laser.read(3) < muro) and (laser.read(4) < muro)):
            if board[yStart][xStart] != '2':
                print()
                try:
                    camsx_q.put_nowait(True)
                except Queue.Full:
                    None
                time.sleep(0.5)
                try:
                    vit = vittima.get_nowait()
                except Queue.Empty:
                    vit = -1
                    pass
                if vit>=0:
                    led.blink(5)
            board[yNow - y][xNow - x] = '!'


     
        
        board[yStart][xStart] = '1'
        
#         
#         for i in range(mappa):
#             for j in range(mappa):
#                 print(' ',board[i][j], end = '')
#             
#             print()
#             print() 
#         
        
        #SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione
        
        GPIO.output(26,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(26,GPIO.HIGH)
        
        #     scelgo via
    
        if (board[yNow + y][xNow + x] != '!') and (board[yNow + y][xNow + x] != '?') and (board[yNow + (y*2)][xNow + (x*2)] != '4'):
            if (board [yNow + (y*2)][xNow + (x*2)] == '2') and (board[yNow - x][xNow + y] != '!') and (board[yNow - x][xNow + y] != '?') and (board[yNow - (x*2)][xNow + (y*2)] != '4') and (board[yNow - (x*2)][xNow + (y*2)] != '2'):
                yNow -= (x*2)
                xNow += (y*2)
                direzione = 1
                ang_attuale += 0
            elif (board [yNow + (y*2)][xNow + (x*2)] == '2') and (board[yNow - y][xNow - x] != '!') and (board[yNow - y][xNow - x] != '?') and (board[yNow - (y*2)][xNow - (x*2)] != '4') and (board[yNow - (y*2)][xNow - (x*2)] != '2'):
                xNow -= (x*2)
                yNow += (y*2)   
                direzione = 4
                ang_attuale += 270 
            else:
                xNow += (x*2)
                yNow += (y*2)    
                direzione = 2
                ang_attuale += 90
                print(ang_attuale)
        
        elif (board[yNow - x][xNow + y] != '!') and (board[yNow - x][xNow + y] != '?') and (board[yNow - (x*2)][xNow + (y*2)] != '4'):
            if (board[yNow - (x*2)][xNow + (y*2)] == '2') and (board[yNow - y][xNow - x] != '!') and (board[yNow - y][xNow - x] != '?') and (board[yNow - (y*2)][xNow - (x*2)] != '4') and (board[yNow - (y*2)][xNow - (x*2)] != '2'):
                xNow -= (x*2)
                yNow -= (y*2)            
                direzione = 4
                ang_attuale += 270
            else:
                yNow -= (x*2)
                xNow += (y*2)
                direzione = 1
                ang_attuale += 0
        
        elif (board[yNow - y][xNow - x] != '!') and (board[yNow - y][xNow - x] != '?') and (board[yNow - (y*2)][xNow - (x*2)] != '4'):
            xNow -= (x*2)
            yNow -= (y*2)
            direzione = 4
            ang_attuale += 270
        
        else:
            yNow += (x*2)
            xNow -= (y*2)
            direzione = 3
            ang_attuale += 180
    
        
        
        try:
            vit = vittima.get_nowait()
        except Queue.Empty:
            vit = -1
            pass
        
        if vit>=0:
            led.blink(5)
        
        #SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione
        
        #(0.25)
        bno.begin()
        if direzione == 1:
            print('Vado dritto')
        else:
            bno_ANG = bno.readAngleRot()
            if direzione == 2:
                print('Ruoto di 90 gradi a destra')
                ser.writeMot(1.0, 1.0, 1, 0)
                while (bno_ANG < 85) or (bno_ANG > 350):
                    bno_ANG = bno.readAngleRot()
                    #print(bno_ANG)
                ser.writeMot()
                if ((board[yStart - y][xStart - x] == '!') or (board[yStart - y][xStart - x] == '?')):
                    ser.writeMot(1.0, 1.0, 0, 0)
                    time.sleep(0.5)
                    ser.writeMot()
                    ser.writeMot(0.5, 0.5, 1, 1)
                    time.sleep(0.25)
                    ser.writeMot()
                
            elif direzione == 4:
                print('Ruoto di 90 gradi a sinistra')
                ser.writeMot(1.0, 1.0, 0, 1)
                while (bno_ANG > 275) or (bno_ANG < 10):
                    bno_ANG = bno.readAngleRot()
                    #print(bno_ANG)
                ser.writeMot()
                if ((board[yStart + y][xStart + x] == '!') or (board[yStart + y][xStart + x] == '?')):
                    ser.writeMot(1.0, 1.0, 0, 0)
                    time.sleep(0.5)
                    ser.writeMot()
                    ser.writeMot(0.5, 0.5, 1, 1)
                    time.sleep(0.25)
                    ser.writeMot()
               
            elif direzione == 3:
                print('Ruoto di 180 gradi a destra')
                ser.writeMot(0.7, 0.7, 1, 0)
                while (bno_ANG < 173) or (bno_ANG > 190):
                    bno_ANG = bno.readAngleRot()
                    #print(bno_ANG)
                ser.writeMot()
                ser.writeMot(1.0, 1.0, 0, 0)
                time.sleep(0.5)
                ser.writeMot()
                ser.writeMot(0.5, 0.5, 1, 1)
                time.sleep(0.25)
                ser.writeMot()
        time.sleep(0.25)
        
        GPIO.output(26,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(26,GPIO.HIGH)
        
        board[yStart][xStart] = '2'
        
        mv.avanti()
        
        if (apds.readC()<750):
            mv.indietro(5)
            print('Negro')
            
            board[yNow][xNow] = '4'
            yNow = yStart
            xNow = xStart
            if ang_attuale == 0:
                ang_attuale = 180
            elif ang_attuale == 90:
                ang_attuale = 270
            elif ang_attuale == 180:
                ang_attuale = 0
            else:
                ang_attuale = 90
            
            
            bno.begin()
            print('Ruoto di 180 gradi a destra')
            ser.writeMot(0.7, 0.7, 1, 0)
            bno_ANG = bno.readAngleRot()
            while (bno_ANG < 173) or (bno_ANG > 190):
                bno_ANG = bno.readAngleRot()
               # print(bno_ANG)
            ser.writeMot()
            
        elif(apds.readB()<800):
            print('Blu')
            time.sleep(5)
                
            GPIO.output(26,GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(26,GPIO.HIGH)
            
        
    #     if(apds.read grigio):
    #         print("CHECK")
    #         check = board.copy()
            
        Fc_avanti = fc.read()
        if not(Fc_avanti[1]):
            mv.indietro(2)
        
        if yStart != yNow or xStart != xNow :
            
            
            yStart = yNow
            xStart = xNow
    #         board[yNow][xNow] = '1'
        
        print()
        print(ang_attuale)
        
        GPIO.output(26,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(26,GPIO.HIGH)
        
            

    # base bianca=2 /base blu=3 /base nera =4 
