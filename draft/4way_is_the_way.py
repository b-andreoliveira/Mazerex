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

'''set GPIO numbering mode'''
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

'''set IOPi buses'''
bus1 = IOPi(0x20)
bus1.set_port_direction(0, 0x00) #sets port 0 (pins 1-8) of IOPi bus 1 as outputs (00 in hex = 00000000 in binary)
bus1.set_port_direction(1, 0x00) #sets port 1 (pins 9-16) of IOPi bus 1 as outputs (00 in hex = 00000000 in binary)
bus1.write_port(0, 0x00) #sets the value of port 0 of IOPi bus 1 as false/low
bus1.write_port(1, 0x00) #sets the value of port 1 of IOPi bus 1 as false/low

bus2 = IOPi(0x21)
bus2.set_port_direction(0, 0xFF) #sets port 0 (pins 1-8) of IOPi bus 2 as inputs (FF in hex = 11111111 in binary)

''' set serial ports for getting OpenScale data '''
#initialize serial port for OpenScale mouse A
ser_A = serial.Serial()
ser_A.port = '/dev/ttyUSB0' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_A.baudrate = 9600
ser_A.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_A.close()
ser_A.open()
ser_A.flush()
if ser_A.is_open==True:
    print("\nScale A ok. Configuration:\n")
    print(ser_A, "\n") #print serial parameters
ser_A.close()

#initialize serial port for OpenScale mouse B
ser_B = serial.Serial()
ser_B.port = '/dev/ttyUSB1' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_B.baudrate = 9600
ser_B.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_B.close()
ser_B.open()
ser_B.flush()
if ser_B.is_open==True:
    print("\nScale B ok. Configuration:\n")
    print(ser_B, "\n") #print serial parameters
ser_B.close()

#initialize serial port for OpenScale mouse C
ser_C = serial.Serial()
ser_C.port = '/dev/ttyUSB2' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_C.baudrate = 9600
ser_C.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_C.close()
ser_C.open()
ser_C.flush()
if ser_C.is_open==True:
    print("\nScale C ok. Configuration:\n")
    print(ser_C, "\n") #print serial parameters
ser_C.close()

#initialize serial port for OpenScale mouse D
ser_D.port = '/dev/ttyUSB3' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_D.baudrate = 9600
ser_D.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_D.close()
ser_D.open()
ser_D.flush()
if ser_D.is_open==True:
    print("\nScale D ok. Configuration:\n")
    print(ser_D, "\n") #print serial parameters
ser_D.close()


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
RFID_B.port = '/dev/ttySOFT0' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
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

#initialize serial port for RFID reader mouse C
RFID_C = serial.Serial()
RFID_C.port = '/dev/ttyAMA1' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
RFID_C.baudrate = 9600
RFID_C.timeout = 100000 # we do not want the device to timeout
# test device connection
RFID_C.close()
RFID_C.open()
RFID_C.flush()
if RFID_C.is_open==True:
    print("\nRFID reader C ok. Configuration:\n")
    print(RFID_C, "\n") #print serial parameters
RFID_C.close()

#initialize serial port for RFID reader mouse D
RFID_D = serial.Serial()
RFID_D.port = '/dev/ttyAMA2' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
RFID_D.baudrate = 9600
RFID_D.timeout = 100000 # we do not want the device to timeout
# test device connection
RFID_D.close()
RFID_D.open()
RFID_D.flush()
if RFID_D.is_open==True:
    print("\nRFID reader D ok. Configuration:\n")
    print(RFID_D, "\n") #print serial parameters
RFID_D.close()

''' set door pins '''
#mouse A
bus1.set_pin_direction (2, 0) #sets pin 2 of bus 1 as output
PdA_food_ON = bus1.write_pin(2, 1)
PdA_food_OFF = bus1.write_pin(2, 0)

bus1.set_pin_direction(4, 0) #sets pin 4 of bus 1 as output
PdA_social_ON = bus1.write_pin(4, 1)
PdA_social_OFF = bus1.write_pin(4, 0)

#mouse B
bus1.set_pin_direction(6, 0) #sets pin 6 of bus 1 as output
PdB_food_ON = bus1.write_pin(6, 1)
PdB_food_OFF = bus1.write_pin(6, 0)

bus1.set_pin_direction(8, 0) #sets pin 8 of bus 1 as output
PdB_social_ON = bus1.write_pin(8, 1)
PdB_social_OFF = bus1.write_pin(8, 0)

#mouse C
bus1.set_pin_direction(10, 0) #sets pin 10 of bus 1 as output
PdC_food_ON = bus1.write_pin(10, 1)
PdC_food_OFF = bus1.write_pin(10, 0)

bus1.set_pin_direction(12, 0) #sets pin 12 of bus 1 as output
PdC_social_ON = bus1.write_pin(12, 1)
PdC_social_OFF = bus1.write_pin(12, 0)

#mouse D
bus1.set_pin_direction(14, 0) #sets pin 14 of bus 1 as output
PdD_food_ON = bus1.write_pin(14, 1)
PdD_food_OFF = bus1.write_pin(14, 0)

bus1.set_pin_direction(16, 0) #sets pin 16 of bus 1 as output
PdD_social_ON = bus1.write_pin(16, 1)
PdD_social_OFF = bus1.write_pin(16, 0)

''' set scale buzzers and LEDs '''
#buzzer tones
heavier_buzz_1 = 700
heavier_buzz_2 = 589
not_heavier_buzz_1 = 131
not_heavier_buzz_2 = 165

#mouse A
#set pin output to buzzer and LEDs
buzzer_A = 12
GPIO.setup(buzzer_A, GPIO.OUT)
buzz_A = GPIO.PWM(buzzer_A, 1) #starting frequency is 1 (inaudible)

bus2.set_pin_direction(9, 0) #output
greenLED_A_ON = bus2.write_pin(9, 1)
greenLED_A_OFF = bus2.write_pin(9, 0)
greenLED_A_OFF; bus2.write_pin(9, 0) #double check if both operations are needed (they do the same)

bus2.set_pin_direction(11, 0)
redLED_A_ON = bus2.write_pin(11, 1)
redLED_A_OFF = bus2.write_pin(11, 0)
redLED_A_OFF; bus2.write_pin(11, 0) #double check if both operations are needed (they do the same)

#mouse B
#set pin output to buzzer and LEDs
buzzer_B = 32
GPIO.setup(buzzer_B, GPIO.OUT)
buzz_B = GPIO.PWM(buzzer_B, 1)

bus2.set_pin_direction(13, 0) #output
greenLED_B_ON = bus2.write_pin(13, 1)
greenLED_B_OFF = bus2.write_pin(13, 0)
greenLED_B_OFF; bus2.write_pin(13, 0) #double check if both operations are needed (they do the same)

bus2.set_pin_direction(15, 0)
redLED_B_ON = bus2.write_pin(15, 1)
redLED_B_OFF = bus2.write_pin(15, 0)
redLED_B_OFF; bus2.write_pin(15, 0) #double check if both operations are needed (they do the same)

#mouse C
#set pin output to buzzer and LEDs
buzzer_C = 33
GPIO.setup(buzzer_C, GPIO.OUT)
buzz_C = GPIO.PWM(buzzer_C, 1)

bus2.set_pin_direction(10, 0) #output
greenLED_C_ON = bus2.write_pin(10, 1)
greenLED_C_OFF = bus2.write_pin(10, 0)
greenLED_C_OFF; bus2.write_pin(10, 0) #double check if both operations are needed (they do the same)

bus2.set_pin_direction(12, 0)
redLED_C_ON = bus2.write_pin(12, 1)
redLED_C_OFF = bus2.write_pin(12, 0)
redLED_C_OFF; bus2.write_pin(12, 0) #double check if both operations are needed (they do the same)

#mouse D
#set pin output to buzzer and LEDs
buzzer_D = 35
GPIO.setup(buzzer_D, GPIO.OUT)
buzz_D = GPIO.PWM(buzzer_C, 1)

bus2.set_pin_direction(14, 0) #output
greenLED_D_ON = bus2.write_pin(14, 1)
greenLED_D_OFF = bus2.write_pin(14, 0)
greenLED_D_OFF; bus2.write_pin(14, 0) #double check if both operations are needed (they do the same)

bus2.set_pin_direction(16, 0)
redLED_D_ON = bus2.write_pin(16, 1)
redLED_D_OFF = bus2.write_pin(16, 0)
redLED_D_OFF; bus2.write_pin(16, 0) #double check if both operations are needed (they do the same)

''' set pins for running wheel '''
#mouse A
#set pin inputs from running wheel rotary encoder and initialize variables
bus2.set_pin_direction(1, 1) #sets pin 1 (bus 2) of IOPi as input
dt_A = bus2.read_pin(1)
dtLastState_A = bus2.read_pin(1)

wheel_counter_A = 0;
cycle_A = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_A = cycle_A;
turn_A = 0;

#mouse B
#set pin inputs from running wheel rotary encoder and initialize variables
bus2.set_pin_direction(3, 1) #sets pin 3 (bus 2) of IOPi as input
dt_B = bus2.read_pin(3)
dtLastState_B = bus2.read_pin(3)

wheel_counter_B = 0;
cycle_B = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_B = cycle_B;
turn_B = 0;

#mouse C
#set pin inputs from running wheel rotary encoder and initialize variables
bus2.set_pin_direction(5, 1) #sets pin 5 (bus 2) of IOPi as input
dt_C = bus2.read_pin(5)
dtLastState_C = bus2.read_pin(5)

wheel_counter_C = 0;
cycle_C = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_C = cycle_C;
turn_C = 0;

#mouse D
#set pin inputs from running wheel rotary encoder and initialize variables
bus2.set_pin_direction(7, 1) #sets pin 7 (bus 2) of IOPi as input
dt_D = bus2.read_pin(7)
dtLastState_D = bus2.read_pin(7)

wheel_counter_D = 0;
cycle_D = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_D = cycle_D;
turn_D = 0;

''' set pins for IR proximity detectors '''
#mouse A
#set pins (bus1 IOPi) for beam break (flying fish) proximity scanner
bus2.set_pin_direction(2, 1) #(pin, direction) #sets pin 2 on bus 2 as an input pin (1 = input, 0 = output)
bus2.set_pin_pullup(2, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
proximity_sensor_A = bus2.read_pin(2) #reads pin 2 (bus 2) of the IOPi as the sensor pin for the proximity sensor

#mouse B
bus2.set_pin_direction(4, 1) #(pin, direction) #sets pin 4 on bus 2 to as an input pin (1 = input, 0 = output)
bus2.set_pin_pullup(4, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
proximit_sensor_B = bus2.read_pin(4) #reads pin 4 (bus 2) of the IOPi as the sensor pin for the proximity sensor

#mouse C
#set pins (bus1 IOPi) for beam break (flying fish) proximity scanner
bus2.set_pin_direction(6, 1) #(pin, direction) #sets pin 6 on bus 2 as an input pin (1 = input, 0 = output)
bus2.set_pin_pullup(6, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
proximity_sensor_C = bus2.read_pin(6) #reads pin 6 (bus 2) of the IOPi as the sensor pin for the proximity sensor

#mouse B
bus2.set_pin_direction(8, 1) #(pin, direction) #sets pin 8 on bus 2 to as an input pin (1 = input, 0 = output)
bus2.set_pin_pullup(8, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
proximit_sensor_D = bus2.read_pin(8) #reads pin 4 (bus 2) of the IOPi as the sensor pin for the proximity sensor

''' sets pins for sending commands to the FED (Pi --> FED) '''
#mouse A
#set pins (bus1 IOPi) for output to FED_A
bus1.set_pin_direction(1, 0) #output
FED_A_OFF = bus1.write_pin(1, 0) #sets pin 1 as low
FED_A_ON = bus1.write_pin(1, 1) #sets pin 1 as high
FED_A_OFF; bus1.write_pin(1, 0) #check if both commands are necessary (in theory they do the same)

#mouse B
#set pins (bus1 IOPi) for output to FED_B
bus1.set_pin_direction(3, 0) #output
FED_B_OFF = bus1.write_pin(3, 0) #sets pin 1 as low
FED_B_ON = bus1.write_pin(3, 1) #sets pin 1 as high
FED_B_OFF; bus1.write_pin(3, 0) #check if both commands are necessary (in theory they do the same)

#mouse C
#set pins (bus1 IOPi) for output to FED_C
bus1.set_pin_direction(5, 0) #output
FED_C_OFF = bus1.write_pin(5, 0) #sets pin 1 as low
FED_C_ON = bus1.write_pin(5, 1) #sets pin 1 as high
FED_C_OFF; bus1.write_pin(5, 0) #check if both commands are necessary (in theory they do the same)

#mouse D
#set pins (bus1 IOPi) for output to FED_D
bus1.set_pin_direction(7, 0) #output
FED_D_OFF = bus1.write_pin(7, 0) #sets pin 1 as low
FED_D_ON = bus1.write_pin(7, 1) #sets pin 1 as high
FED_D_OFF; bus1.write_pin(7, 0) #check if both commands are necessary (in theory they do the same)

''' set pins for reading input from FED (FED --> Pi) '''
#mouse A
#set pin for input from FED_A
read_FED_A = 22
GPIO.setup(read_FED_A, GPIO.IN)
GPIO.add_event_detect(read_FED_A, GPIO.RISING) #detects rising voltage
pellet_counter_A = 0

#mouse B
#set pin for input from FED_B
read_FED_B = 36
GPIO.setup(read_FED_B, GPIO.IN)
GPIO.add_event_detect(read_FED_B, GPIO.RISING) #detects rising volatge
pellet_counter_B = 0

#mouse C
#set pin for input from FED_A
read_FED_C = 38
GPIO.setup(read_FED_C, GPIO.IN)
GPIO.add_event_detect(read_FED_C, GPIO.RISING) #detects rising voltage
pellet_counter_C = 0

#mouse D
#set pin for input from FED_D
read_FED_D = 40
GPIO.setup(read_FED_D, GPIO.IN)
GPIO.add_event_detect(read_FED_D, GPIO.RISING) #detects rising volatge
pellet_counter_D = 0

''' set pins for air puffs '''
#mouse A
bus1.set_pin_direction(9, 0) #pin 9 (bus 1) as output
air_puff_A_OFF = bus1.write_pin(9, 0) #set pin 9 to low/false
air_puff_A_ON = bus1.write_pin(9, 1) #set pin 9 to high/true
bus1.write_pin(9, 0)

#mouse B
bus1.set_pin_direction(11, 0) #pin 11 (bus 1) as output
air_puff_B_OFF = bus1.write_pin(11, 0) #set pin 11 to low/false
air_puff_B_ON = bus1.write_pin(11, 1) #set pin 11 to high/true
bus1.write_pin(11, 0)

#mouse C
bus1.set_pin_direction(13, 0) #pin 13 (bus 1) as output
air_puff_C_OFF = bus1.write_pin(13, 0) #set pin 9 to low/false
air_puff_C_ON = bus1.write_pin(13, 1) #set pin 9 to high/true
bus1.write_pin(13, 0)

#mouse D
bus1.set_pin_direction(15, 0) #pin 11 (bus 1) as output
air_puff_D_OFF = bus1.write_pin(15, 0) #set pin 11 to low/false
air_puff_D_ON = bus1.write_pin(15, 1) #set pin 11 to high/true
bus1.write_pin(15, 0)

'''initialize MODE variable'''
MODE_A = 0
MODE_B = 0
MODE_C = 0
MODE_D = 0

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
DEFINE FUNCTIONS TO BE USED IN THE CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

'''
GENERAL FUNCTIONS ########################################################################################
'''

def countdown():#define countdown function (for testing only)
    for x in range(5,-1, -1):
        print("countdown: " + str(x))
        time.sleep(1)
        
def move_door_social(X):#define function for seting door at social position
    
    if X == 'A':
        PdA_food_OFF = bus1.write_pin(2, 0)
        PdA_social_ON = bus1.write_pin(4, 1)
        PdA_food_OFF; PdA_social_ON #SOCIAL position
    
    elif X == 'B':
        PdB_food_OFF = bus1.write_pin(6, 0)
        PdB_social_ON = bus1.write_pin(8, 1)
        PdB_food_OFF; PdB_social_ON #SOCIAL position
        
    elif X == 'C':
        PdC_food_OFF = bus1.write_pin(10, 0)
        PdC_social_ON = bus1.write_pin(12, 1)
        PdC_food_OFF; PdC_social_ON #SOCIAL position
    
    elif X == 'D':
        PdD_food_OFF = bus1.write_pin(14, 0)
        PdD_social_ON = bus1.write_pin(16, 1)
        PdD_food_OFF; PdD_social_ON #SOCIAL position

def move_door_feeding(X):#define function for seting door at feeding position
    
    if X == 'A': 
        PdA_food_ON = bus1.write_pin(2, 1)
        PdA_social_OFF = bus1.write_pin(4, 0)
        PdA_food_ON; PdA_social_OFF #FEEDING position
    
    elif X == 'B':
        PdB_food_ON = bus1.write_pin(6, 1)
        PdB_social_OFF = bus1.write_pin(8, 0)
        PdB_food_ON; PdB_social_OFF #FEEDING position
        
    elif X == 'C':
        PdC_food_ON = bus1.write_pin(10, 1)
        PdC_social_OFF = bus1.write_pin(12, 0)
        PdC_food_ON; PdC_social_OFF #FEEDING position
        
    elif X == 'D':
        PdD_food_ON = bus1.write_pin(14, 1)
        PdD_social_OFF = bus1.write_pin(16, 0)
        PdD_food_ON; PdD_social_OFF #FEEDING position

def move_door_close(X):#define function for seting door at neutral position
    
    if X == 'A':
        PdA_food_OFF = bus1.write_pin(2, 0)
        PdA_social_OFF = bus1.write_pin(4, 0)
        PdA_food_OFF; PdA_social_OFF #NEUTRAL position
    
    elif X == 'B':
        PdB_food_OFF = bus1.write_pin(6, 0)
        PdB_social_OFF = bus1.write_pin(8, 0)
        PdB_food_OFF; PdB_social_OFF #NEUTRAL position
        
    elif X == 'C':
        PdC_food_OFF = bus1.write_pin(10, 0)
        PdC_social_OFF = bus1.write_pin(12, 0)
        PdC_food_OFF; PdC_social_OFF #NEUTRAL position
        
    elif X == 'D':
        PdD_fod_OFF = bus1.write_pin(14, 0)
        PdD_social_OFF = bus1.write_pin(16, 0)
        PdD_food_OFF; PdD_social_OFF #NEUTRAL position

def animal_in_tube(X): #define function that determine whether animal has entered scale and return boolean
    
    if X == 'A':
        IR_sensor = bus2.read_pin(2)
    elif X == 'B':
        IR_sensor = bus2.read_pin(4)
    elif X == 'C':
        IR_sensor = bus2.read_pin(6)
    elif X == 'D':
        IR_sensor = bus2.read_pin(8)
    else:
        print('something wrong. find me: animal_in_tube(X)')
        
    if IR_sensor == 0: #if proximity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned
    
def append_weight(mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode): #define function for storing weight data
    
    weight_list = {  #make dictionary to store variable values
    "Mouse_ID" : [],
    "Weight_Mean": [],
    "Weight_Median": [],
    "Weight_Mode": [],
    "Weight_Max_Mode": [],
    "Date_Time": []
    }
    
    weight_list.update({'Mouse_ID' : [mouse]}) #update dictionary about which mouse is being weighted
    weight_list.update({'Weight_Mean': [weight_data_mean]}) #update dictionary weight mean value
    weight_list.update({'Weight_Median': [weight_data_median]}) #update dictionary weight median value
    weight_list.update({'Weight_Mode': [weight_data_mode]}) #update dictionary weight mode value
    weight_list.update({'Weight_Max_Mode': [weight_data_max_mode]}) #update dictionary weight max mode value
    weight_list.update({'Date_Time': [datetime.now()]}) #update dictionary date and time of measurement
        
    df_w = pd.DataFrame(weight_list) #transform into dataframe
    print(df_w)

    if not os.path.isfile("weight.csv"):
        df_w.to_csv("weight.csv", encoding="utf-8-sig", index=False)
    else:
        df_w.to_csv("weight.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

'''
MODE 0 FUNCTIONS ########################################################################################
'''

def RFID_check(X): #define function to check ID of the animal
    
    if X == 'A':
        RFID_A.close()
        RFID_A.open()
        RFID_A.flush()
        
        for _ in range(5): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
            line = RFID_A.readline() #read serial input from RFID antenna
            line_as_str = str(line)
            line_as_list = line_as_str.split(r"b'\x")
            dirty_tag = line_as_list[1]
            tag_as_list = dirty_tag.split("\\r")
            
            dirty_tag_2 = tag_as_list[0] 
            tag_as_list_2 = dirty_tag_2.split("x")
            
            if len(tag_as_list_2) == 1: #this if statement is needed because sometimes the split generates a list with 1 or 2 items
                tag = tag_as_list_2[0] #atfer processing data from RFID antenna, stores it in tag 
            
            else:
                tag = tag_as_list_2_A[1] #atfer processing data from RFID antenna, stores it in tag
        
            if tag == '020077914A15B9' or tag == '0077914A15B9':
                print("mouse A detected")
                which_mouse = "A"
                ID_tag = "mouse A"
                append_RFID(which_mouse, tag)
                return True
            else:
                print("not mouse A")
                return False
        
        RFID_A.close()
    
    elif X == 'B':
        RFID_B.close()
        RFID_B.open()
        RFID_B.flush()
        
        for _ in range(5): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
            line = RFID_B.readline() #read serial input from RFID antenna
            line_as_str = str(line)
            line_as_list = line_as_str.split(r"b'\x")
            dirty_tag = line_as_list[1]
            tag_as_list = dirty_tag.split("\\r")
            
            dirty_tag_2 = tag_as_list[0] 
            tag_as_list_2 = dirty_tag_2.split("x")
            
            if len(tag_as_list_2) == 1: #this if statement is needed because sometimes the split generates a list with 1 or 2 items
                tag = tag_as_list_2[0] #atfer processing data from RFID antenna, stores it in tag
                
            else:
                tag = tag_as_list_2[1] #atfer processing data from RFID antenna, stores it in tag
            
            if tag == '0200779148D977' or tag == '00779148D977':
                print("mouse B detected")
                which_mouse = "B"
                ID_tag = "mouse B"
                append_RFID(which_mouse, tag)
                return True
            else:
                print("not mouse B")
                return False
        
        RFID_B.close()

    elif X == 'C':
        RFID_C.close()
        RFID_C.open()
        RFID_C.flush()
        
        for _ in range(5): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
            line = RFID_C.readline() #read serial input from RFID antenna
            line_as_str = str(line)
            line_as_list = line_as_str.split(r"b'\x")
            dirty_tag = line_as_list[1]
            tag_as_list = dirty_tag.split("\\r")
            
            dirty_tag_2 = tag_as_list[0] 
            tag_as_list_2 = dirty_tag_2.split("x")
            
            if len(tag_as_list_2) == 1: #this if statement is needed because sometimes the split generates a list with 1 or 2 items
                tag = tag_as_list_2[0] #atfer processing data from RFID antenna, stores it in tag
                
            else:
                tag = tag_as_list_2[1] #atfer processing data from RFID antenna, stores it in tag
            
            if tag == '0200779149E14E' or tag == '00779149E14E':
                print("mouse C detected")
                which_mouse = "C"
                ID_tag = "mouse C"
                append_RFID(which_mouse, tag)
                return True
            else:
                print("not mouse C")
                return False
        
        RFID_C.close()
        
    elif X == 'D':
        RFID_D.close()
        RFID_D.open()
        RFID_D.flush()
        
        for _ in range(5): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
            line = RFID_D.readline() #read serial input from RFID antenna
            line_as_str = str(line)
            line_as_list = line_as_str.split(r"b'\x")
            dirty_tag = line_as_list[1]
            tag_as_list = dirty_tag.split("\\r")
            
            dirty_tag_2 = tag_as_list[0] 
            tag_as_list_2 = dirty_tag_2.split("x")
            
            if len(tag_as_list_2) == 1: #this if statement is needed because sometimes the split generates a list with 1 or 2 items
                tag = tag_as_list_2[0] #atfer processing data from RFID antenna, stores it in tag
                
            else:
                tag = tag_as_list_2[1] #atfer processing data from RFID antenna, stores it in tag
            
            if tag == 'XXXXXXXX' or tag == 'XXXXXXXX': #PUT HERE ACTUAL TAG D VALUE
                print("mouse D detected")
                which_mouse = "D"
                ID_tag = "mouse D"
                append_RFID(which_mouse, tag)
                return True
            else:
                print("not mouse D")
                return False
        
            RFID_D.close()
    
    else:
        print('something wrong. find me: RFID_check(X)')
        
def append_RFID(which_mouse, tag): #define function  to save which animal was detected and when
    
    RFID_list = {
        "Mouse" : [],
        "RFID_tag" : [],
        "Date_Time" : []
        }
    
    RFID_list.update({"Mouse" : [which_mouse]})
    RFID_list.update({"RFID_tag" : [tag]})
    RFID_list.update({"Date_Time" : [datetime.now()]})
    
    df_rfid = pd.DataFrame(RFID_list)
    print(df_rfid)
    
    if not os.path.isfile("rfid_tag.csv"):
        df_rfid.to_csv("rfid_tag.csv", encoding="utf-8-sig", index=False)
    else:
        df_rfid.to_csv("rfid_tag.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

def scan_tube_entry(X): #define function to check wether there is only one animal in scale
    animal_enter = False
    animal_alone = False
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        
        for _ in range(8):
            line = ser_A.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            
            if mg > float(10) and mg < float(30):
                print("scale scan: 1 animal on scale.")
                return True
                animal_enter = True
                animal_alone = True
                ser_A.close()
            elif mg >= float(30):
                print("more than one animal on scale, restarting")
                return False
                animal_enter = True
                animal_alone = False
            else:
                return False
                animal_enter = False
                animal_alone = False
        
    elif X == 'B':
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        
        for _ in range(8):
            line = ser_B.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            print(mg)
            
            if mg > float(10) and mg < float(30):
                print("scale scan: 1 animal on scale.")
                return True
                animal_enter = True
                animal_alone = True
                ser_B.close()
            elif mg >= float(30):
                print("more than one animal on scale, restarting")
                return False
                animal_enter = True
                animal_alone = False
            else:
                return False
                animal_enter = False
                animal_alone = False

    elif X == 'C':
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        
        for _ in range(8):
            line = ser_C.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_C.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            print(mg)
            
            if mg > float(10) and mg < float(30):
                print("scale scan: 1 animal on scale.")
                return True
                animal_enter = True
                animal_alone = True
                ser_C.close()
            elif mg >= float(30):
                print("more than one animal on scale, restarting")
                return False
                animal_enter = True
                animal_alone = False
            else:
                return False
                animal_enter = False
                animal_alone = False
                
    elif X == 'D':
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        
        for _ in range(8):
            line = ser_D.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_D.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            print(mg)
            
            if mg > float(10) and mg < float(30):
                print("scale scan: 1 animal on scale.")
                return True
                animal_enter = True
                animal_alone = True
                ser_D.close()
            elif mg >= float(30):
                print("more than one animal on scale, restarting")
                return False
                animal_enter = True
                animal_alone = False
            else:
                return False
                animal_enter = False
                animal_alone = False
    else:
        print('something wrong. find me: scan_tube_entry(X)')
        
        
'''
MODE 1 FUNCTIONS ########################################################################################
'''

def acquire_weight_pre(X): #define function to acquire and sotre weight data
    
    if X == 'A':
        print("acquiring weight PRE - mouse A")
        openscale = [] #store weights here
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(8): # chuck two lines 
            line = ser_A.readline()   
        for x in range(100): # 100 lines*120ms per line=12s of data 
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_pre = relProb_float*1000
            openscale.append(mg_pre)
            print("mouse A weight in grams PRE: "+str(mg_pre))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #mouse ID
            mouse = 'A'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
            # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
                
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
        print("mouse A weight data saved. opening door.")
        ser_A.close()
        return weight_data_mean
        
    elif X == 'B':
        print("acquiring weight PRE - mouse B")
        openscale = [] #store weights here
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        for _ in range(8): # chuck two lines 
            line = ser_B.readline()   
        for x in range(10): # 100 lines*120ms per line=12s of data
            ''' RANGE 10 HERE BECAUSE OPSEN SCALE 2 IS REPORTING TOO SLOWLY! CHANGE BACK TO 100 WHEN THAT'S FIXED'''
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_pre = relProb_float*1000
            openscale.append(mg_pre)
            print("mouse B weight in grams PRE: "+str(mg_pre))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #mouse ID
            mouse = 'B'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
            # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
                
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
        print("mouse B weight data saved. opening door.")
        ser_B.close()
        return weight_data_mean

    elif X == 'C':
        print("acquiring weight PRE - mouse C")
        openscale = [] #store weights here
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        for _ in range(8): # chuck two lines 
            line = ser_C.readline()   
        for x in range(100): # 100 lines*120ms per line=12s of data 
            line = ser_C.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_pre = relProb_float*1000
            openscale.append(mg_pre)
            print("mouse C weight in grams PRE: "+str(mg_pre))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #mouse ID
            mouse = 'A'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
            # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
                
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
        print("mouse C weight data saved. opening door.")
        ser_C.close()
        return weight_data_mean
    
    elif X == 'D':
        print("acquiring weight PRE - mouse D")
        openscale = [] #store weights here
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        for _ in range(8): # chuck two lines 
            line = ser_D.readline()   
        for x in range(100): # 100 lines*120ms per line=12s of data 
            line = ser_D.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_pre = relProb_float*1000
            openscale.append(mg_pre)
            print("mouse D weight in grams PRE: "+str(mg_pre))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #mouse ID
            mouse = 'D'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
            # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
                
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
        print("mouse D weight data saved. opening door.")
        ser_D.close()
        return weight_data_mean    

    else:
        print('something wrong. find me: acquire_weight_pre(X)')
        
def wait_for_animal_to_leave_foor_feeding_area(X): #define function for determining if animal has left the tube
    
    animal_out = False
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        
        for _ in range(8):
            line = ser_A.readline()
        
        while animal_out == False:
                    
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
        
            if mg < float(5):
                animal_out = True
                print("mouse A left for feeding area")
                ser_A.close()
                return 2 #return value to be assigned to MODE_A
            else:
                animal_out = False
                return 1       
        
    elif X == 'B':
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        
        for _ in range(8):
            line = ser_B.readline()
        
        while animal_out == False:
                    
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
        
            if mg < float(5):
                animal_out = True
                print("mouse B left for feeding area")
                ser_B.close()
                return 2 #return value to be assigned to MODE_A
            else:
                animal_out = False
                return 1 
    
    elif X == 'C':
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        
        for _ in range(8):
            line = ser_C.readline()
        
        while animal_out == False:
                    
            line = ser_C.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
        
            if mg < float(5):
                animal_out = True
                print("mouse B left for feeding area")
                ser_C.close()
                return 2 #return value to be assigned to MODE_A
            else:
                animal_out = False
                return 1 
    
    elif X == 'D':
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        
        for _ in range(8):
            line = ser_D.readline()
        
        while animal_out == False:
                    
            line = ser_D.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
        
            if mg < float(5):
                animal_out = True
                print("mouse D left for feeding area")
                ser_D.close()
                return 2 #return value to be assigned to MODE_A
            else:
                animal_out = False
                return 1
            
    else:
        print('something wrong. find me: wait_for_animal_to_leave_foor_feeding_area(X)')

'''
MODE 2 FUNCTIONS ########################################################################################
'''

def acquire_weight_post(X): #define function to acquire and save weight data
    
    if X == 'A':
        openscale = [] #store weights here
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(8): # chuck two lines 
            line = ser_A.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data 
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_post = relProb_float*1000
            openscale.append(mg_post)
            print("mouse A weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #ID
            mouse = 'A'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
           # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
            
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                      weight_data_mode, weight_data_max_mode)
        
        #define variables for comaprison with if clause in the next functuion
        mg_post_mean = weight_data_mean
        mg_post_median = weight_data_median
        
        # change mode and clean up
        del openscale
        ser_A.close()
        
        #return values for comparison
        return mg_post_mean
        
    elif X == 'B':
        openscale = [] #store weights here
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        for _ in range(8): # chuck two lines 
            line = ser_B.readline()
        
        for x in range(10): # 100 lines*120ms per line=12s of data
            ''' RANGE 10 HERE BECAUSE OPSEN SCALE 2 IS REPORTING TOO SLOWLY! CHANGE BACK TO 100 WHEN THAT'S FIXED'''
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_post = relProb_float*1000
            openscale.append(mg_post)
            print("mouse B weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #ID
            mouse = 'B'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
           # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
            
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                      weight_data_mode, weight_data_max_mode)
        
        #define variables for comaprison with if clause in the next functuion
        mg_post_mean = weight_data_mean
        mg_post_median = weight_data_median
        
        # change mode and clean up
        del openscale
        ser_B.close()
        
        #return values for comparison
        return mg_post_mean
        
    elif X == 'C':
        openscale = [] #store weights here
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        for _ in range(8): # chuck two lines 
            line = ser_C.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data
            line = ser_C.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_post = relProb_float*1000
            openscale.append(mg_post)
            print("mouse C weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #ID
            mouse = 'C'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
           # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
            
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                      weight_data_mode, weight_data_max_mode)
        
        #define variables for comaprison with if clause in the next functuion
        mg_post_mean = weight_data_mean
        mg_post_median = weight_data_median
        
        # change mode and clean up
        del openscale
        ser_C.close()
        
        #return values for comparison
        return mg_post_mean
    
    elif X == 'D':
        openscale = [] #store weights here
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        for _ in range(8): # chuck two lines 
            line = ser_D.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data
            line = ser_D.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_post = relProb_float*1000
            openscale.append(mg_post)
            print("mouse C weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            #ID
            mouse = 'D'
            # mean 
            weight_data_mean = stats.mean(openscale)
            # median
            weight_data_median = stats.median(openscale)
           # mode
            try:
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
            
            # mode max TO DO
            try:
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, weight_data_mean, weight_data_median,
                      weight_data_mode, weight_data_max_mode)
        
        #define variables for comaprison with if clause in the next functuion
        mg_post_mean = weight_data_mean
        mg_post_median = weight_data_median
        
        # change mode and clean up
        del openscale
        ser_D.close()
        
        #return values for comparison
        return mg_post_mean
    
    else:
        print('something wrong. find me: acquire_weight_post(X)')

def check_weight_post_A(mg_pre_mean_A, mg_post_mean_A): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_A > mg_pre_mean_A:
        print("mouse A is heavier than before. initializing buzzer")
        bad_buzz('A')
        air_puff('A')
        
    else:
        print("mouse A is not havier than before. opening door")
        good_buzz('A')
    
    bus1.write_pin(9, 0) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function
        
def check_weight_post_B(mg_pre_mean_B, mg_post_mean_B): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_B > mg_pre_mean_B:
        print("mouse B is heavier than before. initializing buzzer")
        bad_buzz('B')
        air_puff('B')
        
    else:
        print("mouse B is not havier than before. opening door")
        good_buzz('B')
    
    bus1.write_pin(11, 0) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function

def check_weight_post_C(mg_pre_mean_C, mg_post_mean_C): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_C > mg_pre_mean_C:
        print("mouse C is heavier than before. initializing buzzer")
        bad_buzz('C')
        air_puff('C')
        
    else:
        print("mouse C is not havier than before. opening door")
        good_buzz('C')
    
    bus1.write_pin(13, 0) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function

def check_weight_post_D(mg_pre_mean_D, mg_post_mean_D): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_D > mg_pre_mean_D:
        print("mouse D is heavier than before. initializing buzzer")
        bad_buzz('D')
        air_puff('D')
        
    else:
        print("mouse D is not havier than before. opening door")
        good_buzz('D')
    
    bus1.write_pin(15, 0) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function

def air_puff(X): #define function for delivering air puff
    
    if X == 'A':
        bus1.write_pin(9, 1) #turns air puff ON
        time.sleep(1.5) #waits for 1.5 seconds
        bus1.write_pin(9, 0) #turns air puff OFF
        
    elif X == 'B':
        bus1.write_pin(11, 1) #turns air puff ON
        time.sleep(1.5)
        bus1.write_pin(11, 0) #turns air puff OFF
        
    elif X == 'C':
        bus1.write_pin(13, 1) #turns air puff ON
        time.sleep(1.5)
        bus1.write_pin(13, 0) #rturns air puff OFF
    
    elif X == 'D':
        bus1.write_pin(15, 1) #turns air puff ON
        time.sleep(1.5)
        bus1.write_pin(15, 0)
    
    else:
        print('something wrong. find me: air_puff(X)')
        
    bus1.write_pin(9, 0) #turns air puff OFF
    bus1.write_pin(11, 0) #turns air puff OFF
    bus1.write_pin(13, 0) #turns air puff OFF
    bus1.write_pin(15, 0) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function
    
def bad_buzz(X): #define funtion to be executed when animal is heaveir than chosen weight treshold

    if X == 'A':
        buzz_A.start(50)
        for _ in range(10):
            print("bad buzz mouse A")
            buzz_A.ChangeFrequency(heavier_buzz_1) #1st tone
            bus2.write_pin(11, 1) #turns red led ON
            time.sleep(0.1)
            buzz_A.ChangeFrequency(heavier_buzz_2) #2nd tone
            bus2.write_pin(11, 0) #turns red led OFF
            time.sleep(0.1)
        buzz_A.stop()
    
    elif X == 'B':
        buzz_B.start(50)
        for _ in range(10):
            print("bad buzz mouse B")
            buzz_B.ChangeFrequency(heavier_buzz_1) #1st tone
            bus2.write_pin(15, 1) #turns red led ON
            time.sleep(0.1)
            buzz_B.ChangeFrequency(heavier_buzz_2) #2nd tone
            bus2.write_pin(15, 0) #turns red led OFF
            time.sleep(0.1)
        buzz_B.stop()
        
    elif X == 'C':
        buzz_C.start(50)
        for _ in range(10):
            print("bad buzz mouse C")
            buzz_C.ChangeFrequency(heavier_buzz_1) #1st tone
            bus2.write_pin(12, 1) #turns red led ON
            time.sleep(0.1)
            buzz_C.ChangeFrequency(heavier_buzz_2) #2nd tone
            bus2.write_pin(12, 0) #turns red led OFF
            time.sleep(0.1)
        buzz_C.stop()
        
    elif X == 'D':
        buzz_D.start(50)
        for _ in range(10):
            print("bad buzz mouse D")
            buzz_D.ChangeFrequency(heavier_buzz_1) #1st tone
            bus2.write_pin(16, 1) #turns red led ON
            time.sleep(0.1)
            buzz_D.ChangeFrequency(heavier_buzz_2) #2nd tone
            bus2.write_pin(16, 0) #turns red led OFF
            time.sleep(0.1)
        buzz_D.stop()
        
    else:
        print('something wrong. find me: bad_buzz(X)')

def good_buzz(X): #define funtion to be executed when animal is heaveir than chosen weight treshold
    
    if X == 'A':
        buzz_A.start(50)
        for _ in range(10):
            print("good buzz mouse A")
            buzz_A.ChangeFrequency(not_heavier_buzz_1) #1st tone
            bus2.write_pin(9, 1) #turns green led ON
            time.sleep(0.1)
            buzz_A.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            bus2.write_pin(9, 0) #turns green led OFF
            time.sleep(0.1)
        buzz_A.stop()
        
    elif X == 'B':
        buzz_B.start(50)
        for _ in range(10):
            print("good buzz mouse B")
            buzz_B.ChangeFrequency(not_heavier_buzz_1) #1st tone
            bus2.write_pin(13, 1) #turns green led ON
            time.sleep(0.1)
            buzz_B.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            bus2.write_pin(13, 0) #turns green led OFF
            time.sleep(0.1)
        buzz_B.stop()
        
    elif X == 'C':
        buzz_C.start(50)
        for _ in range(10):
            print("good buzz mouse C")
            buzz_C.ChangeFrequency(not_heavier_buzz_1) #1st tone
            bus2.write_pin(10, 1) #turns green led ON
            time.sleep(0.1)
            buzz_C.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            bus2.write_pin(10, 0) #turns green led OFF
            time.sleep(0.1)
        buzz_C.stop()
    
    elif X == 'D':
        buzz_D.stat(50)
        for _ in range(10):
            print("good buzz mouse D")
            buzz_D.ChangeFrequency(not_heavier_buzz_1) #1st tone
            bus2.write_pin(14, 1) #turns green led ON
            time.sleep(0.1)
            buzz_D.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            bus2.write_pin(14, 0) #turns gren led OFF
            time.sleep(0.1)
        buss_D.stop()
        
    else:
        print('something wrong. find me: good_buzz(X)')
        
def scan_tube_leaving(X): #define function for checking if animal has left the scale
    animal_left = False
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(8):
            line = ser_A.readline()
        
        while animal_left == False:
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            
            if mg < float(10):
                print("mouse A left for social area.")
                animal_left = True
                ser_A.close()
                return True
            else:
                animal_left = False
                return False
    
    elif X == 'B':
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        for _ in range(8):
            line = ser_B.readline()
        
        while animal_left == False:
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            
            if mg < float(10):
                print("mouse B left for social area.")
                animal_left = True
                ser_B.close()
                return True
            else:
                animal_left = False
                return False         
    
    elif X == 'C':
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        for _ in range(8):
            line = ser_C.readline()
        
        while animal_left == False:
            line = ser_C.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            
            if mg < float(10):
                print("mouse C left for social area.")
                animal_left = True
                ser_C.close()
                return True
            else:
                animal_left = False
                return False
    
    elif X == 'D':
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        for _ in range(8):
            line = ser_D.readline()
        
        while animal_left == False:
            line = ser_D.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
            
            if mg < float(10):
                print("mouse D left for social area.")
                animal_left = True
                ser_D.close()
                return True
            else:
                animal_left = False
                return False
            
    else:
        print('something wrong. find me: scan_tube_leaving(X)')
        
def append_rotation(X, wheel_counter): #define function for storing wheel data
    
    rotation_list = {
    "Mouse" : [],
    "Rotation" : [],
    "Date_Time" : []
    }
    
    rotation_list.update({"Mouse" : [X]})
    rotation_list.update({"Rotation" : [wheel_counter]})
    rotation_list.update({"Date_Time" : [datetime.now()]})
    
    df_r = pd.DataFrame(rotation_list)
    print(df_r)
    
    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
def append_pellet(X,pellet_counter):#define function for storing pellet retrieval data
    
    pellet_list = {
    "Mouse" : [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Mouse" : [X]})
    pellet_list.update({"Pellet": [pellet_counter]})
    pellet_list.update({"Date_Time": [datetime.now()]})

    df_p = pd.DataFrame(pellet_list)
    print(df_p)

    if not os.path.isfile("pellet.csv"):
        df_p.to_csv("pellet.csv", encoding = "utf-8-sig", index = False)
    else:
        df_p.to_csv("pellet.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
FUNCTIONS FOR THREADING
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
def mouse_A(MODE_A): #define function that runs everything for mouse A
    
    global dtLastState_A
    global wheel_counter_A
    global turn_A
    global pellet_counter_A
    global limit_A
    
    while True:
    
        if MODE_A == 0: 
            move_door_social('A')
            print("\nMODE_A 0\n")
            
            
        while MODE_A == 0:
            proximity_check_A = animal_in_tube('A') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_A == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1A')
                tag_A = RFID_check('A') #checks RFID tag and returns bolean 
                    
                if tag_A == True: #CHECK 2: if it's mouse B, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2A')
                    how_many_A = scan_tube_entry('A') #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_A == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3A')
                        move_door_close('A') #close doors
                        which_mouse = 'A'
                        MODE_A = 1 
                            
                    else: #CHECK 3
                        print('check 3A fail')
                        how_many_A = False
                        proximity_check_A = False
                        tag_A = False
                        pass
                    
                else: #CHECK 2
                    print('check 2A fail')
                    tag_A = False
                    proximity_check_A = False
                    pass
                
            else: #CHECK 1
                proximity_check_A = False
                pass
                
        if MODE_A == 1:
            ser_A.close()
            print("\nMODE_A 1\n")
            mg_pre_mean_A = acquire_weight_pre('A') #saves the mean weight data
            move_door_feeding('A') #open door to feeding area
            
            while MODE_A == 1:
                MODE_A = wait_for_animal_to_leave_foor_feeding_area('A') #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_A == 2:
            print("\nMODE_A 2\n")
            ser_A.close()
            
            while MODE_A == 2:
                dtState_A = bus2.read_pin(1) #read input from running wheel
                returned_A = animal_in_tube('A') #checks if animal has returned from feeding area and store it as boolean
                
                if returned_A == False: #if animal has not yet returned from feeding area, perform these functions
                    
                    if dtState_A != dtLastState_A: 
                        wheel_counter_A += 1 #running wheel rotation wheel_counter
                        dtLastState_A = dtState_A
                        
                        if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
                            turn_A = wheel_counter_A/cycle_A
                            limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                            print("mouse A wheel turns: "+str(turn_A))
                            
                            if turn_A % 10 == 0 and turn_A != 0: #each 10 revolutions
                                print("mouse A completed 10 wheel turns, delivering pellet")
                                bus1.write_pin(1, 1) #sends output to FED - turnd FED motor on and makes pellet drop
                        else:
                            pass
                    
                    elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
                        bus1.write_pin(1, 0) #turns FED motor off
                        air_puff('A') #delivers air puff to animal
                        pellet_counter_A += 1 #counts one pellet
                        print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
                    
                    else:
                        pass
                    
                
                else: #if animal has returned from feeding area, perform these functions
                    print("mouse A returned. acquiring weight")
                    print("mouse A rotation counter: "+str(wheel_counter_A))
                    move_door_close('A') #close doors for proper weighting
                    append_rotation('A', wheel_counter_A) #save running wheel rotation data
                    append_pellet('A', pellet_counter_A) #save pellet data
                    
                    wheel_counter_A = 0 #reset wheel rotation counter
                    pellet_counter_A = 0 #reset pellet counter
                    turn_A = 0 #reset wheel turn counter
                    limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                    dtLastState_A = dt_A #reset input from wheel 
                    
                    mg_post_mean_A = acquire_weight_post('A') #acquire weight and assign mean weight value
                    check_weight_post_A(mg_pre_mean_A, mg_post_mean_A) #compare weights pre and post and delivered stimulus
                    move_door_social('A') #open door to social area
                    animal_left_A = scan_tube_leaving('A') #scan tube to check whether animal is still in and stores info as boolean
                    
                    while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                        animal_left_A = scan_tube_leaving('A') #scan tube to check whether animal is still in and stores info as boolean
                        
                    if animal_left_A == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_close('A') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse A: cycle over, starting again")
                        MODE_A = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping  

def mouse_B(MODE_B): #define function that runs everything for mouse B
   
    global dtLastState_B
    global wheel_counter_B
    global turn_B
    global pellet_counter_B
    global limit_B
    
    while True:
    
        if MODE_B == 0: 
            move_door_social('B')
            print("\nMODE_B 0\n")
            
            
        while MODE_B == 0:
            proximity_check_B = animal_in_tube('B') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_B == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1B')
                tag_B = RFID_check('B') #checks RFID tag and returns bolean 
                    
                if tag_B == True: #CHECK 2: if it's mouse B, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2B')
                    how_many_B = scan_tube_entry('B') #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_B == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3B')
                        move_door_close('B') #close doors
                        which_mouse = 'B'
                        MODE_B = 1 
                            
                    else: #CHECK 3
                        print('check 3B fail')
                        how_many_B = False
                        proximity_check_B = False
                        tag_B = False
                        pass
                    
                else: #CHECK 2
                    print('check 2B fail')
                    tag_AB = False
                    proximity_check_B = False
                    pass
                
            else: #CHECK 1
                proximity_check_B = False
                pass
                
        if MODE_B == 1:
            ser_B.close()
            print("\nMODE_B 1\n")
            mg_pre_mean_B = acquire_weight_pre('B') #saves the mean weight data
            move_door_feeding('B') #open door to feeding area
            
            while MODE_B == 1:
                MODE_B = wait_for_animal_to_leave_foor_feeding_area('B') #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_B == 2:
            print("\nMODE_B 2\n")
            ser_B.close()
            
            while MODE_B == 2:
                dtState_B = bus2.read_pin(3) #read input from running wheel
                returned_B = animal_in_tube('B') #checks if animal has returned from feeding area and store it as boolean
                
                if returned_B == False: #if animal has not yet returned from feeding area, perform these functions
                    
                    if dtState_B != dtLastState_B: 
                        wheel_counter_B += 1 #running wheel rotation wheel_counter
                        dtLastState_B = dtState_B
                        
                        if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
                            turn_B = wheel_counter_B/cycle_B
                            limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
                            print("mouse B wheel turns: "+str(turn_B))
                            
                            if turn_B % 10 == 0 and turn_B != 0: #each 10 revolutions
                                print("mouse B completed 10 wheel turns, delivering pellet")
                                bus1.write_pin(3, 1) #sends output to FED - turnd FED motor on and makes pellet drop
                        else:
                            pass
                    
                    elif GPIO.event_detected(read_FED_B): #detects signal coming from the FED
                        bus1.write_pin(3, 0) #turns FED_B motor off
                        air_puff('B') #delivers air puff to animal
                        pellet_counter_B += 1 #counts one pellet
                        print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))
                    
                    else:
                        pass
                    
                
                else: #if animal has returned from feeding area, perform these functions
                    print("mouse B returned. acquiring weight")
                    print("mouse B rotation counter: "+str(wheel_counter_B))
                    move_door_close('B') #close doors for proper weighting
                    append_rotation('B', wheel_counter_B) #save running wheel rotation data
                    append_pellet('B', pellet_counter_B) #save pellet data
                    
                    wheel_counter_B = 0 #reset wheel rotation counter
                    pellet_counter_B = 0 #reset pellet counter
                    turn_B = 0 #reset wheel turn counter
                    limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                    dtLastState_B = dt_B #reset input from wheel 
                    
                    mg_post_mean_B = acquire_weight_post('B') #acquire weight and assign mean weight value
                    check_weight_post_B(mg_pre_mean_B, mg_post_mean_B) #compare weights pre and post and delivered stimulus
                    move_door_social('B') #open door to social area
                    animal_left_B = scan_tube_leaving('B') #scan tube to check whether animal is still in and stores info as boolean
                    
                    while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                        animal_left_B = scan_tube_leaving('B') #scan tube to check whether animal is still in and stores info as boolean
                        
                    if animal_left_B == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_close('B') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse B: cycle over, starting again")
                        MODE_B = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping

def mouse_C(MODE_C): #define function that runs everything for mouse C
   
    global dtLastState_C
    global wheel_counter_C
    global turn_C
    global pellet_counter_C
    global limit_C
    
    while True:
    
        if MODE_C == 0: 
            move_door_social('C')
            print("\nMODE_C 0\n")
            
            
        while MODE_C == 0:
            proximity_check_C = animal_in_tube('C') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_C == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1C')
                tag_B = RFID_check('C') #checks RFID tag and returns bolean 
                    
                if tag_C == True: #CHECK 2: if it's mouse C, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2C')
                    how_many_C = scan_tube_entry('C') #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_C == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3C')
                        move_door_close('C') #close doors
                        which_mouse = 'C'
                        MODE_C = 1 
                            
                    else: #CHECK 3
                        print('check 3C fail')
                        how_many_C = False
                        proximity_check_C = False
                        tag_C = False
                        pass
                    
                else: #CHECK 2
                    print('check 2C fail')
                    tag_C = False
                    proximity_check_C = False
                    pass
                
            else: #CHECK 1
                proximity_check_C = False
                pass
                
        if MODE_C == 1:
            ser_C.close()
            print("\nMODE_C 1\n")
            mg_pre_mean_C = acquire_weight_pre('C') #saves the mean weight data
            move_door_feeding('C') #open door to feeding area
            
            while MODE_C == 1:
                MODE_C = wait_for_animal_to_leave_foor_feeding_area('C') #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_C == 2:
            print("\nMODE_C 2\n")
            ser_C.close()
            
            while MODE_C == 2:
                dtState_C = bus2.read_pin(5) #read input from running wheel
                returned_C = animal_in_tube('C') #checks if animal has returned from feeding area and store it as boolean
                
                if returned_C == False: #if animal has not yet returned from feeding area, perform these functions
                    
                    if dtState_C != dtLastState_C: 
                        wheel_counter_C += 1 #running wheel rotation wheel_counter
                        dtLastState_C = dtState_C
                        
                        if wheel_counter_C >= limit_C: #when completes 1 full turn (wheel_counter = 1200)
                            turn_C = wheel_counter_C/cycle_C
                            limit_C = wheel_counter_C + cycle_C #reset limit for 1 extra turn
                            print("mouse C wheel turns: "+str(turn_C))
                            
                            if turn_C % 10 == 0 and turn_C != 0: #each 10 revolutions
                                print("mouse C completed 10 wheel turns, delivering pellet")
                                bus1.write_pin(5, 1) #sends output to FED - turnd FED motor on and makes pellet drop
                        else:
                            pass
                    
                    elif GPIO.event_detected(read_FED_C): #detects signal coming from the FED
                        bus1.write_pin(5, 0) #turns FED_B motor off
                        air_puff('C') #delivers air puff to animal
                        pellet_counter_C += 1 #counts one pellet
                        print("Pellet retrieved. Pellet counter for mouse C: "+str(pellet_counter_C))
                    
                    else:
                        pass
                    
                
                else: #if animal has returned from feeding area, perform these functions
                    print("mouse C returned. acquiring weight")
                    print("mouse C rotation counter: "+str(wheel_counter_C))
                    move_door_close('C') #close doors for proper weighting
                    append_rotation('C', wheel_counter_C) #save running wheel rotation data
                    append_pellet('C', pellet_counter_C) #save pellet data
                    
                    wheel_counter_C = 0 #reset wheel rotation counter
                    pellet_counter_C = 0 #reset pellet counter
                    turn_C = 0 #reset wheel turn counter
                    limit_C = cycle_C #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                    dtLastState_C = dt_C #reset input from wheel 
                    
                    mg_post_mean_C = acquire_weight_post('C') #acquire weight and assign mean weight value
                    check_weight_post_C(mg_pre_mean_C, mg_post_mean_C) #compare weights pre and post and delivered stimulus
                    move_door_social('C') #open door to social area
                    animal_left_C = scan_tube_leaving('C') #scan tube to check whether animal is still in and stores info as boolean
                    
                    while animal_left_C == False: #while the animal is still on the tube, perform thee tasks
                        animal_left_C = scan_tube_leaving('C') #scan tube to check whether animal is still in and stores info as boolean
                        
                    if animal_left_C == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_close('C') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse C: cycle over, starting again")
                        MODE_C = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping
                    
def mouse_D(MODE_D): #define function that runs everything for mouse D
   
    global dtLastState_D
    global wheel_counter_D
    global turn_D
    global pellet_counter_D
    global limit_D
    
    while True:
    
        if MODE_D == 0: 
            move_door_social('D')
            print("\nMODE_D 0\n")
            
            
        while MODE_D == 0:
            proximity_check_D = animal_in_tube('D') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_D == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1D')
                tag_D = RFID_check('D') #checks RFID tag and returns bolean 
                    
                if tag_D == True: #CHECK 2: if it's mouse D, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2D')
                    how_many_D = scan_tube_entry('D') #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_D == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3D')
                        move_door_close('D') #close doors
                        which_mouse = 'D'
                        MODE_D = 1 
                            
                    else: #CHECK 3
                        print('check 3D fail')
                        how_many_D = False
                        proximity_check_D = False
                        tag_D = False
                        pass
                    
                else: #CHECK 2
                    print('check 2D fail')
                    tag_D = False
                    proximity_check_D = False
                    pass
                
            else: #CHECK 1
                proximity_check_D = False
                pass
                
        if MODE_D == 1:
            ser_D.close()
            print("\nMODE_D 1\n")
            mg_pre_mean_D = acquire_weight_pre('D') #saves the mean weight data
            move_door_feeding('D') #open door to feeding area
            
            while MODE_D == 1:
                MODE_D = wait_for_animal_to_leave_foor_feeding_area('D') #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_D == 2:
            print("\nMODE_D 2\n")
            ser_D.close()
            
            while MODE_D == 2:
                dtState_D = bus2.read_pin(7) #read input from running wheel
                returned_D = animal_in_tube('D') #checks if animal has returned from feeding area and store it as boolean
                
                if returned_D == False: #if animal has not yet returned from feeding area, perform these functions
                    
                    if dtState_D != dtLastState_D: 
                        wheel_counter_D += 1 #running wheel rotation wheel_counter
                        dtLastState_D = dtState_D
                        
                        if wheel_counter_D >= limit_D: #when completes 1 full turn (wheel_counter = 1200)
                            turn_D = wheel_counter_D/cycle_D
                            limit_D = wheel_counter_D + cycle_D #reset limit for 1 extra turn
                            print("mouse D wheel turns: "+str(turn_D))
                            
                            if turn_D % 10 == 0 and turn_D != 0: #each 10 revolutions
                                print("mouse D completed 10 wheel turns, delivering pellet")
                                bus1.write_pin(7, 1) #sends output to FED - turnd FED motor on and makes pellet drop
                        else:
                            pass
                    
                    elif GPIO.event_detected(read_FED_D): #detects signal coming from the FED
                        bus1.write_pin(7, 0) #turns FED_B motor off
                        air_puff('D') #delivers air puff to animal
                        pellet_counter_D += 1 #counts one pellet
                        print("Pellet retrieved. Pellet counter for mouse D: "+str(pellet_counter_D))
                    
                    else:
                        pass
                    
                
                else: #if animal has returned from feeding area, perform these functions
                    print("mouse D returned. acquiring weight")
                    print("mouse D rotation counter: "+str(wheel_counter_D))
                    move_door_close('D') #close doors for proper weighting
                    append_rotation('D', wheel_counter_D) #save running wheel rotation data
                    append_pellet('D', pellet_counter_D) #save pellet data
                    
                    wheel_counter_D = 0 #reset wheel rotation counter
                    pellet_counter_D = 0 #reset pellet counter
                    turn_D = 0 #reset wheel turn counter
                    limit_D = cycle_D #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                    dtLastState_D = dt_D #reset input from wheel 
                    
                    mg_post_mean_D = acquire_weight_post('D') #acquire weight and assign mean weight value
                    check_weight_post_D(mg_pre_mean_D, mg_post_mean_D) #compare weights pre and post and delivered stimulus
                    move_door_social('D') #open door to social area
                    animal_left_D = scan_tube_leaving('D') #scan tube to check whether animal is still in and stores info as boolean
                    
                    while animal_left_D == False: #while the animal is still on the tube, perform thee tasks
                        animal_left_D = scan_tube_leaving('D') #scan tube to check whether animal is still in and stores info as boolean
                        
                    if animal_left_D == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_close('D') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse D: cycle over, starting again")
                        MODE_D = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping
                    
'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
print("/n STARTING EXECUTION /n")

#set all doors to social position
move_door_social('A')
move_door_social('B')
move_door_social('C')
move_door_social('D')
#close all RFID antennas serial ports
RFID_A.close()
RFID_B.close()
RFID_C.close()
RFID_D.close()
#close all OpenScales seria ports
ser_A.close()
ser_B.close()
ser_C.close()
ser_D.close()
#turn signal to al FEDs low
bus1.write_pin(1, 0) #FED_A off
bus1.write_pin(3, 0) #FED_B off
bus1.write_pin(5, 0) #FED_C off
bus1.write_pin(7, 0) #FED_D off
#turn signal to all air puffs low
bus1.write_pin(9, 0) #air puff A off
bus1.write_pin(11, 0) #air puff B off
bus1.write_pin(13, 0) #air puff C off
bus1.write_pin(15, 0) #air puff D off
#set MODE variables
MODE_A = 0
MODE_B = 0
MODE_C = 0
MODE_D = 0

#create thread objects
thread_A = threading.Thread(target=mouse_A, args=(MODE_A,))
thread_B = threading.Thread(target=mouse_B, args=(MODE_B,))
thread_C = threading.Thread(target=mouse_C, args=(MODE_C,))
thread_D = threading.Thread(target=mouse_D, args=(MODE_D,))
#initialize thread objects   
thread_A.start()
thread_B.start()
thread_C.start()
thread_D.start()