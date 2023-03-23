import smbus
import time
import struct
import RPi.GPIO as gpio
import board

class APDS9960:
  APDS9960_ADDRESS = 0x39
  APDS9960_ID = 0xAB
  
  APDS9960_ENABLE = 0x80
  
  def __init__(self, sensorId=-1, address=0x28):
        self._sensorId = sensorId
        self._address = address
        self._mode = BNO055.OPERATION_MODE_IMUPLUS
