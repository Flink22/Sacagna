import RPi.GPIO as GPIO
import board
import busio
import math
import time
import sys
import queue as Queue

from os.path import join

class casella:
    def __init__(self):
        self.padre=0
        self.distanza=10000 

def main(camdx_q, camsx_q, vittima):
    
    GPIO.setmode(GPIO.BCM)
    button_pin = 17
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    global running
    running = True

    def button_callback(channel):
        global running
        if running==True:
            print("Programma interrotto.")
            running = False
        else:
            print("Programma ripreso.")
            running = True
    GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=200)
        
    
    muro = 150

    
    mappa=12

    xStart = xNow = xend = 6
    yStart = yNow = yend = 6
    
#     xStart = xNow = xend = 40
#     yStart = yNow = yend = 40
#     mappa = 80
    
    ang_attuale = 0
    dire = 1
    calli=0
    ritorno = 0
    
    nero = 500
    blu = 500


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
    
#     board[7][8]='a'
#     board[8][7]='b'
    
                                                                                                                            
    while True:
        
        if running:
        
            ang_attuale = ang_attuale % 360
            
            x=int(math.cos(math.radians(ang_attuale)))
            y=int(math.sin(math.radians(ang_attuale)))
            
             #RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO
                
            if ((laser.read(1) < muro) and (laser.read(2) < muro)): #RADDRIZZO DX
                ang_DX = (math.atan((laser.read(1) - laser.read(2))/175))*180/math.pi
                
                if (ang_DX < -8.0) or (ang_DX > 8.0):
                    print('raddrizzo DX', ang_DX)
                    bno.begin()
                    bno_ANG = bno.readAngleRot()
                    if (ang_DX > 0):
                        ser.writeMot(0.3, 0.3, 1, 2)
                        ang_DX = ang_DX - 3
                        while (bno_ANG < ang_DX) or (bno_ANG > 350):
                            bno_ANG = bno.readAngleRot()
                    
                    else:
                        ang_DX = ang_DX + 363
                        ser.writeMot(0.3, 0.3, 2, 1)
                        while (bno_ANG < 10) or (bno_ANG > ang_DX):
                            bno_ANG = bno.readAngleRot()
                
                ser.writeMot()
            
            elif ((laser.read(3) < muro) and (laser.read(4) < muro)): #RADDRIZZO SX
                ang_SX = (math.atan((laser.read(4) - laser.read(3))/175))*180/math.pi
                
                if (ang_SX < -8.0) or (ang_SX > 8.0):
                    print('raddrizzo SX', ang_SX)
                    bno.begin()
                    bno_ANG = bno.readAngleRot()
                    if (ang_SX > 0):
                        ang_SX = ang_SX - 3
                        ser.writeMot(0.3, 0.3, 2, 1)
                        while (bno_ANG < ang_SX) or (bno_ANG > 350):
                            bno_ANG = bno.readAngleRot()
                    
                    else:
                        ang_SX = ang_SX + 363
                        ser.writeMot(0.3, 0.3, 1, 2)
                        while (bno_ANG < 10) or (bno_ANG > ang_SX):
                            bno_ANG = bno.readAngleRot()
                
                ser.writeMot()
            
            #FINE FINE RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO#RADDRIZZO   
            
            check_avanti = 0
            
            if ((laser.read(1) < muro) and (laser.read(2) < muro)):
                if board[yStart][xStart] != '2':
                    print()
                    try:
                        camdx_q.put_nowait(True)
                    except Queue.Full:
                        None
                board[yNow + y][xNow + x] = '!'

            if ((laser.read(3) < muro) and (laser.read(4) < muro)):
                if board[yStart][xStart] != '2':
                    print()
                    try:
                        camsx_q.put_nowait(True)
                    except Queue.Full:
                        None
                board[yNow - y][xNow - x] = '!'
            
            if laser.read(0) < muro:
                board[yNow - x][xNow + y] = '?'
                if board[yStart][xStart] != '2':
                    check_avanti = 1
            
            time.sleep(0.25)
            try:
                vit = vittima.get_nowait()
            except Queue.Empty:
                vit = -1
                pass
            if vit>=0:
                led.blink(5)
           
# mappa   ## mappa  # mappa   mappa  # mappa  # mappa   ## mappa  # mappa   mappa  # mappa # mappa   ## mappa  # mappa   mappa  # mappa # mappa   ## mappa  # mappa   mappa  # mappa          
#             board[yStart][xStart] = '1'
#             print('angolo')
#             print(ang_attuale) 
#             for i in range(mappa):
#                 for j in range(mappa):
#                     print(' ',board[i][j], end = '')
#                  
#                 print()
#                 print() 
#     #         
            
            #SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione
            
            
            #     scelgo via
        
            if (board[yNow + y][xNow + x] != '!') and (board[yNow + y][xNow + x] != '?') and (board[yNow + (y*2)][xNow + (x*2)] != '4'):
                if (board [yNow + (y*2)][xNow + (x*2)] == '2') and (board[yNow - x][xNow + y] != '!') and (board[yNow - x][xNow + y] != '?') and (board[yNow - (x*2)][xNow + (y*2)] != '4') and (board[yNow - (x*2)][xNow + (y*2)] != '2'):
                    yNow -= (x*2)
                    xNow += (y*2)
                    direzione = 1
                    ang_attuale += 0
                elif (board [yNow + (y*2)][xNow + (x*2)] == '2') and (board[yNow - y][xNow - x] != '!') and (board[yNow - y][xNow - x] != '?') and (board[yNow - (y*2)][xNow - (x*2)] != '4') and (board[yNow - (y*2)][xNow - (x*2)] != '2'):
                    xNow -= (x*2)
                    yNow -= (y*2)   
                    direzione = 4
                    ang_attuale += 270 
                elif(board[yNow + (y*2)][xNow + (x*2)] != '2'):
                    xNow += (x*2)
                    yNow += (y*2)    
                    direzione = 2
                    ang_attuale += 90
                    
                else:
                    calli=1
            
            elif (board[yNow - x][xNow + y] != '!') and (board[yNow - x][xNow + y] != '?') and (board[yNow - (x*2)][xNow + (y*2)] != '4'):
                if (board[yNow - (x*2)][xNow + (y*2)] == '2') and (board[yNow - y][xNow - x] != '!') and (board[yNow - y][xNow - x] != '?') and (board[yNow - (y*2)][xNow - (x*2)] != '4') and (board[yNow - (y*2)][xNow - (x*2)] != '2'):
                    xNow -= (x*2)
                    yNow -= (y*2)            
                    direzione = 4
                    ang_attuale += 270
                elif(board[yNow - (x*2)][xNow + (y*2)] != '2'):
                    yNow -= (x*2)
                    xNow += (y*2)
                    direzione = 1
                    ang_attuale += 0
                else:
                    calli=1
            
            elif (board[yNow - y][xNow - x] != '!') and (board[yNow - y][xNow - x] != '?') and (board[yNow - (y*2)][xNow - (x*2)] != '4'):
                xNow -= (x*2)
                yNow -= (y*2)
                direzione = 4
                ang_attuale += 270
            
            else:
                if (board[yNow + (x*2)][xNow - (y*2)] == '2'):
                    calli=1
                else:
                    
                    yNow += (x*2)
                    xNow -= (y*2)
                    direzione = 3
                    ang_attuale += 180
            
            ang_attuale = ang_attuale % 360
            print(ang_attuale)
            if calli==1:
                print("faccio calli")
                yn=yNow//2
                xn=xNow//2
                dis=0
                
                arrivo=[]
                mpcalli = [[casella() for i in range(mappa//2)] for i in range(mappa//2)]
                frontiera= [xn,yn,dis]
                mpcalli[yn][xn].distanza = 0
                while len(arrivo) == 0:
                    if len (frontiera) ==0 and ritorno == 0:
                        print ('ritorno')
                        ritorno = 1
                        board[yend][xend]= '0'
                        yn=yNow//2
                        xn=xNow//2
                        dis=0
                        arrivo=[]
                        mpcalli = [[casella() for i in range(mappa//2)] for i in range(mappa//2)]
                        frontiera= [xn,yn,dis]
                        mpcalli[yn][xn].distanza = 0
               
                    xn=frontiera[0]
                    yn=frontiera[1]
                    dis=frontiera[2]
                    dis +=1
                    if (board[(yn*2)][(xn*2) + 1]!= '!') and (board[yn*2][(xn*2) + 1]!= '?') and (board[yn*2][(xn*2) + 2]!= '4'):
                        
                        if board[yn*2][(xn*2)+2]=='2' and mpcalli[yn][xn].distanza<mpcalli[yn][xn+1].distanza:
                            mpcalli[yn][xn+1].distanza = dis
                            mpcalli[yn][xn+1].padre = 2
                            frontiera.append(xn+1)
                            frontiera.append(yn)
                            frontiera.append(dis)

                        elif board[yn*2][(xn*2) + 2]== '0':
                            arrivo.append(xn+1)
                            arrivo.append(yn)
                            arrivo.append(dis)
                            mpcalli[yn][xn+1].distanza = dis
                            mpcalli[yn][xn+1].padre = 2


                    
                    if (board[(yn*2)-1][(xn*2)]!= '!') and (board[(yn*2)-1][(xn*2)]!= '?') and (board[(yn*2)-2][(xn*2)]!= '4'):
                        if board[(yn*2)-2][(xn*2)]=='2' and mpcalli[yn][xn].distanza<mpcalli[yn-1][xn].distanza:
                            mpcalli[yn-1][xn].distanza = dis
                            mpcalli[yn-1][xn].padre = 1
                            frontiera.append(xn)
                            frontiera.append(yn-1)
                            frontiera.append(dis)

                        elif board[(yn*2)-2][(xn*2)]== '0':
                            arrivo.append(xn)
                            arrivo.append(yn-1)
                            arrivo.append(dis)
                            mpcalli[yn-1][xn].distanza = dis
                            mpcalli[yn-1][xn].padre = 1
                    
                    if (board[(yn*2)][(xn*2) - 1]!= '!') and (board[yn*2][(xn*2) - 1]!= '?') and (board[yn*2][(xn*2) - 2]!= '4'):
                        if board[yn*2][(xn*2)-2]=='2' and mpcalli[yn][xn].distanza<mpcalli[yn][xn-1].distanza:
                            mpcalli[yn][xn-1].distanza = dis
                            mpcalli[yn][xn-1].padre = 4
                            frontiera.append(xn-1)
                            frontiera.append(yn)
                            frontiera.append(dis)

                        elif board[yn*2][(xn*2) - 2]== '0':
                            arrivo.append(xn-1)
                            arrivo.append(yn)
                            arrivo.append(dis)
                            mpcalli[yn][xn-1].distanza = dis
                            mpcalli[yn][xn-1].padre = 4
                    
                    if (board[(yn*2)+1][(xn*2)]!= '!') and (board[(yn*2)+1][(xn*2)]!= '?') and (board[(yn*2)+2][(xn*2)]!= '4'):
                        if board[(yn*2)+2][(xn*2)]=='2' and mpcalli[yn][xn].distanza<mpcalli[yn+1][xn].distanza:
                            mpcalli[yn+1][xn].distanza = dis
                            mpcalli[yn+1][xn].padre = 3
                            frontiera.append(xn)
                            frontiera.append(yn+1)
                            frontiera.append(dis)

                        elif board[(yn*2)+2][(xn*2)]== '0':
                            arrivo.append(xn)
                            arrivo.append(yn+1)
                            arrivo.append(dis)
                            mpcalli[yn+1][xn].distanza = dis
                            mpcalli[yn+1][xn].padre = 3
                    
                    
#                     for i in range(mappa // 2):
#                         for j in range(mappa // 2):
#                             print(' ',mpcalli[i][j].padre, end = '')
#                          
#                         print()
#                         print()
#                     print()
#                         
                        
#                     print(frontiera)
#                     time.sleep(10)
                        
                    for i in range (3):
                        frontiera.pop(0)
                
                frontiera.clear()
                xn=arrivo[0]
                yn=arrivo[1]
                dis=arrivo[2]
                while dis!=1:
                    dis -=1
                    if mpcalli[yn][xn].padre==4:
                        xn+=1
                    elif mpcalli[yn][xn].padre==2:
                        xn-=1
                    elif mpcalli[yn][xn].padre==3:
                        yn-=1
                    elif mpcalli[yn][xn].padre==1:
                        yn+=1
#                 for i in range(mappa // 2):
#                         for j in range(mappa // 2):
#                             mpcalli[i][j].padre=0
#                 
    #             print (((ang_attuale) % 360))
    #             print ((mpcalli[yn][xn].padre-1)*90)

                if ((ang_attuale % 360))==(mpcalli[yn][xn].padre-1)*90:
                    yNow -= (x*2)
                    xNow += (y*2)
                    direzione = 1
                    ang_attuale += 0
                    
                elif ((ang_attuale+90) % 360)==(mpcalli[yn][xn].padre-1)*90:
                    xNow += (x*2)
                    yNow += (y*2)    
                    direzione = 2
                    ang_attuale += 90
                    
                elif ((ang_attuale+180) % 360)==(mpcalli[yn][xn].padre-1)*90 :
                    yNow += (x*2)
                    xNow -= (y*2)
                    direzione = 3
                    ang_attuale += 180
                    
                else:
                    xNow -= (x*2)
                    yNow -= (y*2)
                    direzione = 4
                    ang_attuale += 270
                arrivo.clear()
            
            #FINE FINE SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione#SCELGO direzione
            ang_attuale = ang_attuale % 360
            GPIO.output(26,GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(26,GPIO.HIGH)
            x=int(math.cos(math.radians(ang_attuale)))
            y=int(math.sin(math.radians(ang_attuale)))
            
            vit = -1
            bno.begin()
            if direzione == 1:
                print('Vado dritto')
            else:
                bno_ANG = bno.readAngleRot()
                if direzione == 2:
                    print('Ruoto di 90 gradi a destra')
                    ser.writeMot(1.0, 1.0, 1, 2)
                    while (bno_ANG < 85) or (bno_ANG > 350):
#                         ser.writeMot(1.0, 1.0, 1, 2)
                        bno_ANG = bno.readAngleRot()
                        #print(bno_ANG)
                    ser.writeMot()
                   
                    if check_avanti == 1:
                        try:
                            camsx_q.put_nowait(True)
                        except Queue.Full:
                            None
                    
                elif direzione == 4:
                    print('Ruoto di 90 gradi a sinistra')
                    ser.writeMot(1.0, 1.0, 2, 1)
                    while (bno_ANG > 275) or (bno_ANG < 10):
#                         ser.writeMot(1.0, 1.0, 2, 1)
                        bno_ANG = bno.readAngleRot()
                        #print(bno_ANG)
                    ser.writeMot()
                   
                    if check_avanti == 1:
                        try:
                            camdx_q.put_nowait(True)
                        except Queue.Full:
                            None
                   
                elif direzione == 3:
                    print('Ruoto di 180 gradi a destra')
                    
                    if check_avanti == 1:
                        ser.writeMot(1.0, 1.0, 1, 2)
                        while (bno_ANG < 85) or (bno_ANG > 350):
#                             ser.writeMot(1.0, 1.0, 1, 2)
                            bno_ANG = bno.readAngleRot()
                            #print(bno_ANG)
                        ser.writeMot()
                        try:
                            camsx_q.put_nowait(True)
                        except Queue.Full:
                            None
                        time.sleep(0.25)   
                        try:
                            vit = vittima.get_nowait()
                        except Queue.Empty:
                            vit = -1
                            pass
                        if vit>=0:
                            led.blink(5)
                        bno.begin()
                        time.sleep(0.1)
                        bno_ANG = bno.readAngleRot()
                        ser.writeMot(1.0, 1.0, 1, 2)
                        while (bno_ANG < 85) or (bno_ANG > 350):
#                             ser.writeMot(1.0, 1.0, 1, 2)
                            bno_ANG = bno.readAngleRot()
                            #print(bno_ANG)
                        ser.writeMot()
                        
                    else:
                        ser.writeMot(0.7, 0.7, 1, 2)
                        while (bno_ANG < 173) or (bno_ANG > 190):
                            bno_ANG = bno.readAngleRot()
                            #print(bno_ANG)
                        ser.writeMot()
          
            
#             print ('cosa vedo dietro')
#             print (board[yNow + x][xNow - y])
#             print(ang_attuale)
#             print(x)
#             print (y)
#             print(xNow)
#             print(yNow)
            
            if (board[yStart + x][xStart - y] == '!') or (board[yStart + x][xStart - y] == '?'):
                mv.indietro()
                mv.avanti(cm = 4)
                print('sbatto')            
            GPIO.output(26,GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(26,GPIO.HIGH)
            
            board[yStart][xStart] = '2'
            calli=0
            
            try:
                vit = vittima.get_nowait()
            except Queue.Empty:
                vit = -1
                pass
            if vit>=0:
                led.blink(5)
                
            check_avanti = 0
            
            #AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI
            dis = mv.avanti(nero = nero)
#             print (dis)
#             print ('distanza gg')
            #AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI#AVANTI
            
            if (apds.readC()<nero) and (apds.readB()<blu):
                print('Negro')
                mv.indietro(dis/100)
                
                board[yNow][xNow] = '4'
                yNow = yStart
                xNow = xStart
                
                ang_attuale += 180
                
                bno.begin()
                print('Ruoto di 180 gradi')
                bno_ANG = bno.readAngleRot()
                ser.writeMot(0.7, 0.7, 1, 2)
                while (bno_ANG < 173) or (bno_ANG > 190):
#                     ser.writeMot(0.7, 0.7, 1, 2)
                    bno_ANG = bno.readAngleRot()
                   # print(bno_ANG)
                ser.writeMot()
                
            elif(apds.readB()<blu):
                print('Blu')
                time.sleep(4.5)
                    
                GPIO.output(26,GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(26,GPIO.HIGH)
                
            
        #     if(apds.read grigio):
        #         print("CHECK")
        #         check = board.copy()
                
            Fc_avanti = fc.read()
            if not(Fc_avanti[1]):
                if dis<1000:
                    print('finecorsa -1')
                    mv.indietro(dis/100)
                    xNow=xStart
                    yNow=yStart
                else:
                    print('finecorsa')
                    mv.indietro(3)
            
            if yStart != yNow or xStart != xNow :
                yStart = yNow
                xStart = xNow
        #         board[yNow][xNow] = '1'
            
            print()
            print(ang_attuale)
            
            GPIO.output(26,GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(26,GPIO.HIGH)
        else:
            # Il programma è in pausa
            print("Programma in pausa...")
            time.sleep(0.1)
        
            

    # base bianca=2 /base blu=3 /base nera =4 
