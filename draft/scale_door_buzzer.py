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
ser.port = '/dev/ttyUSB1' #OpenScale serial port
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

while True:
    
    while MODE == 1:
        ser.close()
        print("\nMODE 1 loop started\n")
        openscale = [] #store weight list
        ser.open()
        ser.flush()
    
        if MODE == 1:
            print("\nMODE 1\n")
            print("animal in social area. put weight (>10g) on scale")
        
            for x in range(1,6):
#                 line_bf = ser.readline()
                print("countdown: " + str(x))
                time.sleep(1)
        
            for x in range (20): #this for loop aims to clean the data input through .decode() and .strip() functions
                #read 20 lines*400ms = 8s of data points
                line_bf = ser.readline() #read input fromOpenScale
                strip_line_bf = line_bf.strip() #gets rid of the tail end of the bytes (\r\n')
                clean_line_bf = strip_line_bf.decode('ascii') #gets rid of the head end of the byt
                value_as_list_bf = clean_line_bf.split(",") #split into a list with two values
                value_str_bf = value_as_list_bf[0] #select first item of list
                m_kg_bf = float(value_str_bf); #convert string to float
                m_g_bf = m_kg_bf*1000 #converts kg to g
                print("\n"); print(m_g_bf); print(type(m_g_bf))
    
                openscale.append(m_g_bf)
        
#             for x in range(20): #this for loop aims to clean the data input through the .split() function
#                 #read 20 lines*400ms = 8s of data points
#                 line_bf = ser.readline()
#                 line_str_bf = str(line_bf)
#                 line_as_list_bf = line_str_bf.split("b'")
#                 value_bf = line_as_list_bf[1]
#                 value_as_list_bf = value_bf.split(",")
#                 mass_g_bf = float(value_as_list_bf[0])*1000
#                 print("\n"); print(mass_g_bf); print(type(mass_g_bf))
#             
#                 openscale.append(mass_g_bf)
            

            
                if m_g_bf > float(10):
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
            
            
                else :
                    print("not enough weight on scale")
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
        
            for x in range(1,6):
                print("countdown: " + str(x))
                time.sleep(1)
        
            for x in range (20):
                line_af = ser.readline() #read input fromOpenScale
                strip_line_af = line_af.strip() #gets rid of the tail end of the bytes (\r\n')
                clean_line_af = strip_line_af.decode('ascii') #gets rid of the head end of the byte
                
                value_as_list_af = clean_line_af.split(",k") #split into a list with two values
                value_str_af = value_as_list_af[0] #select first item of list
                m_kg_af = float(value_str_af); #convert string to float
                m_g_af = m_kg_af*1000 #converts kg to g
                print("\n"); print(m_g_af); print(type(m_g_af))
    
                openscale.append(m_g_af)
            
                if m_g_af > float(10):
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
                
                    
                
                

        
        
    
    
    
    
    
    
    
    
    


