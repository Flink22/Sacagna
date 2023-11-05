import RPi.GPIO as GPIO
import board
import time
import adafruit_vl6180x as vl6180

i2c = board.I2C()

class sensor:
    misura = None
    def define(self, pin = -1, address = -1):
        self.pin = pin
        self.address = address

class VL6180:
    def __init__(self):
        
        self.laser = [sensor() for i in range(5)]
        self.laser[0].define(pin = 23, address = 0x20)
        self.laser[1].define(pin = 24, address = 0x21)
        self.laser[2].define(pin = 20, address = 0x22)
        self.laser[3].define(pin = 21, address = 0x23)
        self.laser[4].define(pin = 18, address = 0x24)
        GPIO.setup(9,GPIO.OUT)
        GPIO.output(9,GPIO.LOW)
        for i in range(0, 5):
            GPIO.setup(self.laser[i].pin,GPIO.OUT)
            GPIO.output(self.laser[i].pin,GPIO.LOW)
        
        for i in range(0, 5):
            GPIO.output(self.laser[i].pin,GPIO.HIGH)
            time.sleep(0.1)
            ls = vl6180.VL6180X(i2c)
            ls._write_8(0x212, self.laser[i].address)
            time.sleep(0.1)
            self.laser[i].misura = vl6180.VL6180X(i2c, self.laser[i].address)
        print("Laser INIT finito")
        GPIO.output(9,GPIO.HIGH)


    def read(self , n):
        misura = self.laser[n].misura.range
        if misura < 10:
            misura = 255
        return misura

if __name__ == '__main__':
    laser = VL6180()
    while True:
        print("------------")
        for i in range(5):
            a = laser.read(i)
            print(a)
        time.sleep(0.5)

