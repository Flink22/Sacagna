import RPi.GPIO as gpio
import board
import busio
import time
import adafruit_vl6180x as vl6180

laser_SHDN = [23, 24, 20, 21, 18]
bno_SHDN = 9
laser_ADDRESS = [0x20, 0x22, 0x24, 0x26, 0x28]
laser_MM = [0, 0, 0, 0, 0]
i2c = busio.I2C(board.SCL, board.SDA)

def init():
    
    gpio.setup(bno_SHDN,gpio.OUT)
    gpio.output(bno_SHDN,gpio.LOW) #ricordati di accendere il bno!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    for i in range(0, 5):
        gpio.setup(laser_SHDN[i],gpio.OUT)
        gpio.output(laser_SHDN[i],gpio.LOW)
    
    for i in range(0, 5):
        gpio.output(laser_SHDN[i],gpio.HIGH)
        sensor = vl6180.VL6180X(i2c)
        sensor._write_8(0x212, laser_ADDRESS[i])
        time.sleep(0.01)
    

def read():
    
    for i in range(0, 5):
        
        laser_MM[i] = 0
        
        for k in range(0, 5):
            sensor = vl6180.VL6180X(i2c, address = laser_ADDRESS[i])
            laser_MM[i] += sensor.range
        
        laser_MM[i] = laser_MM[i]/5
        
    time.sleep(1)
    return laser_MM
