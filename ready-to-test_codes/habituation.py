#import libraries
import os
import time
import serial
import threading
import pandas as pd
import RPi.GPIO as GPIO
import statistics as stats
import numpy as np
from datetime import datetime, timedelta

# change directory to document data folder
os.chdir("/home/pi/Documents/data/dummy_data")

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
INITIALIZE PARAMETERS AND VARIABES
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

#set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

#pins mouse A
PdA_food = 7 #pin that send command to Arduino to keep/put door in the food position
PdA_social = 11 #pin that send command to Arduino to keep/put door in the social position
gLED_A = 22 #pin that controls green LED (feedback module)
rLED_A = 24 #pin that controls red LED (feedback module)
buzzer_A = 26 #pin that controls buzzer (feedbaxk module)
dt_A = 12 #pin that counts rotations of the wheel
IR_A = 8 #pin that detects signal from proximity sensor (IR = infrared)
writeFED_A = 18 #pin that sends command to FED (make pellet drop)
read_FED_A = 16 #pin that reads information from FED (if pellet has been retireved or not)
airpuff_A = 33 #pin that controls air puff

#pins mouse B
PdB_food = 13 #pin that send command to Arduino to keep/put door in the food position
PdB_social = 15 #pin that send command to Arduino to keep/put door in the social position
gLED_B = 36 #pin that controls green LED (feedback module)
rLED_B = 32 #pin that controls red LED (feedback module)
buzzer_B = 40 #pin that controls buzzer (feedbaxk module)
dt_B = 19 #pin that counts rotations of the wheel
IR_B = 31 #pin that detects signal from proximity sensor (IR = infrared)
read_FED_B = 21 #pin that sends command to FED (make pellet drop)
writeFED_B = 23 #pin that reads information from FED (if pellet has been retrieved or not)
airpuff_B = 35 #pin that controls air puff

''' configure pins for sending commands to the FED (Pi --> FED) '''
#mouse A
#set pins for output to FED_A
GPIO.setup(writeFED_A, GPIO.OUT) #set pin as output
GPIO.output(writeFED_A, True) #turn pin signal on

#mouse B
#set pins for output to FED_B
GPIO.setup(writeFED_B, GPIO.OUT) #set pin as output
GPIO.output(writeFED_B, True) #turn pin signal on