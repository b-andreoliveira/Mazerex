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


now = datetime.now()

print(now)

weights = pd.read_csv("/home/pi/Documents/data/dummy_data/weight.csv", header=None, error_bad_lines=False)

print(weights)

now2 = str(now)
print(now2)
now3 = now2.split(' ')
print(now3)