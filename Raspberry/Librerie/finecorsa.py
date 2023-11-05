import RPi.GPIO as GPIO
import board
import time

class FINECORSA:
    
    FINECORSA_Av_C = 7
    FINECORSA_Av_D = 8
    FINECORSA_Av_S = 6
    
    FINECORSA_Av_C_S = False
    FINECORSA_Av_D_S = False
    FINECORSA_Av_S_S = False
    
    def __init__(self):
        GPIO.setup(self.FINECORSA_Av_C, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.FINECORSA_Av_D, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.FINECORSA_Av_S, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        
    def read(self):
        self.FINECORSA_Av_D_S = not(GPIO.input(self.FINECORSA_Av_D))
        self.FINECORSA_Av_C_S = not(GPIO.input(self.FINECORSA_Av_C))
        self.FINECORSA_Av_S_S = not(GPIO.input(self.FINECORSA_Av_S))
        
        return (self.FINECORSA_Av_D_S, self.FINECORSA_Av_C_S, self.FINECORSA_Av_S_S)

if __name__ == '__main__':
    fc = FINECORSA()
    while True:
        print(fc.read())
        time.sleep(0.01)