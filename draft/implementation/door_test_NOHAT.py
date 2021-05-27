#import libraries
import os
import time
import serial
import threading
import pandas as pd
from IOPi import IOPi
import RPi.GPIO as GPIO
import statistics as stats
from datetime import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

''' set door pins '''
#mouse A
PdA_food = 3
PdA_social = 5
GPIO.setup(PdA_food,GPIO.OUT)
GPIO.setup(PdA_social, GPIO.OUT)
GPIO.output(PdA_food,False)
GPIO.output(PdA_social, True) #SOCIAL position

#mouse B
PdB_food = 7
PdB_social = 11
GPIO.setup(PdB_food,GPIO.OUT)
GPIO.setup(PdB_social, GPIO.OUT)
GPIO.output(PdB_food,False)
GPIO.output(PdB_social, True) #SOCIAL position




while True:
    
    GPIO.output(PdA_food, False); GPIO.output(PdA_social, True) #mouse A SOCIAL
    GPIO.output(PdB_food, False); GPIO.output(PdB_social, True) #mouse B SOCIAL
    print('social')
    time.sleep(2)
    GPIO.output(PdA_food, False); GPIO.output(PdA_social, False) #mouse A CLSOED
    GPIO.output(PdB_food, False); GPIO.output(PdB_social, False) #mouse B CLOSED
    print('closed')
    time.sleep(2)
    GPIO.output(PdA_food, True); GPIO.output(PdA_social, False) #mouse A FOOD
    GPIO.output(PdB_food, True); GPIO.output(PdB_social, False) #mouse B FOOD
    print('food')
    time.sleep(2)