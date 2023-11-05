import board
import neopixel
import time
import RPi.GPIO as GPIO

class LED:
    def __init__(self):
        self.led = [11, 25, 12, 16]
        GPIO.setup(self.led[0],GPIO.OUT)
        GPIO.setup(self.led[1],GPIO.OUT)
        GPIO.setup(self.led[2],GPIO.OUT)
        GPIO.setup(self.led[3],GPIO.OUT)
#         self.np = neopixel.NeoPixel(board.D12, 1, brightness=0.5)
        
    def lack(self):
        GPIO.output(self.led[2],GPIO.LOW)
        GPIO.output(self.led[3],GPIO.HIGH)
                
    def ok(self):
        GPIO.output(self.led[2],GPIO.HIGH)
        GPIO.output(self.led[3],GPIO.LOW)
    
    def stop(self):
        GPIO.output(self.led[3],GPIO.LOW)
        GPIO.output(self.led[2],GPIO.LOW)
    
        
    def blink(self, n):
        for i in range(n):
            GPIO.output(self.led[0],GPIO.LOW)
            GPIO.output(self.led[1],GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self.led[0],GPIO.HIGH)
            GPIO.output(self.led[1],GPIO.HIGH)
            time.sleep(0.5)

if __name__ == "__main__":
    ld = LED()
    while True:
        
        ld.ok()
        time.sleep(0.1)
        ld.stop()
        time.sleep(0.1)
#     time.sleep(1)
#     ld.stop()
#     time.sleep(1)
#     ld.ok()
#     time.sleep(2)
#     ld.stop()
