import smbus
import time
import struct
import board

class VL6180X:
    VL6180X_ADDRESS = 0x29
    VL6180X_ID      = 0xB4
    
    VL6180X_GPIO_0  = 0x010
    VL6180X_GPIO_1  = 0x011
    VL6180X_START_RANGE = 0x018
    VL6180X_INTERMEASUREMENT = 0x01B
    
    VL6180X_SLAVE_ADDRESS = 0x212
    
    VL6180X_DATA  = 0x064
    
    def __init__(self, sensorId=-1, address=VL6180X_ADDRESS):
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
    
    def readColor(self):
        buf = self.readBytes(APDS9960.APDS9960_CDATAL, 8)
        xyz = struct.unpack('hhhh', struct.pack('BBBBBBBB', buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]))
        return tuple([i for i in xyz])
    
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
        print(apds.readColor())
        time.sleep(0.01)
