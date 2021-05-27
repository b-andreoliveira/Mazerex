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

''' set serial ports for getting RFID antenna signal '''
#initialize serial port for RFID reader mouse A
RFID_A = serial.Serial()
RFID_A.port = '/dev/ttyS0' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
RFID_A.baudrate = 9600
RFID_A.timeout = 100000 # we do not want the device to timeout
# test device connection
RFID_A.close()
RFID_A.open()
RFID_A.flush()
if RFID_A.is_open==True:
    print("\nRFID reader A ok. Configuration:\n")
    print(RFID_A, "\n") #print serial parameters
RFID_A.close()

#initialize serial port for RFID reader mouse B
RFID_B = serial.Serial()
RFID_B.port = '/dev/ttyAMA1' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
RFID_B.baudrate = 9600
RFID_B.timeout = 100000 # we do not want the device to timeout
# test device connection
RFID_B.close()
RFID_B.open()
RFID_B.flush()
if RFID_B.is_open==True:
    print("\nRFID reader B ok. Configuration:\n")
    print(RFID_B, "\n") #print serial parameters
RFID_B.close()

RFID_A.open()
RFID_A.flush()

RFID_B.open()
RFID_B.flush()

print("GO")
while True:
    
    key = input()
    
#     if key == 'a':
#         
#         for _ in range (10):
#             line_A = RFID_A.readline
#             print(line_A)
#             time.sleep(0.1)
#         
#     elif key == 'b':
#         
#         line_B = RFID_B.readline
#         print(line_B)
    
    
    if key == 'a':
        RFID_A.close()
        RFID_A.open()
        RFID_A.flush()
        
        for _ in range(2): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
            line = RFID_A.readline() #read serial input from RFID antenna
            print("line: "+str(line))
            line_as_str = str(line)
            print("line_as_str: "+line_as_str)
            line_as_list = line_as_str.split(r"b'\x")
            print("line_as_list: "+str(line_as_list))
            dirty_tag = line_as_list[1]
            print("dirty_tag: "+str(dirty_tag))
            tag_as_list = dirty_tag.split("\\r")
            
            dirty_tag_2 = tag_as_list[0] 
            tag_as_list_2 = dirty_tag_2.split("x")
            print('tag_as_list_2: '+ str(tag_as_list_2))
            
            if len(tag_as_list_2) == 1: #this if statement is needed because sometimes the split generates a list with 1 or 2 items
                tag = tag_as_list_2[0] #atfer processing data from RFID antenna, stores it in tag 
            
            else:
                tag = tag_as_list_2[-1] #atfer processing data from RFID antenna, stores it in tag
            print("tag: "+str(tag))
        
            if tag == '020077914A15B9' or tag == '0077914A15B9':
                print("mouse A detected")
                which_mouse = "A"
                ID_tag = "mouse A"
            else:
                print("not mouse A")
        
        RFID_A.close()
    
    elif key == 'b':
        RFID_B.close()
        RFID_B.open()
        RFID_B.flush()
        
        for _ in range(2): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
            line = RFID_B.readline() #read serial input from RFID antenna
            print("line: "+str(line))
            line_as_str = str(line)
            print("line_as_str: "+line_as_str)
            line_as_list = line_as_str.split(r"b'\x")
            print("line_as_list: "+str(line_as_list))
            dirty_tag = line_as_list[1]
            print("dirty_tag: "+str(dirty_tag))
            tag_as_list = dirty_tag.split("\\r")
            
            dirty_tag_2 = tag_as_list[0] 
            tag_as_list_2 = dirty_tag_2.split("x")
            print('tag_as_list_2: '+ str(tag_as_list_2))
            
            if len(tag_as_list_2) == 1: #this if statement is needed because sometimes the split generates a list with 1 or 2 items
                tag = tag_as_list_2[0] #atfer processing data from RFID antenna, stores it in tag 
            
            else:
                tag = tag_as_list_2[-1] #atfer processing data from RFID antenna, stores it in tag
            print("tag: "+str(tag))
            
            if tag == '0200779148D977' or tag == '00779148D977':
                print("mouse B detected")
                which_mouse = "B"
                ID_tag = "mouse B"
            else:
                print("not mouse B")
        
        RFID_B.close()    
    