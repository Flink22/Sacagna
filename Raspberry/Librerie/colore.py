import smbus
import time
import struct

class APDS9960:
    APDS9960_ADDRESS = 0x29
    APDS9960_ID      = 0xAB
    APDS9960_CHIP_ID_ADDR = 0x92
    
    APDS9960_ENABLE  = 0x80
    APDS9960_ATIME   = 0x81
    APDS9960_WTIME   = 0x83
    APDS9960_CONTROL = 0x8F
    APDS9960_CONFIG1 = 0x8D
    APDS9960_CONFIG2 = 0x90
    APDS9960_CONFIG3 = 0x9F
    
    APDS9960_CDATAL  = 0x94
    APDS9960_CDATAH  = 0x95
    APDS9960_RDATAL  = 0x96
    APDS9960_RDATAH  = 0x97
    APDS9960_GDATAL  = 0x98
    APDS9960_GDATAH  = 0x99
    APDS9960_BDATAL  = 0x9A
    APDS9960_BDATAH  = 0x9B
    
    def __init__(self, sensorId=-1, address=0x39):
        self._sensorId = sensorId
        self._address = address
    
    def begin(self):
        self._bus = smbus.SMBus(1)
        
        while self.readBytes(APDS9960.APDS9960_CHIP_ID_ADDR)[0] != APDS9960.APDS9960_ID:
            time.sleep(0.01)
        time.sleep(0.05)
        
        self.writeBytes(APDS9960.APDS9960_ENABLE, [0x03])
        time.sleep(0.05)
        self.writeBytes(APDS9960.APDS9960_ATIME, [0xF6])
        time.sleep(0.05)
        self.writeBytes(APDS9960.APDS9960_CONFIG1, [0x62])
        time.sleep(0.05)
        self.writeBytes(APDS9960.APDS9960_CONTROL, [0x43])
        time.sleep(0.05)
        return True
    
    def readC(self):
        buf = self.readBytes(APDS9960.APDS9960_CDATAL, 2)
        clear = struct.unpack('h', struct.pack('BB', buf[0], buf[1]))
        return clear[0]
    
    def readB(self):
        buf = self.readBytes(APDS9960.APDS9960_BDATAL, 2)
        blue = struct.unpack('h', struct.pack('BB', buf[0], buf[1]))
        return blue[0]
    
    def readBytes(self, register, numBytes=1):
        return self._bus.read_i2c_block_data(self._address, register, numBytes)
    
    def writeBytes(self, register, byteVals):
        return self._bus.write_i2c_block_data(self._address, register, byteVals)
    
if __name__ == '__main__':
    apds = APDS9960()
    if apds.begin() is not True:
        print("Error initializing APDS9960")
        exit()
    time.sleep(1)
    while True:
        print(apds.readB())
        time.sleep(0.01)
