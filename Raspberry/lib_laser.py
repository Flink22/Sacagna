import smbus
import time
import struct
import board

class VL6180X:
    VL6180X_ADDRESS = 0x29
    VL6180X_ID_ADDRESS = 0x000
    VL6180X_ID      = 0xB4
    
    VL6180X_GPIO_0  = 0x010
    VL6180X_GPIO_1  = 0x011
    VL6180X_START_RANGE = 0x018
    VL6180X_INTERMEASUREMENT = 0x01B
    VL6180X_HISTORY_CTRL = 0x012
    VL6180X_INTERRUPT_CONFIG = 0x014
    VL6180X_CALIBRATE = 0x02E
    VL6180X_CALIBRATE_INTERVALL = 0x031
    
    VL6180X_SLAVE_ADDRESS = 0x212
    
    VL6180X_DATA  = 0x064
    
    def __init__(self, sensorId=-1, address=VL6180X_ADDRESS):
        self._sensorId = sensorId
        self._address = address
    
    def begin(self):
        self._bus = smbus.SMBus(1)
        
        while self.readBytes(VL6180X.VL6180X_ID_ADDRESS)[0] != VL6180X.VL6180X_ID:
            time.sleep(0.01)
        time.sleep(0.05)
        
        self.writeBytes(0x0207, 0x01)
        self.writeBytes(0x0208, 0x01)
        self.writeBytes(0x0096, 0x00)
        self.writeBytes(0x0097, 0xfd)
        self.writeBytes(0x00e3, 0x00)
        self.writeBytes(0x00e4, 0x04)
        self.writeBytes(0x00e5, 0x02)
        self.writeBytes(0x00e6, 0x01)
        self.writeBytes(0x00e7, 0x03)
        self.writeBytes(0x00f5, 0x02)
        self.writeBytes(0x00d9, 0x05)
        self.writeBytes(0x00db, 0xce)
        self.writeBytes(0x00dc, 0x03)
        self.writeBytes(0x00dd, 0xf8)
        self.writeBytes(0x009f, 0x00)
        self.writeBytes(0x00a3, 0x3c)
        self.writeBytes(0x00b7, 0x00)
        self.writeBytes(0x00bb, 0x3c)
        self.writeBytes(0x00b2, 0x09)
        self.writeBytes(0x00ca, 0x09)
        self.writeBytes(0x0198, 0x01)
        self.writeBytes(0x01b0, 0x17)
        self.writeBytes(0x01ad, 0x00)
        self.writeBytes(0x00ff, 0x05)
        self.writeBytes(0x0100, 0x05)
        self.writeBytes(0x0199, 0x05)
        self.writeBytes(0x01a6, 0x1b)
        self.writeBytes(0x01ac, 0x3e)
        self.writeBytes(0x01a7, 0x1f)
        self.writeBytes(0x0030, 0x00)
        
        self.writeBytes(VL6180X.VL6180X_GPIO_0, [0x40])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_GPIO_1, [0x00])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_HISTORY_CTRL, [0x00])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_INTERRUPT_CONFIG, [0x00])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_START_RANGE, [0x02])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_INTERMEASUREMENT, [0x04])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_CALIBRATE, [0x01])
        time.sleep(0.05)
        self.writeBytes(VL6180X.VL6180X_CALIBRATE_INTERVALL, [0x00])
        time.sleep(0.05)
        return True
    
    def readDistance(self):
        buf = self.readBytes(VL6180X.VL6180X_DATA)
        return buf[0]
    
    def readBytes(self, register, numBytes=1):
        return self._bus.read_i2c_block_data(self._address, register, numBytes)
    
    def writeBytes(self, register, byteVals):
        return self._bus.write_i2c_block_data(self._address, register, byteVals)
    
if __name__ == '__main__':
    vl = VL6180X()
    if vl.begin() is not True:
        print("Error initializing VL6180X")
        exit()
    time.sleep(1)
    while True:
        print(apds.readDistance())
        time.sleep(0.01)
