import RPi.GPIO as gpio
import board
import busio
import time
import adafruit_vl6180x as vl6180

laser_SHDN = [5, 6, 13, 19, 26]
laser_ADDRESS = [0x20, 0x22, 0x24, 0x26, 0x28]
laser_MM = [5, 6, 13, 19, 26]
i2c = busio.I2C(board.SCL, board.SDA)

def init():
    
    for i in range(0, 5):
        gpio.setup(laser_SHDN[i],gpio.OUT)
        gpio.output(laser_SHDN[i],gpio.LOW)
    
    for i in range(0, 5):
        gpio.output(laser_SHDN[i],gpio.HIGH)
        sensor = vl6180.VL6180X(i2c)
        sensor._write_8(0x212, laser_ADDRESS[i])
        time.sleep(1)
    

def read():
    
    for i in range(0, 5):
        sensor = vl6180.VL6180X(i2c, address = laser_ADDRESS[i])
        laser_MM[i] = sensor.range
        print("Range: {0}mm".format(laser_MM[i]))
        
    time.sleep(1)

if __name__ == "__main__":
    init()
    while True:
        read()
        print(" ------------- ")