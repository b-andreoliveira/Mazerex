import serial
import time
import RPi.GPIO as GPIO
import os
import pandas as pd
import statistics as stats
import time
from datetime import datetime

GPIO.setmode(GPIO.BOARD)
#set pin inputs from running wheel rotary encoder
clk = 37
dt = 38

GPIO.setup(clk,GPIO.IN)
GPIO.setup(dt,GPIO.IN)
clkLastState = GPIO.input(clk)
dtLastState = GPIO.input(dt)

counter = 0;
cycle = 1200; #calibration value
limit = cycle;
turn = 0;

try:  
    while True:
            clkState = GPIO.input(clk)
            dtState = GPIO.input(dt)
            
#             if clkState != clkLastState:
#                 counter += 1
#                 
# #                 print(counter)
#                 clkLastState = clkState
            
            if dtState != dtLastState:
                counter += 1
#                 print(counter)
                dtLastState = dtState
                
            if counter >= limit:
                print(counter)
                turn = counter/cycle
                print(turn)
                limit=counter+cycle              
finally:
    GPIO.cleanup()
