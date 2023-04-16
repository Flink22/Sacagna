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
    
    def avanti(self, cm = 28.5):
        cm = cm * 100
        ser.resetD()
        ser.writeMot(1.0, 1.0, 1, 1)
        
        Fc_avanti = fc.read()
        apds.begin()
        
        dis = 0
        print("Avanti")
        while (dis < cm) and (Fc_avanti[1]) and (apds.readC()>50):
            ser.askD()
            dis = ser.read()
            time.sleep(0.002)
            Fc_avanti = fc.read()
            print(dis)
            
        ser.writeMot()
        time.sleep(0.25)
        ser.resetD()
        ser.clean()
    
    def indietro(self, cm = 5.0):
        cm = cm * 100
        ser.resetD()
        ser.writeMot(1.0, 1.0, 0, 0)
        
        dis = 0
        print("Indietro")
        while dis < cm:
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
        mv.indietro()
        time.sleep(5)

