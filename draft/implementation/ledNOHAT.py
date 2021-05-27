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

readFED_A = 31

GPIO.setup(readFED_A, GPIO.OUT)

while True:
    
    GPIO.output(readFED_A, True)
    time.sleep(1)
    GPIO.output(readFED_A, False)
    time.sleep(1)