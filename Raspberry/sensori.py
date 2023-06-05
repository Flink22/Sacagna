import RPi.GPIO as GPIO
import board
import time
import adafruit_vl6180x as vl6180

import giroscopio
import colore

i2c = board.I2C()

class sensor:
    misura = None
    def define(self, pin = -1, address = -1):
        self.pin = pin
        self.address = address

class sensors:
    def __init__(self):
        
        self.bno = sensor()
        self.bno.define(pin = 10, address = 0x28)
        self.bno.current = [0] * 3
        self.bno.offset = [0] * 3
        self.bno.old= [None] * 3
        
        self.apds = sensor()
        self.apds.define(address = 0x39)
        
        self.laser = [sensor() for i in range(5)]
        self.laser[0].define(pin = 23, address = 0x20)
        self.laser[1].define(pin = 24, address = 0x21)
        self.laser[2].define(pin = 20, address = 0x22)
        self.laser[3].define(pin = 21, address = 0x23)
        self.laser[4].define(pin = 18, address = 0x24)
        
        GPIO.setup(10,GPIO.OUT)
        GPIO.setup(9,GPIO.OUT)
        GPIO.output(10,GPIO.LOW)
        GPIO.output(9,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(9,GPIO.HIGH)
    
    def initLASER(self):
        print("Start INIT LASER")
        for i in range(0, 5):
            GPIO.setup(self.laser[i].pin,GPIO.OUT)
            GPIO.output(self.laser[i].pin,GPIO.LOW)
        
        for i in range(0, 5):
            GPIO.output(self.laser[i].pin,GPIO.HIGH)
            time.sleep(0.1)
            try:
                ls = vl6180.VL6180X(i2c)
                ls._write_8(0x212, self.laser[i].address)
                time.sleep(0.1)
                self.laser[i].misura = vl6180.VL6180X(i2c, self.laser[i].address)
            except:
                print("Errore INIT LASER", i)

    def readLASER(self , n):
        try:
            misura = self.laser[n].misura.range
        except:
            misura = -1
        
        if misura < 0:
            try:
                misura = self.laser[n].misura.range
            except:
                misura = -2
                print("Errore Lettura LASER", n)
        return misura
    
    def initBNO(self):
        print("Start INIT BNO")
        try:
            self.bno.misura = BNO055()
            if self.bno.misura.begin() is not True:
                print("Errore begin BNO")
                
            self.bno.misura.setExternalCrystalUse(True)
        except:
            print("Errore INIT BNO")
        
        try:
            c1, c2, c3, c4 = 0,0,0,0
            inizio_cal = time.time()
            while not((c1 > 1 and c2 > 1 ) or (time.time() - inizio_cal) > 20):
                c1, c2, c3, c4 = self.giroscopio.misura.getCalibration()
                time.sleep(0.5)
            print("Fine CALIB BNO")
        except:
            print("Errore CALIB BNO")
            
        try:
            self.bno.current = self.bno.misura.readAngle()
            
            if(self.bno.old[0] == None):
                for i in range(3):
                    self.bno.offset[i] = self.bno.current[i]
            else:
                for i in range(3):
                    self.bno.offset[i] = self.bno.current[i] - self.bno.old[i]
                    
            self.bno.old = [0]*3
        except:
            print("Errore OFFSET BNO")
            
    def readBNO(self):
        
        self.bno.temp = [-1000, -1000, -1000]
        errors = 0
        
        while errors < 5 and (self.bno.temp[0] < 0 or self.bno.temp[0] > 360) and (self.bno.temp[1] < -180 or self.bno.temp[1] > 180):
            errors += 1
            try:
                self.bno.temp = list(self.bno.misura.readAngle())
            except:
                self.bno.temp = [-6969, -6969, -6969]
                
        if self.bno.temp[0] > -999:
            for i in range (3):
                self.bno.old[i] = self.bno.current[i] = self.bno.temp[i] - self.bno.offset[i]
            
            if self.bno.current[0] < 0:
                self.bno.current[0] += 360
            if self.bno.current[0] > 360:
                self.bno.current[0] -= 360
            
            return tuple(self.bno.current)
        else:
            return tuple(self.bno.temp)
    
    def initAPDS(self):
        try:
            self.apds.misura = APDS9960()
            if self.apds.misura.begin() is not True:
                print("Errore begin APDS")
        except:
            print("Errore INIT APDS")
    
    def readAPDS(self):
        try:
            misura = self.apds.misura.range
        except:
            misura = -1
        
        if misura < 0:
            try:
                misura = self.apds.misura.range
            except:
                misura = -2
                print("Errore Lettura APDS")
        return misura
