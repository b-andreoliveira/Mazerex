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
GPIO.output(Pd1_food,False)
GPIO.output(Pd1_social, True)

while True: # infinite loop
    print("\nloop started\n")
    openscale = [] #store weight list
    ser.open()
    ser.flush()
    for x in range(8): # chuck eight lines of garbage 
        line=ser.readline()
        print(line)
    for x in range(20): # read 20lines*400ms=8s of data points
        line=ser.readline()
        print(line)
        # fixing string and converts to float
        line_as_list = line.split(b',')
        m_kg = line_as_list[0]
        m_kg_as_list = m_kg.split(b'\n')
        m_kg_float = float(m_kg_as_list[0])
        m_g = m_kg_float*1000 # kg to g
        openscale.append(m_g) # appends to list
        
        
        if m_g>10:
            ser.close()
            del openscale #why delete openscale?
            GPIO.output(Pd1_food,False)
            GPIO.output(Pd1_social, False)
            time.sleep(5)
            openscale.append(m_g)
            GPIO.output(Pd1_food,True)
            GPIO.output(Pd1_social, False)
            break
        break
    
    for x in range(8): # chuck eight lines of garbage 
        line=ser.readline()
        print(line)
    for x in range(20): # read 20lines*400ms=8s of data points
        line=ser.readline()
        print(line)
        # fixing string and converts to float
        line_as_list = line.split(b',')
        m_kg = line_as_list[0]
        m_kg_as_list = m_kg.split(b'\n')
        m_kg_float = float(m_kg_as_list[0])
        m_g = m_kg_float*1000 # kg to g
        openscale.append(m_g) # appends to list
        
        if m_g>10:
            ser.close()
            #del openscale
            GPIO.output(Pd1_food, False)
            GPIO.output(Pd1_social, False)
            time.sleep(5)
            openscale.append(m_g)
            GPIO.output(Pd1_food, False)
            GPIO.output(Pd1_social, True)
            break
        break
    
        
        
        

