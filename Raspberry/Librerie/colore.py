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
    
    APDS9960_DATA  = 0x94
    
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
    
    def read(self):
        buf = self.readBytes(APDS9960.APDS9960_DATA, 8)
        clear = struct.unpack('hhhh', struct.pack('BBBBBBBB', buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]))
        return clear
    
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
        print(apds.read())
        time.sleep(0.01)
