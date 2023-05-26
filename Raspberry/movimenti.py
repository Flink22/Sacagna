import time

from seriale import SERIALEPICO
from finecorsa import FINECORSA
from giroscopio import BNO055
from colore import APDS9960

ser = SERIALEPICO()
fc  = FINECORSA()
bno = BNO055()
apds = APDS9960()

class MOVIMENTI:
    
    def avanti(self, cm = 28.5,nero = 750 ):
        cm = cm * 100
        ser.resetD()
#         ser.writeMot(1.0, 1.0, 1, 1)
        
        Fc_avanti = fc.read()
        apds.begin()
        
        bno.begin()
        rampa = 0
        dis = 0
        print("Avanti")
        while (dis < cm) and (Fc_avanti[1]) and (apds.readC()>nero):
            ser.writeMot(1.5, 1.5, 1, 1)
            if ((bno.readAngleInc() <= -15) or (bno.readAngleInc() >= 15)):
                rampa = 1
                while ((bno.readAngleInc() <= -15) or (bno.readAngleInc() >= 15)) and (Fc_avanti[1]):
                    ser.writeMot(1.5, 1.5, 1, 1)
                    Fc_avanti = fc.read()
                    print("Rampa")
                ser.resetD()
                cm = 1300
            ser.askD()
            dis = ser.read()
            Fc_avanti = fc.read()
            
#         while ((bno.readAngleInc() <= -15) or (bno.readAngleInc() >= 15)) and (Fc_avanti[1]):
#             ser.writeMot(1.0, 1.0, 1, 1)
#             Fc_avanti = fc.read()
#             print("Rampa")
            
        ser.writeMot()
        time.sleep(0.25)
        ser.resetD()
        ser.clean()
    
    def indietro(self, cm = 4.0):
        cm = cm * 100
        ser.resetD()
        ser.writeMot(1.2, 1.2, 0, 0)
        
        dis = 0
        print("Indietro")
        while dis < cm:
            ser.writeMot(1.2, 1.2, 0, 0) 
            ser.askD()
            dis = ser.read()
            time.sleep(0.002)
            print(dis)
        
        ser.writeMot()
        time.sleep(0.25)
        ser.resetD()
        ser.clean()

if __name__ == '__main__':
    mv = MOVIMENTI()
    while True:
        mv.avanti(cm = 2000)
        time.sleep(5)
