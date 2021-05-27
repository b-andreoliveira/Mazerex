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

# change directory to document data folder
os.chdir("/home/pi/Documents/data/dummy_data")

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
INITIALIZE PARAMETERS AND VARIABES
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
GPIO.setmode(GPIO.BOARD)

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


''' sets pins for sending commands to the FED (Pi --> FED) '''
#mouse A
#set pins for output to FED_A
writeFED_A = 18
GPIO.setup(writeFED_A, GPIO.OUT)
GPIO.output(writeFED_A, False)

#mouse B
#set pins for output to FED_B
writeFED_B = 21
GPIO.setup(writeFED_B, GPIO.OUT)
GPIO.output(writeFED_B, False)

''' set pins for reading input from FED (FED --> Pi) '''
#mouse A
#set pin for input from FED_A
read_FED_A = 16
GPIO.setup(read_FED_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(read_FED_A, GPIO.RISING) #detects rising voltage
pellet_counter_A = 0

#mouse B
#set pin for input from FED_B
read_FED_B = 19
GPIO.setup(read_FED_B, GPIO.IN)
GPIO.add_event_detect(read_FED_B, GPIO.RISING) #detects rising voltage
pellet_counter_B = 0

''' set pins for air puffs '''
#mouse A
airpuff_A = 33
GPIO.setup(airpuff_A, GPIO.OUT)
GPIO.output(airpuff_A, False)

#mouse B
airpuff_B = 35
GPIO.setup(airpuff_B, GPIO.OUT)
GPIO.setup(airpuff_B, False)

'''initialize MODE variable'''
MODE_A = 0
MODE_B = 0


def air_puff(X): #define function for delivering air puff
    
    if X == 'A':
        GPIO.output(airpuff_A, True) #turns air puff ON
        time.sleep(1.5) #waits for 1.5 seconds
        GPIO.output(airpuff_A, False) #turns air puff OFF
        
    elif X == 'B':
        GPIO.output(airpuff_B, True) #turns air puff ON
        time.sleep(1.5)
        GPIO.output(airpuff_B, False) #turns air puff OFF
    
    else:
        print('something wrong. find me: air_puff(X)')
        
    GPIO.output(airpuff_A, False) #turns air puff OFF
    GPIO.output(airpuff_B, False) #turns air puff OFF  #this is to ensure both air puffs are off by the end of the function




while True:
    
    dtState_A = GPIO.input(dt_A) #read input from running wheel
    dtState_B = GPIO.input(dt_B)
    
    if dtState_A != dtLastState_A: 
        wheel_counter_A += 1 #running wheel rotation wheel_counter
        dtLastState_A = dtState_A
        
        if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
            turn_A = wheel_counter_A/cycle_A
            limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
            print("mouse A wheel turns: "+str(turn_A))
            
            if turn_A % 1 == 0 and turn_A != 0: #each 10 revolutions
                print("mouse A completed 10 wheel turns, delivering pellet")
                GPIO.output(writeFED_A, True) #sends output to FED - turnd FED motor on and makes pellet drop
                time.sleep(0.1)
                GPIO.output(writeFED_A, False)
        else:
            pass
    elif dtState_B != dtLastState_B: 
        wheel_counter_B += 1 #running wheel rotation wheel_counter
        dtLastState_B = dtState_B
        
        if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
            turn_B = wheel_counter_B/cycle_B
            limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
            print("mouse B wheel turns: "+str(turn_B))
            
            if turn_B % 1 == 0 and turn_A != 0: #each 10 revolutions
                print("mouse B completed 10 wheel turns, delivering pellet")
                GPIO.output(writeFED_B, True) #sends output to FED - turnd FED motor on and makes pellet drop
                time.sleep(0.1)
                GPIO.output(writeFED_B, False)
        else:
            pass

    elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
        GPIO.output(writeFED_A, False) #turns FED motor off
        air_puff('A') #delivers air puff to animal
        pellet_counter_A += 1 #counts one pellet
        print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
        
    elif GPIO.event_detected(read_FED_B):
        GPIO.output(writeFED_B, False)
        air_puff('B')
        pellet_counter_B += 1
        print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))

