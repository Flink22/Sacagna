import RPi.GPIO as gpio
import board
import time

led = [11, 25]

class LED:
    
    def __init__(self):
        gpio.setup(led[0],gpio.OUT)
        gpio.setup(led[1],gpio.OUT)
    
    def blink(self, n):
        for i in range(n):
            gpio.output(led[0],gpio.HIGH)
            gpio.output(led[1],gpio.HIGH)
            time.sleep(0.5)
            gpio.output(led[0],gpio.LOW)
            gpio.output(led[1],gpio.LOW)
            time.sleep(0.5)
