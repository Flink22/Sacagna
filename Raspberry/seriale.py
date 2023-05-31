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
                out = readbyte[0] + (readbyte[1] << 8)
        return out
    
    def write(self, byte):
        self.ser.write(struct.pack('>B',byte))
        
    def vel(self, vel):
        if vel > 2.54:
            vel = 2.54
        elif vel < 0.0:
            vel = 0.0
        return vel
    
    def writeMot(self, vel_dx = 0.0, vel_sx = 0.0,  dir_dx = 3, dir_sx = 3):
        #invia velocità motori
        #writeMot() ferma tutto e non richiede la distanza
        
        self.clean()
        
        vel_dx_i = int((self.vel(vel_dx)) * 50)
        vel_sx_i = int((self.vel(vel_sx)) * 50)
        
        dx = [0]*8
        sx = [0]*8
        dirdx = [0]*2
        dirsx = [0]*2
        
        for i in range (0,7):
            dx[i] = vel_dx_i % 2
            sx[i] = vel_sx_i % 2
            vel_dx_i = vel_dx_i // 2
            vel_sx_i = vel_sx_i // 2
            
        dirdx[0] = dir_dx & 0x01
        dirdx[1] = dir_dx >> 1
        dirsx[0] = dir_sx & 0x01
        dirsx[1] = dir_sx >> 1
        
        byte = [0]*4
        
        byte[0] = (0<<7) | (0<<6) | (1<<5) | (1<<2) | (dirdx[1]<<1) | (dirdx[0]<<0)  #DX
        byte[2] = (0<<7) | (0<<6) | (1<<5) | (0<<2) | (dirsx[1]<<1) | (dirsx[0]<<0)  #SX
        
        for i in range (1,7):
            byte[1] |= (dx[i]<<i)
            byte[3] |= (sx[i]<<i)
        
        byte[1] |= (1<<7)
        byte[3] |= (1<<7)
                
        for i in range (4):
            self.write(byte[i])
    
    def resetD(self):
        self.clean()
        byte = (0<<7) | (1<<6)
        self.write(byte)
        
    def askD(self):
        self.clean()
        byte = (0<<7) | (1<<6) | (1<<3)
        self.write(byte)
        
    def askK(self, d, n =  0):
        self.clean()
        
        if d == 'DX':
            d = 1
        else:
            d = 0
        
        l = n & 0x01;
        h = n >> 1;
        
        byte = (0<<7) | (1<<6) | (1<<4) | (lato<<2) | (h<<1) | (l<<0)
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
