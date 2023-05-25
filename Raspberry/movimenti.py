import time
import math

from seriale import SERIALEPICO
from finecorsa import FINECORSA
from giroscopio import BNO055
from colore import APDS9960

ser = SERIALEPICO()
fc  = FINECORSA()
bno = BNO055()
apds = APDS9960()

class MOVIMENTI:
    
    def avanti(self, cm = 28.5):
        cm = cm * 100
        ser.resetD()
        
        Fc_avanti = fc.read()
        apds.begin()
        bno.begin()
        
        dis = 0
        print("Avanti")
        while (dis < cm) and (Fc_avanti[1]) and (apds.readC()>50):
            
            #PID
            ser.writeMot(1.0, 1.0, dx, sx)
            
            ser.askD()
            dis = ser.read()
            time.sleep(0.002)
            Fc_avanti = fc.read()
            
        ser.writeMot()
        ser.resetD()
        ser.clean()
        if dis < 1000:
            return 2
    
    def indietro(self, cm = 5.0):
        cm = cm * 100
        ser.resetD()
        ser.writeMot(1.0, 1.0, 0, 0)
        
        dis = 0
        print("Indietro")
        while dis < cm:
            ser.writeMot(1.0, 1.0, 0, 0)
            ser.askD()
            dis = ser.read()
            time.sleep(0.002)
            print(dis)
        
        ser.writeMot()
        ser.resetD()
        ser.clean()

if __name__ == '__main__':
    mv = MOVIMENTI()
    while True:
        mv.indietro()
        time.sleep(5)

