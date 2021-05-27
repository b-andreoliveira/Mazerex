#import libraries
import os
import time
import serial
import threading
import pandas as pd
from IOPi import IOPi
import RPi.GPIO as GPIO
import statistics as stats
from datetime import datetime, timedelta

# change directory to document data folder
os.chdir("/home/pi/Documents/data/dummy_data")

weight = pd.read_csv('/home/pi/Documents/data/dummy_data/weight.csv')
pellet = pd.read_csv('/home/pi/Documents/data/dummy_data/pellet.csv')
mouse_ID = ['A', 'B']

weight12h_filt = datetime.now() - timedelta(hours = 12)

pellet3h_filt = datetime.now() - timedelta(hours = 3)



print(weight12h_filt, pellet3h_filt)

filtID_A_weight = (weight['Mouse_ID'] == 'A')
filtID_B_weight = (weight['Mouse_ID'] == 'B')
filtID_A_pellet = (pellet['Mouse_ID'] == 'A')
filtID_B_pellet = (pellet['Mouse_ID'] == 'B')

weight_A = weight.loc[filtID_A_weight]
weight_B = weight.loc[filtID_B_weight]
pellet_A = pellet.loc[filtID_A_pellet]
pellet_B = pellet.loc[filtID_B_pellet]

