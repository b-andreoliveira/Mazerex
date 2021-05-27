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

''' set pins for running wheel '''
#mouse A
#set pin inputs from running wheel rotary encoder and initialize variables
dt_A = 12
GPIO.setup(dt_A, GPIO.IN)
dtLastState_A = GPIO.input(dt_A)
wheel_counter_A = 0;
cycle_A = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_A = cycle_A;
turn_A = 0;

#mouse B
#set pin inputs from running wheel rotary encoder and initialize variables
dt_B = 15
GPIO.setup(dt_B, GPIO.IN)
dtLastState_B = GPIO.input(dt_B)
wheel_counter_B = 0;
cycle_B = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_B = cycle_B;
turn_B = 0;

while True:
    
    dtState_A = GPIO.input(dt_A)
    dtState_B = GPIO.input(dt_B)
    
    if dtState_A != dtLastState_A:
        wheel_counter_A += 1
        turn_A = wheel_counter_A/cycle_A
#         print('turn counter A:' + str(turn_A))
        
        if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
            turn_A = wheel_counter_A/cycle_A
            limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
            print("mouse A wheel turns: "+str(turn_A))
        
    if dtState_B != dtLastState_B:
        wheel_counter_B += 1
        turn_B = wheel_counter_B/cycle_B
#         print('turn counter B:' + str(turn_B))
        
        if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
            turn_B = wheel_counter_B/cycle_B
            limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
            print("mouse B wheel turns: "+str(turn_B))
