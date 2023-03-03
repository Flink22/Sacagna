import serial
import time
import struct
import RPi.GPIO as gpio
import board

class SerialeATmega:
    
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=500000,
            parity= serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS, 
            timeout = 0.001
        )
        self.error = "error"
        self.noPort = "noPort"        
    
    
    def check_port(self):
        if self.ser.isOpen() != True:
            return self.noPort
        else:
            return 1
    
    
    
    def read(self, size = 4):
        out = self.check_port()
        if out == 1:
            if(self.ser.in_waiting >= 0):
                readbyte = self.ser.read(size)
                if (len(readbyte) != size):
                    out = self.error
                else:
                    out = readbyte[0] + readbyte[1] * 10 + readbyte[2] * 100 + readbyte[3] * 1000
        else:
            out = self.error
        if out != "error":
            return int(out)
    
    
    
    def write(self, byte):
        out = self.check_port()
        if out == 1:
            self.ser.write(struct.pack('>B',byte))
    
    
    
    def clean(self):
        self.ser.flush()
        self.ser.flushInput()


if __name__ == '__main__':
    serial = SerialeATmega()
    while True:
        data = serial.write(11)
        while(data < 137):
            data = serial.read()
            print(data)
            print('------')
            serial.clean()
            time.sleep(0.01)
        time.sleep(2)
        serial.clean()
