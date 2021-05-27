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

'''set GPIO numbering mode'''
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

''' set pins for IR proximity detectors '''
#mouse A
#set pins for beam break (flying fish) proximity scanner
IR_A = 8
GPIO.setup(IR_A, GPIO.IN)

#mouse B
#set pins for beam break (flying fish) proximity scanner
IR_B = 13
GPIO.setup(IR_B, GPIO.IN)

def animal_in_tube(X): #define function that determine whether animal has entered scale and return boolean
    
    if X == 'A':
        IR_sensor = GPIO.input(IR_A)
    elif X == 'B':
        IR_sensor = GPIO.input(IR_B)
    else:
        print('something wrong. find me: animal_in_tube(X)')
        
    if IR_sensor == 0: #if proximity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned

while True:
    
    proximity_A = animal_in_tube('A')
    proximity_B = animal_in_tube('B')
    
    if proximity_A == True:
        value_A = GPIO.input(IR_A)
        print("A")
        
    if proximity_B == True:
        value_B = GPIO.input(IR_B)
        print("B")
    
    time.sleep(1)
    