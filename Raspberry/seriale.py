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
        gpio.setup(25,gpio.OUT)
        gpio.setup(11,gpio.OUT)
        gpio.output(25,gpio.LOW)
        gpio.output(11,gpio.LOW)
        
    
    
    def check_port(self):
        if self.ser.isOpen() != True:
            return self.noPort
        else:
            return 1
    
    
    
    def read(self):
        out = self.check_port()
        if out == 1:
            if(self.ser.in_waiting >= 0):
                readbyte = self.ser.read(size = 1)
                if (len(readbyte) != 1):
                    out = self.error
                else:
                    out = readbyte[0]
        else:
            out = self.error
        return out
    
    
    
    def write(self, byte):
        out = self.check_port()
        if out == 1:
            self.ser.write(struct.pack('>B',byte))
    
    
    
    def clean(self):
        self.ser.flush()
        self.ser.flushInput()


if __name__ == '__main__':
    serial = SerialeATmega()
    a = 70
    while True:
        data = serial.read()
        serial.write(a)
        time.sleep(0.1)
        print(data)
        serial.clean()
        print('------') 

