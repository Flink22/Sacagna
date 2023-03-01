import RPi.GPIO as gpio
import board
import busio
import time
import adafruit_vl6180x as vl6180

laser_SHDN = [23, 24, 20, 21, 18]
laser_ADDRESS = [0x20, 0x21, 0x22, 0x23, 0x24]
laser_MM = [0, 0, 0, 0, 0]
i2c = busio.I2C(board.SCL, board.SDA)

class VL6180:
    def __init__(self):
        gpio.setup(10,gpio.OUT)
        gpio.output(10,gpio.LOW)
        for i in range(0, 5):
            gpio.setup(laser_SHDN[i],gpio.OUT)
            gpio.output(laser_SHDN[i],gpio.LOW)
        
        for i in range(0, 5):
            gpio.output(laser_SHDN[i],gpio.HIGH)
            sensor = vl6180.VL6180X(i2c)
            sensor._write_8(0x212, laser_ADDRESS[i])
            time.sleep(0.1)
    

    def read(self, n = 1):
        for i in range(0, 5):
            laser_MM[i] = 0
            for k in range(n):
                sensor = vl6180.VL6180X(i2c, address = laser_ADDRESS[i])
                laser_MM[i] += sensor.range
            
            laser_MM[i] = laser_MM[i]/2
        
        return laser_MM
