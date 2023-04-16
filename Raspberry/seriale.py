import serial
import time
import struct

class SERIALEPICO:
    
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate = 1000000,
            parity= serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS, 
            timeout = 0
        )
        self.error = "serial error"
    
    def read(self, byte = 2):
        start = time.time()
        out = 0
        while(self.ser.in_waiting <= 0):
            if((time.time() - start) > 0.002):
                print(self.error)
                out = 1
                break
        if out != 1:
            readbyte = self.ser.read(size = byte)
            if (len(readbyte) != byte):
                print(self.error)
            else:
                out = readbyte[0] + readbyte[1] * 100
                if out != 1013:
                    return out
                else:
                    out = 5
        return 1
    
    def write(self, byte):
        self.ser.write(struct.pack('>B',byte))
        
    def vel(self, vel):
        if vel > 1.55:
            vel = 1.55
        elif vel < 0.0:
            vel = 0.0
        return vel
    
    def writeMot(self, vel_dx = 0.0, vel_sx = 0.0,  dir_dx = 0, dir_sx = 0):
        #invia velocità motori, posso richiedere la distanza
        #writeMot() ferma tutto e non richiede la distanza
        
        self.ser.flush()
        
        vel_dx_i = int((self.vel(vel_dx)) * 20)
        vel_sx_i = int((self.vel(vel_sx)) * 20)
        
        dx = [0]*8
        sx = [0]*8
        
        for i in range (1,6):
            dx[i] = vel_dx_i % 2
            sx[i] = vel_sx_i % 2
            vel_dx_i = vel_dx_i // 2
            vel_sx_i = vel_sx_i // 2
            
        byte = [0]*2
        
        byte[0] = (1<<7) | (1<<6) | (dir_dx<<0) #DX
        byte[1] = (1<<7) | (0<<6) | (dir_sx<<0) #SX
        for i in range (1,6):
            byte[0] |= (dx[i]<<i)
            byte[1] |= (sx[i]<<i)
                
        for i in range (2):
            self.write(byte[i])
    
    def resetD(self):
        self.clean()
        byte = (0<<7) | (1<<6)
        self.write(byte)
        
    def askD(self):
        self.clean()
        byte = (0<<7) | (0<<6) | (1<<5)
        self.write(byte)
        
    def clean(self):
        self.ser.flush()
        self.ser.flushInput()


if __name__ == '__main__':
    serial = SERIALEPICO()
    serial.writeMot(1.0, 1.0, 1, 1)
    time.sleep(1)
    while True:
        a=0
        while a<2850:
            serial.writeMot(0.8, 0.8, 1, 1)
            serial.askD()
            print('--------')
            a = serial.read()
            print(a)
        
        serial.writeMot()
        time.sleep(1)
        serial.resetD()
    
    serial.writeMot()
        

