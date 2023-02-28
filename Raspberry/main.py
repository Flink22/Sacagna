import laser
import RPi.GPIO as gpio
import board
import busio
import math
import time
import Serial

laser_MM = [0, 0, 0, 0, 0]
led = [11, 25]

# serial = Serial.SerialeATmega()
laser = laser.Laser()

# gpio.setup(led[0],gpio.OUT)
# gpio.setup(led[1],gpio.OUT)

while True:
#     letturaseriale = serial.read()
    laser_MM = laser.read()
    
    ang_DX = (math.atan((laser_MM[1] - laser_MM[2])/170))*180/math.pi
    ang_SX = (math.atan((laser_MM[4] - laser_MM[3])/170))*180/math.pi
    
    print(str(ang_DX) + " | " + str(ang_SX))
#     print(letturaseriale)
#     
#     gpio.output(led[0],gpio.HIGH)
#     gpio.output(led[1],gpio.HIGH)
#     
#     time.sleep(0.5)
#     
#     gpio.output(led[0],gpio.LOW)
#     gpio.output(led[1],gpio.LOW)
#     
    time.sleep(0.5)
