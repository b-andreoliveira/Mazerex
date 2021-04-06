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
ser.port = '/dev/ttyUSB0' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser.baudrate = 9600
ser.timeout = 100000 # we do not want the device to timeout
# test device connection
ser.close()
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
GPIO.output(Pd1_social, True) #SOCIAL position

#set pin output to buzzer
buzzer = 40
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, False)

MODE = 1

print("about to enter while loop, position should be SOCIAL")
time.sleep(3)

while True: #infinite loop
    
    m_g_af = 0 #set these variables to avoid possible crashes down the line
    m_g_bf = 0
    
    while MODE == 1:
        ser.close()
        print("\nMODE 1 loop started\n")
        openscale = [] #store weight list
        ser.open()
        ser.flush()
    
        if MODE == 1:
            print("\nMODE 1\n")
            print("animal in social area. put weight (>10g) on scale")
        
            for x in range(10,-1, -1):
#                 line_bf = ser.readline()
                print("countdown: " + str(x))
                time.sleep(1)
        
        
            for x in range(20): #this for loop aims to clean the data input through the .split() function
                #read 20 lines*400ms = 8s of data points
                try:    #hsi is to avoid crash if the input from the OpenScale comes in a diferent format (sometiems it does)
                    line_bf = ser.readline()
                    line_str_bf = str(line_bf)
                    if len(line_str_bf) > 18:
                        del line_bf
                        del line_str_bf
                    else:
                        line_as_list_bf = line_str_bf.split("b'")
                        value_bf = line_as_list_bf[1]
                        value_as_list_bf = value_bf.split(",")
                        
#                       if value_as_list_bf[0][-2:] == "kg":
#                           value_as_list_bf[0] = value_as_list_bf[0][:-2]
                        
                        m_g_bf = float(value_as_list_bf[0])*1000
                        print("\n"); print(m_g_bf); print(type(m_g_bf))
                        openscale.append(m_g_bf)
                except:
                    print("wrong input")
            

            
                if m_g_bf > float(10) and MODE == 1:
                    ser.close()
#                     del openscale
                    GPIO.output(Pd1_food, False)
                    GPIO.output(Pd1_social, False) #NEUTRAL position
                    ser.open()
                    ser.flush()
                    time.sleep(5)
                    openscale.append(m_g_bf)
                    GPIO.output(Pd1_food, True)
                    GPIO.output(Pd1_social, False) #FOOD position
                    print("\nMODE 2\n")
                    MODE = 2
            
            
                else:
                    print("MID not enough weight on scale")
                    MODE = 1
                
                break
            
            
    while MODE == 2:
        ser.close()
        print("\nMODE 2 loop started\n")
#         openscale = [] #store weight list
        ser.open()
        ser.flush()
    
        if MODE == 2:
            print("animal in feeding area. put weight (>10g) on scale")
        
            for x in range(10, -1, -1):
                print("countdown: " + str(x))
                time.sleep(1)
        
            for x in range(20): #this for loop aims to clean the data input through the .split() function
                #read 20 lines*400ms = 8s of data points
                try:
                    line_af = ser.readline()
                    line_str_af = str(line_af)
                    if len(line_str_af) > 18:
                        del line_af
                        del line_str_af
                    else:
                        line_as_list_af = line_str_af.split("b'")
                        value_af = line_as_list_af[1]
                        value_as_list_af = value_af.split(",")
                        
#                         if value_as_list_bf[0][-2:] == "kg":
#                             value_as_list_bf[0] = value_as_list_bf[0][:-2]
                        
                        m_g_af = float(value_as_list_af[0])*1000
                        print("\n"); print(m_g_af); print(type(m_g_bf))
                        openscale.append(m_g_af)
                except:
                    print("wrong input")
            
                if m_g_af > float(10) and MODE == 2:
                    ser.close()
#                     del openscale
                    GPIO.output(Pd1_food, False)
                    GPIO.output(Pd1_social, False) #NEUTRAL position
                    ser.open()
                    ser.flush()
                    time.sleep(5)
                    openscale.append(m_g_af)
                
                
                    if m_g_af > m_g_bf:
                        print("heavier than before. initiating buzzer")
                        GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
                        GPIO.output(buzzer, False); time.sleep(0.5)
                        GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
                        GPIO.output(buzzer, False); time.sleep(0.5)
                        GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
                        GPIO.output(buzzer, False); time.sleep(0.5)
                        GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
                        GPIO.output(buzzer, False); time.sleep(0.5)
                        GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
                        GPIO.output(buzzer, False); time.sleep(0.5)
                    
#                         for x in range(20):
#                             GPIO.output(buzzer, True)
#                             time.sleep(0.5)
#                             GPIO.output(buzzer, False)
#                             time.sleep(0.5)
#                             break
                    
                        GPIO.output(Pd1_food, False)
                        GPIO.output(Pd1_social, True) #SOCIAL position
                        print("\nMODE 1\n")
#                         del m_g_bf
#                         del m_g_af
                        MODE = 1
                    
                    else :
                        print("not heavier than before. opening door")
                        GPIO.output(Pd1_food, False)
                        GPIO.output(Pd1_social, True) #SOCIAL position
                        print("\nMODE 1\n")
#                         del m_g_bf
#                         del m_g_af
                        MODE = 1
                        break
                    
                elif m_g_af < float(10):
                    print("END not enought weight on scale.")
                    MODE = 2
                    break
