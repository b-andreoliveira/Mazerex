#import libraries
import serial
import time
import RPi.GPIO as GPIO
import os
import pandas as pd
from datetime import datetime

# change directory to document data folder
os.chdir("/home/pi/Documents/data/")

#initialize serial port for OpenScale
ser = serial.Serial()
ser.port = '/dev/ttyUSB0' #Arduino serial port
ser.baudrate = 9600
ser.timeout = 100000 # we do not want the device to timeout
# test device connection
ser.open()
ser.flush()
if ser.is_open==True:
    print("\nScale ok. Configuration:\n")
    print(ser, "\n") #print serial parameters
ser.close()

# set GPIO numbering mode
GPIO.setmode(GPIO.BOARD) 
# set pin outputs to arduino
Pd1_food = 16
Pd1_social = 11
GPIO.setup(Pd1_food,GPIO.OUT)
GPIO.setup(Pd1_social, GPIO.OUT)
GPIO.output(Pd1_food, False)
GPIO.output(Pd1_social, False)

print("all set up, starting door")

while True:
    GPIO.output(Pd1_food, False)    #food output LOW
    GPIO.output(Pd1_social, False)  #social output LOW
    time.sleep(5)                   #should stay at NEUTRAL position for 5 seconds
    GPIO.output(Pd1_food, True)     #food output HIGH
    GPIO.output(Pd1_social, False)  #social output LOW
    time.sleep(5)                   #should stay at FOOD position for 5 seconds
    GPIO.output(Pd1_food, False)    #food output LOW
    GPIO.output(Pd1_social, False)  #social output LOW
    time.sleep(5)                   #should stay at NEUTRAL position for 5 seconds
    GPIO.output(Pd1_food, False)    #food output LOW
    GPIO.output(Pd1_social, True)   #social output HIGH
    time.sleep(5)                   #should stay at SOCIAL position for 5 seconds

