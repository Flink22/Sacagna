import smbus
import time
import struct
import board

class APDS9960:
    APDS9960_ADDRESS = 0x39
    APDS9960_ID = 0xAB
    
    APDS9960_ENABLE = 0x80
    
    APDS9960_CDATAL  = 0x94
    APDS9960_CDATAH  = 0x95
    APDS9960_RDATAL  = 0x96
    APDS9960_RDATAH  = 0x97
    APDS9960_GDATAL  = 0x98
    APDS9960_GDATAH  = 0x99
    APDS9960_BDATAL  = 0x9A
    APDS9960_BDATAH  = 0x9B
    
    def __init__(self, sensorId=-1, address=APDS9960_ADDRESS):
        self._sensorId = sensorId
        self._address = address
    
    def begin(self):
        
    
    def readColor(self):
        buf = self.readBytes(APDS9960_CDATAL, 8)
        xyz = struct.unpack('hhhh', struct.pack('BBBBBBBB', buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]))
        return tuple([i for i in xyz])
    
    def readBytes(self, register, numBytes=1):
        return self._bus.read_i2c_block_data(self._address, register, numBytes)
    
    def writeBytes(self, register, byteVals):
        return self._bus.write_i2c_block_data(self._address, register, byteVals)
