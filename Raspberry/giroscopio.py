import smbus
import time
import struct

class BNO055:
    BNO055_ID 				= 0xA0
    
    POWER_MODE_NORMAL 		= 0X00
    OPERATION_MODE_CONFIG 	= 0X00
    OPERATION_MODE_IMUPLUS 	= 0X08
    
    VECTOR_EULER 			= 0x1A
    
    BNO055_PAGE_ID_ADDR 	= 0X07
    BNO055_CHIP_ID_ADDR 	= 0x00
    
    BNO055_OPR_MODE_ADDR 	= 0X3D
    BNO055_PWR_MODE_ADDR 	= 0X3E
    
    BNO055_SYS_TRIGGER_ADDR = 0X3F
    
    def __init__(self, sensorId=-1, address=0x28):
        self._sensorId = sensorId
        self._address = address
        self._mode = BNO055.OPERATION_MODE_IMUPLUS
    
    def begin(self, mode=None):
        if mode is None:
            mode = self._mode
        self._bus = smbus.SMBus(1)
        
        if self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
            time.sleep(0.6)
            if self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
                return False
        
        self.setMode(BNO055.OPERATION_MODE_CONFIG)
        
        self.writeBytes(BNO055.BNO055_SYS_TRIGGER_ADDR, [0x20])
        time.sleep(0.6)
        while self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
            time.sleep(0.01)
        time.sleep(0.05)
        
        self.writeBytes(BNO055.BNO055_PWR_MODE_ADDR, [BNO055.POWER_MODE_NORMAL])
        time.sleep(0.01)
        
        self.writeBytes(BNO055.BNO055_PAGE_ID_ADDR, [0])
        self.writeBytes(BNO055.BNO055_SYS_TRIGGER_ADDR, [0])
        time.sleep(0.01)
        
        self.setMode(BNO055.OPERATION_MODE_CONFIG)
        time.sleep(0.025)
        self.writeBytes(BNO055.BNO055_PAGE_ID_ADDR, [0])
        self.writeBytes(BNO055.BNO055_SYS_TRIGGER_ADDR, [0x80])
        self.setMode(mode)
        time.sleep(0.02)
        
        return True
    
    def readAngle(self):
        buf = self.readBytes(BNO055.VECTOR_EULER, 6)
        xyz = struct.unpack('hhh', struct.pack('BBBBBB', buf[0], buf[1], buf[2], buf[3], buf[4], buf[5]))
        return tuple([i/16.0 for i in xyz])
    
    def setMode(self, mode):
        self._mode = mode
        self.writeBytes(BNO055.BNO055_OPR_MODE_ADDR, [self._mode])
        time.sleep(0.03)
    
    def readBytes(self, register, numBytes=1):
        return self._bus.read_i2c_block_data(self._address, register, numBytes)
    
    def writeBytes(self, register, byteVals):
        return self._bus.write_i2c_block_data(self._address, register, byteVals)


if __name__ == '__main__':
    bno = BNO055()
    if bno.begin() is not True:
        print("Error initializing device")
        exit()
    time.sleep(1)
    while True:
        print(bno.readAngle())
        time.sleep(0.01)
