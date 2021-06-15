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

print("Please specify which protocol to run: \n 'OG' = original script, all feedbacks active \n 'PR' = practice mode, all feedbacks inactive \n 'FBA' = fear based anorexia  \n 'CBA' = cost based anorexia  \n 'WBA' = weight based anorexia")
protocol = input() #specify the protocol
'''
"OG" = original, refers to the base code - all feedbacks active
"PR" = practice mode, animals have full access to food and no feedback of any kind
"FBA" = fear based anorexia
"CBA" = cost based anorexia
"WBA" = weight based anorexia
""
'''
if protocol == "CBA":
    print("\nProtocol chosen: CBA  \n Please define pellet price (in wheel turns): \n 0 = 1 \n 1 = 5 \n 2 = 10 \n 3 = 25 \n 4 = 50 \n 5 = 100 \n")
    pellet_price = input() #set pellet price for CBA protocol
    print("Price set to "+str(pellet_price)+" wheel turns for a food pellet \n")
elif protocol == "FBA":
    pellet_price = 0
    print("\nProtocol chosen: FBA\n")
elif protocol == "WBA":
    pellet_price = 0
    print("\nProtocol chosen: WBA\n")
elif protocol == "PR":
    pellet_price = 0
    print("\nProtocol chosen: PR\n")
elif protocol == "OG":
    pellet_price = 0
    print("\nProtocol chosen: OG\n")

#soft coded parameters
lines_to_chuck = 15 #specify how many lines to chuck when accessing OpenScales (more lines, more time it takes)
wheel_turns_OG = 1 #specify pellet price in wheel turns for the OG protocol
airpuff_time = 1.5 #specify (in seconds) how long the air puff will last
cycle_A = 160; #calibration value for running wheel (1200 for old wheels, 160 for new ones)
cycle_B = 160; #calibration value for tunning wheel (1200 for old wheels, 160 for new ones)
heavier_buzz_1 = 700 #frequency of 1st tone when animal is heavier than before
heavier_buzz_2 = 589 #frequency of 2nd tone when animal is heavier than before
not_heavier_buzz_1 = 131 #frequency of 1st tone when animal is NOT heavier than before
not_heavier_buzz_2 = 165 #frequency of 2nd tone when animal is NOT heavier than before
IDtag_A = "137575399650" #define tag ID for mouse A
IDtag_B = "137575399602" #define tag ID for mouse B
#ALWAYS CHECK TO SEE IF SERIAL PORTS ARE CORRECT BEFORE RUNNING CODE!!!!!!!
serial_port_A = '/dev/ttyUSB0' #define USB port used to collect serial data from OpenScale
serial_port_B = '/dev/ttyUSB1' #define USB port used to collect serial data from OpenScale


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
writeFED_B = 23 #pin that reads information from FED (if pellet has been retireved or not)
airpuff_B = 35 #pin that controls air puff

''' configure door pins '''
#mouse A
GPIO.setup(PdA_food,GPIO.OUT) #set pin as output
GPIO.setup(PdA_social, GPIO.OUT) #set pin as output
GPIO.output(PdA_food,False); GPIO.output(PdA_social, True) #door position: SOCIAL

#mouse B
GPIO.setup(PdB_food,GPIO.OUT) #set pin as output
GPIO.setup(PdB_social, GPIO.OUT) #set pin as output
GPIO.output(PdB_food,False); GPIO.output(PdB_social, True) #door position: SOCIAL

''' configure pins for buzzers and LEDs '''
#mouse A
#set pin output to buzzer and LEDs
GPIO.setup(gLED_A, GPIO.OUT) #set pin as output
GPIO.setup(rLED_A, GPIO.OUT) #set pin as output
GPIO.setup(buzzer_A, GPIO.OUT) #set pin as output
buzz_A = GPIO.PWM(buzzer_A, 1) #create PWM object and set starting frequency at 1 (inaudible)
GPIO.output(gLED_A, False) #turn green LED off
GPIO.output(rLED_A,False) #turn red LED off

#mouse B
GPIO.setup(gLED_B, GPIO.OUT) #set pin as output
GPIO.setup(rLED_B, GPIO.OUT) #set pin as output
GPIO.setup(buzzer_B, GPIO.OUT) #set pin as output
buzz_B = GPIO.PWM(buzzer_B, 1) #create PWM object ans set starting frequency at 1 (inaudible)
GPIO.output(gLED_B, False) #turn green LED off
GPIO.output(rLED_B,False) #turn red LED off

''' configure pins for running wheel '''
#mouse A
#set pin inputs from running wheel rotary encoder and initialize variables
GPIO.setup(dt_A, GPIO.IN) #set pin as input
dtLastState_A = GPIO.input(dt_A) #set variable = dt input pin
wheel_counter_A = 0 #set initial rotation counter to 0
limit_A = cycle_A #set limit (e.g. how many counts = 1 wheel revolution)
turn_A = 0 #set variable to count wheel revolutions

#mouse B
#set pin inputs from running wheel rotary encoder and initialize variables
GPIO.setup(dt_B, GPIO.IN) #set pin as input
dtLastState_B = GPIO.input(dt_B) #set variable = dt input pin
wheel_counter_B = 0 #set initial rotation counter to 0
limit_B = cycle_B #set limit (e.g. how many counts = 1 wheel revolution)
turn_B = 0 #set variable to count wheel revolutions

''' configure pins for IR proximity detectors '''
#mouse A
#set pins for infrared proximity detector
GPIO.setup(IR_A, GPIO.IN) #set pin as input

#mouse B
#set pins for infrared proximity detector
GPIO.setup(IR_B, GPIO.IN) #set pin as input

''' configure pins for sending commands to the FED (Pi --> FED) '''
#mouse A
#set pins for output to FED_A
GPIO.setup(writeFED_A, GPIO.OUT) #set pin as output
GPIO.output(writeFED_A, False) #turn pin signal off

#mouse B
#set pins for output to FED_B
GPIO.setup(writeFED_B, GPIO.OUT) #set pin as output
GPIO.output(writeFED_B, False) #turn pin signal off

''' configure pins for reading input from FED (FED --> Pi) '''
#mouse A
#set pin for input from FED_A
GPIO.setup(read_FED_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #set pin as input
GPIO.add_event_detect(read_FED_A, GPIO.RISING) #set this pin to detect whenever there is a change in voltage (RISING = from low to high)
pellet_counter_A = 0 #set variable that coubnts how many pellets were retirved to 0

#mouse B
#set pin for input from FED_B
GPIO.setup(read_FED_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #set pin as input
GPIO.add_event_detect(read_FED_B, GPIO.RISING) #set this pin to detect whenever there is a change in voltage (RISING = from low to high)
pellet_counter_B = 0 #set variable that coubnts how many pellets were retirved to 0

''' configure pins for air puffs '''
#mouse A
GPIO.setup(airpuff_A, GPIO.OUT) #set pin as output
GPIO.output(airpuff_A, False) #turn air puff off

#mouse B
GPIO.setup(airpuff_B, GPIO.OUT) #set pin as output
GPIO.setup(airpuff_B, False) #turn ait puff off

'''initialize MODE variable'''
MODE_A = 0
MODE_B = 0

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
INITIALIZE AND CONFIGURE SERIAL PORTS (SCALES AND ANTENNAS)
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
''' set serial ports for getting OpenScale data '''
#initialize serial port for OpenScale mouse A
ser_A = serial.Serial()
ser_A.port = serial_port_A #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
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
ser_B.port = serial_port_B #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
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


'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
DEFINE FUNCTIONS
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
        PdA_food_OFF = GPIO.output(PdA_food, False)
        PdA_social_ON = GPIO.output(PdA_social, True)
        PdA_food_OFF; PdA_social_ON #SOCIAL position
    
    elif X == 'B':
        PdB_food_OFF = GPIO.output(PdB_food, False)
        PdB_social_ON = GPIO.output(PdB_social, True)
        PdB_food_OFF; PdB_social_ON #SOCIAL position

def move_door_feeding(X):#define function for seting door at feeding position
    
    if X == 'A': 
        PdA_food_ON = GPIO.output(PdA_food, True)
        PdA_social_OFF = GPIO.output(PdA_social, False)
        PdA_food_ON; PdA_social_OFF #FEEDING position
    
    elif X == 'B':
        PdB_food_ON = GPIO.output(PdB_food, True)
        PdB_social_OFF = GPIO.output(PdB_social, False)
        PdB_food_ON; PdB_social_OFF #FEEDING position

def move_door_close(X):#define function for seting door at neutral position
    
    if X == 'A':
        PdA_food_OFF = GPIO.output(PdA_food, False)
        PdA_social_OFF = GPIO.output(PdA_social, False)
        PdA_food_OFF; PdA_social_OFF #NEUTRAL position
    
    elif X == 'B':
        PdB_food_OFF = GPIO.output(PdB_food, False)
        PdB_social_OFF = GPIO.output(PdB_social, False)
        PdB_food_OFF; PdB_social_OFF #NEUTRAL position

def animal_in_tube(X): #define function that determine whether animal has entered scale and return boolean
    
    if X == 'A':
        IR_sensor = GPIO.input(IR_A)
    elif X == 'B':
        IR_sensor = GPIO.input(IR_B)
    else:
        print('something wrong. find me: animal_in_tube(X)')
        
    if IR_sensor == 0: #if proximity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned

def append_weight(mouse, when, protocol, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode): #define function for storing weight data
    
    weight_list = {  #make dictionary to store variable values
    "Mouse_ID" : [],
    "Protocol" : [],
    "When" : [],
    "Weight_Mean": [],
    "Weight_Median": [],
    "Weight_Mode": [],
    "Weight_Max_Mode": [],
    "Date_Time": []
    }
    
    weight_list.update({'Mouse_ID' : [mouse]}) #update dictionary about which mouse is being weighted
    weight_list.update({'When' : [when]}) #if it is pre (going to feed) or post (returnong from feed)
    weight_list.update({'Protocol': [protocol]})
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

def RFID_check(X, protocol, IDtag): #define function to check ID of the animal
    
    if X == 'A':
        try:
            RFID_A.open()
            RFID_A.flush()

            junk     = RFID_A.read(1)
            tag_hex  = RFID_A.read(10)
            checksum = RFID_A.read(2)
            junk2    = RFID_A.read(3)
            
            tag = str(int(tag_hex, 16)) # transform from hexadecimal to a number
            RFID_A.close()
        except:
            RFID_A.close()
            print("Something went wrong. Find me: RFID_check(A)")
            tag = 0
        print(tag)
        if tag == '00' or tag == IDtag or tag == '38723977519':
            print("mouse A detected")
            which_mouse = "A"
            ID_tag = "mouse A"
            append_RFID(which_mouse, protocol, tag)
            return True
        else:
            print("not mouse A")
            return False
    
    elif X == 'B':
        try:
            RFID_B.open()
            RFID_B.flush()

            junk     = RFID_B.read(1)
            tag_hex  = RFID_B.read(10)
            checksum = RFID_B.read(2)
            junk2    = RFID_B.read(3)
            
            tag = str(int(tag_hex, 16)) # transform from hexadecimal to a number
            RFID_B.close()
        except:
            RFID_B.close()
            print("Something went wrong. Find me: RFID_check(B)")
            tag = 0
        print(tag)
        if tag == '00' or tag == IDtag or tag == '38723977519':
            print("mouse B detected")
            which_mouse = "B"
            ID_tag = "mouse B"
            append_RFID(which_mouse, protocol, tag)
            return True
        else:
            print("not mouse B")
            return False
        
    else:
        print('something wrong. find me: RFID_check(X)')
        
def append_RFID(which_mouse, tag, protocol): #define function  to save which animal was detected and when
    
    RFID_list = {
        "Mouse_ID" : [],
        "RFID_tag" : [],
        "Protocol" : [],
        "Date_Time" : []
        }
    
    RFID_list.update({"Mouse_ID" : [which_mouse]})
    RFID_list.update({"RFID_tag" : [tag]})
    RFID_list.update({"Protocol" : [protocol]})
    RFID_list.update({"Date_Time" : [datetime.now()]})
    
    df_rfid = pd.DataFrame(RFID_list)
    print(df_rfid)
    
    if not os.path.isfile("rfid_tag.csv"):
        df_rfid.to_csv("rfid_tag.csv", encoding="utf-8-sig", index=False)
    else:
        df_rfid.to_csv("rfid_tag.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

def scan_tube_entry(X, lines_to_chuck): #define function to check wether there is only one animal in scale and return boolean
    animal_enter = False #function will end and return True when these variables become True
    animal_alone = False #function will end and return True when these variables become True
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_A.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg = relProb_float*1000
            
            if mg > float(10) and mg < float(30): #if weight >10 and <30, return True
                print("scale scan: 1 animal on scale.")
                return True
                animal_enter = True
                animal_alone = True
                ser_A.close()
            elif mg >= float(30): #if weight >30, return False
                print("more than one animal on scale, restarting")
                return False
                animal_enter = True
                animal_alone = False
            else: #if weight <10, return False
                return False
                animal_enter = False
                animal_alone = False
        
    elif X == 'B':
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_B.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg = relProb_float*1000
            print(mg)
            
            if mg > float(10) and mg < float(30): #if weight >10 and <30, return True
                print("scale scan: 1 animal on scale.")
                return True
                animal_enter = True
                animal_alone = True
                ser_B.close()
            elif mg >= float(30): #if weight >30, return False
                print("more than one animal on scale, restarting")
                return False
                animal_enter = True
                animal_alone = False
            else: #if weight <10, return False
                return False
                animal_enter = False
                animal_alone = False
    else:
        print('something wrong. find me: scan_tube_entry(X)')
        
'''
MODE 1 FUNCTIONS ########################################################################################
'''

def acquire_weight_pre(X, lines_to_chuck, protocol, ID_tag): #define function to acquire and sotre weight data
    
    if X == 'A':
        print("acquiring weight PRE - mouse A")
        openscale = [] #store weights here
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_A.readline()   
        for x in range(100): # 100 lines*120ms per line=12s of data 
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg_pre = relProb_float*1000
            openscale.append(mg_pre) #temporatily stores weight value
            print("mouse A weight in grams PRE: "+str(mg_pre))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            mouse = ID_tag #mouse ID
            when = 'pre' #specify if pre pre or post
            weight_data_mean = stats.mean(openscale) #mean
            weight_data_median = stats.median(openscale) #meadian
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
        append_weight(mouse, when, protocol, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
        print("mouse A weight data saved. opening door.")
#         ser_A.close()
        return weight_data_mean
        
    elif X == 'B':
        print("acquiring weight PRE - mouse B")
        openscale = [] #store weights here
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_B.readline()   
        for x in range(100): # 100 lines*120ms per line=12s of data
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg_pre = relProb_float*1000
            openscale.append(mg_pre) #temporatily stores weight value
            print("mouse B weight in grams PRE: "+str(mg_pre))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            mouse = ID_tag #mouse ID
            when = 'pre' #specify if pre pre or post
            weight_data_mean = stats.mean(openscale) # mean 
            weight_data_median = stats.median(openscale) # median
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
        append_weight(mouse, when, protocol, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
        print("mouse B weight data saved. opening door.")
        ser_B.close()
        return weight_data_mean   

    else:
        print('something wrong. find me: acquire_weight_pre(X)')

def wait_for_animal_to_leave_foor_feeding_area(X, lines_to_chuck): #define function for determining if animal has left the tube
    
    animal_out = False
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_A.readline()
        
        while animal_out == False: #while animal_out is False, keep looping
                    
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg = relProb_float*1000
        
            if mg < float(5): #if weight on scale goes below 5g (after weighting), assign the value 2 to the MODE variable
                animal_out = True #change animal_out value to True (stops the loop)
                print("mouse A left for feeding area")
                ser_A.close()
                return 2 #return value to be assigned to MODE_A
            else: #if weight on scale stays above 5g (after weighting), assign the value 1 to the MODE variable
                animal_out = False #keeps animal_out value as False (continues with the loop)
                return 1 #return value to be assigned to MODE_A      
        
    elif X == 'B':
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_B.readline()
        
        while animal_out == False: #while animal_out is False, keep looping
                    
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg = relProb_float*1000
        
            if mg < float(5): #if weight on scale goes below 5g (after weighting), assign the value 2 to the MODE variable
                animal_out = True #change animal_out value to True (stops the loop)
                print("mouse B left for feeding area")
                ser_B.close()
                return 2 #return value to be assigned to MODE_B
            else: #if weight on scale stays above 5g (after weighting), assign the value 1 to the MODE variable
                animal_out = False #keeps animal_out value as False (continues with the loop)
                return 1 #return value to be assigned to MODE_B
            
    else:
        print('something wrong. find me: wait_for_animal_to_leave_foor_feeding_area(X)')

'''
MODE 2 FUNCTIONS ########################################################################################
'''

def acquire_weight_post(X, lines_to_chuck, protocol, ID_tag): #define function to acquire and save weight data
    
    if X == 'A':
        openscale = [] #store weights here
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_A.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data 
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg_post = relProb_float*1000
            openscale.append(mg_post)
            print("mouse A weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            mouse = ID_tag #ID
            when = 'post' #specify if pre or post
            weight_data_mean = stats.mean(openscale) #mean
            weight_data_median = stats.median(openscale) #median
            try: # mode
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
            try: # mode max TO DO
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, when, protocol, weight_data_mean, weight_data_median,
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
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_B.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_post = relProb_float*1000 #this block of code processes and extracts the info and puts it in float format
            openscale.append(mg_post)
            print("mouse B weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            mouse = ID_tag #ID
            when = 'post' #specify if pre or post
            weight_data_mean = stats.mean(openscale) #mean
            weight_data_median = stats.median(openscale) #median
            try:# mode
                weight_data_mode = stats.mode(openscale)
            except:
                weight_data_mode = "NO MODE"
            try:# mode max TO DO
                weight_data_max_mode = stats.multimode(openscale)
                weight_data_max_mode = weight_data_max_mode[-1] # largest of modes
            except:
                weight_data_max_mode = "NO MAX_MODE"

    
        #appending data to database
        append_weight(mouse, when, protocol, weight_data_mean, weight_data_median,
                      weight_data_mode, weight_data_max_mode)
        
        #define variables for comaprison with if clause in the next functuion
        mg_post_mean = weight_data_mean
        mg_post_median = weight_data_median
        
        # change mode and clean up
        del openscale
        ser_B.close()
        
        #return values for comparison
        return mg_post_mean
    
    else:
        print('something wrong. find me: acquire_weight_post(X)')
        
def check_weight_post_A(mg_pre_mean_A, mg_post_mean_A): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_A > mg_pre_mean_A: #if mean weight POST (coming from feeding area) is bigger than mean weight PRE (going to feeding area)
        print("mouse A is heavier than before. initializing buzzer")
        bad_buzz('A', heavier_buzz_1, heavier_buzz_2) #execute bad_buzz(X) function
        air_puff('A', airpuff_time) #execute air_puff(X) function
        
    else: #if mean weight POST (coming from feeding area) is NOT bigger than mean weight PRE (going to feeding area)
        print("mouse A is not havier than before. opening door")
        good_buzz('A', not_heavier_buzz_1, not_heavier_buzz_2) #execute good_buzz(X) function
    
    GPIO.output(airpuff_A, False) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function
        
def check_weight_post_B(mg_pre_mean_B, mg_post_mean_B): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_B > mg_pre_mean_B: #if mean weight POST (coming from feeding area) is bigger than mean weight PRE (going to feeding area)
        print("mouse B is heavier than before. initializing buzzer")
        bad_buzz('B', heavier_buzz_1, heavier_buzz_2) #execute bad_buzz(X) function
        air_puff('B', airpuff_time) #execute air_puff(X) function
        
    else: #if mean weight POST (coming from feeding area) is NOT bigger than mean weight PRE (going to feeding area)
        print("mouse B is not havier than before. opening door")
        good_buzz('B', not_heavier_buzz_1, not_heavier_buzz_2) #execute good_buzz(X) function
    
    GPIO.output(airpuff_B, False) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function

def air_puff(X, airpuff_time): #define function for delivering air puff
    
    if X == 'A':
        GPIO.output(airpuff_A, True) #turns air puff ON
        time.sleep(airpuff_time) #waits for X seconds (defined in the beginning of the code)
        GPIO.output(airpuff_A, False) #turns air puff OFF
        
    elif X == 'B':
        GPIO.output(airpuff_B, True) #turns air puff ON
        time.sleep(airpuff_time) #waits for X seconds (defined in the beginning of the code)
        GPIO.output(airpuff_B, False) #turns air puff OFF
    
    else:
        print('something wrong. find me: air_puff(X)')
        
    GPIO.output(airpuff_A, False) #turns air puff OFF
    GPIO.output(airpuff_B, False) #turns air puff OFF  #this is to ensure both air puffs are off by the end of the function

def bad_buzz(X, heavier_buzz_1, heavier_buzz_2): #define funtion to be executed when animal is heaveir than chosen weight treshold

    if X == 'A':
        buzz_A.start(50)
        for _ in range(10):
            print("bad buzz mouse A")
            buzz_A.ChangeFrequency(heavier_buzz_1) #1st tone
            GPIO.output(rLED_A,True) #turns red led ON
            time.sleep(0.1)
            buzz_A.ChangeFrequency(heavier_buzz_2) #2nd tone
            GPIO.output(rLED_A,False) #turns red led OFF
            time.sleep(0.1)
        buzz_A.stop()

    elif X == 'B':
        buzz_B.start(50)
        for _ in range(10):
            print("bad buzz mouse B")
            buzz_B.ChangeFrequency(heavier_buzz_1) #1st tone
            GPIO.output(rLED_B,True) #turns red led ON
            time.sleep(0.1)
            buzz_B.ChangeFrequency(heavier_buzz_2) #2nd tone
            GPIO.output(rLED_B,False) #turns red led OFF
            time.sleep(0.1)
        buzz_B.stop()
        
    else:
        print('something wrong. find me: bad_buzz(X)')
        
def good_buzz(X, not_heavier_buzz_1, not_heavier_buzz_2): #define funtion to be executed when animal is heaveir than chosen weight treshold
    
    if X == 'A':
        buzz_A.start(50)
        for _ in range(10):
            print("good buzz mouse A")
            buzz_A.ChangeFrequency(not_heavier_buzz_1) #1st tone
            GPIO.output(gLED_A,True) #turns green led ON
            time.sleep(0.1)
            buzz_A.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            GPIO.output(gLED_A,False) #turns green led OFF
            time.sleep(0.1)
        buzz_A.stop()
        
    elif X == 'B':
        buzz_B.start(50)
        for _ in range(10):
            print("good buzz mouse B")
            buzz_B.ChangeFrequency(not_heavier_buzz_1) #1st tone
            GPIO.output(gLED_B,True) #turns green led ON
            time.sleep(0.1)
            buzz_B.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            GPIO.output(gLED_B,False) #turns green led OFF
            time.sleep(0.1)
        buzz_B.stop()
        
    else:
        print('something wrong. find me: good_buzz(X)')
        
def scan_tube_leaving(X, lines_to_chuck): #define function for checking if animal has left the scale
    
    animal_left = False
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_A.readline()
        
        while animal_left == False:
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg = relProb_float*1000
            
            if mg < float(10): #if scale goes below 10g, animal left the scale and went back into social area; return True
                print("mouse A left for social area.")
                animal_left = True #changes animal_left variable to True (stops loop)
                ser_A.close()
                return True #return True
            else: #if scale stays above 10g, animal is still on scale and have not yet went back into social area; return False
                animal_left = False #keeps animal_left value as False (continues loop)
                return False #return False
    
    elif X == 'B':
        ser_B.close()
        ser_B.open()
        ser_B.flush()
        for _ in range(lines_to_chuck): # chuck X lines (specified in the beginning of the code)
            line = ser_B.readline()
        
        while animal_left == False:
            line = ser_B.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0]) #this block of code processes and extracts the info and puts it in float format
            mg = relProb_float*1000
            
            if mg < float(10): #if scale goes below 10g, animal left the scale and went back into social area; return True
                print("mouse B left for social area.")
                animal_left = True #changes animal_left variable to True (stops loop)
                ser_B.close()
                return True #return True
            else: #if scale stays above 10g, animal is still on scale and have not yet went back into social area; return False
                animal_left = False #keeps animal_left value as False (continues loop)
                return False #return False
            
    else:
        print('something wrong. find me: scan_tube_leaving(X)')

def append_rotation(ID_tag, protocol, wheel_counter): #define function for storing wheel data
    
    rotation_list = {
    "Mouse_ID" : [],
    "Protocol" : [],
    "Rotation" : [],
    "Date_Time" : []
    }
    
    rotation_list.update({"Mouse_ID" : [ID_tag]})
    rotation_list.update({"Protocol" : [protocol]})
    rotation_list.update({"Rotation" : [wheel_counter]})
    rotation_list.update({"Date_Time" : [datetime.now()]})
    
    df_r = pd.DataFrame(rotation_list)
    print(df_r)
    
    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
def append_pellet(ID_tag, protocol, pellet_counter):#define function for storing pellet retrieval data
    
    pellet_list = {
    "Mouse_ID" : [],
    "Protocol" : [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Mouse_ID" : [ID_tag]})
    pellet_list.update({"Protocol" : [protocol]})
    pellet_list.update({"Pellet": [pellet_counter]})
    pellet_list.update({"Date_Time": [datetime.now()]})

    df_p = pd.DataFrame(pellet_list)
    print(df_p)

    if not os.path.isfile("pellet.csv"):
        df_p.to_csv("pellet.csv", encoding = "utf-8-sig", index = False)
    else:
        df_p.to_csv("pellet.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)

def price(pellet_price): #define function to set pellet price when choosing the CBA protocol

    if pellet_price == '0': #if user presses 0, pellet price is 1 wheel turn
        return 1
    elif pellet_price == '1': #if user presses 1, pellet price is 5 wheel turns
        return 5
    elif pellet_price == '2': #if user presses 2, pellet price is 10 wheel turns
        return 10
    elif pellet_price == '3': #if user presses 3, pellet price is 25 wheel turns
        return 25
    elif pellet_price == '4': #if user presses 4, pellet price is 50 wheel turns
        return 50
    elif pellet_price == '5': #if user presses 5, pellet price is 100 wheel turns
        return 100   
        
'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
FUNCTIONS FOR THREADING
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
def mouse_A(MODE_A, protocol, wheel_turns_OG, lines_to_chuck, airpuff_time, pellet_price,
            dtLastState_A, wheel_counter_A, turn_A, pellet_counter_A, limit_A, IDtag_A): #define function that runs everything for mouse A
    
    while True: #infinite loop
    
        if MODE_A == 0: 
            move_door_social('A') #move door to social position
            print("\nMODE_A 0\n")
            
            
        while MODE_A == 0:
            proximity_check_A = animal_in_tube('A') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_A == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1A: proximity detected')
                tag_A = RFID_check('A', protocol, IDtag_A) #checks RFID tag and returns bolean 
                    
                if tag_A == True: #CHECK 2: if it's mouse B, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2A: RFID ok')
                    how_many_A = scan_tube_entry('A', lines_to_chuck) #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_A == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3A: weight ok')
                        move_door_close('A') #close doors
                        which_mouse = 'A'
                        MODE_A = 1 #if all 3 checks succeed, assign value 1 to MODE variable
                            
                    else: #CHECK 3
                        print('check 3A fail: weight not >10 and <30g')
                        how_many_A = False
                        proximity_check_A = False
                        tag_A = False
                        pass
                    
                else: #CHECK 2
                    print('check 2A fail: wrong RFID tag')
                    tag_A = False
                    proximity_check_A = False
                    pass
                
            else: #CHECK 1
                proximity_check_A = False
                pass
                
        if MODE_A == 1:
            ser_A.close()
            print("\nMODE_A 1\n")
            mg_pre_mean_A = acquire_weight_pre('A', lines_to_chuck, protocol, IDtag_A) #acquires and saves the mean weight data
            move_door_feeding('A') #open door to feeding area
            
            while MODE_A == 1:
                MODE_A = wait_for_animal_to_leave_foor_feeding_area('A', lines_to_chuck) #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_A == 2:
            print("\nMODE_A 2\n")
            ser_A.close()

            if protocol == "OG": #MODE 2 code for the OG protocol
            
                while MODE_A == 2:
                    dtState_A = GPIO.input(dt_A) #read input from running wheel
                    returned_A = animal_in_tube('A') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_A == False: #if animal has not yet returned from feeding area, perform these functions
                        
                        if dtState_A != dtLastState_A: 
                            wheel_counter_A += 1 #running wheel rotation wheel_counter
                            dtLastState_A = dtState_A
                            
                            if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 160)
                                turn_A = wheel_counter_A/cycle_A
                                limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                                print("mouse A wheel turns: "+str(turn_A))
                                
                                if (turn_A % wheel_turns_OG == 0) and (turn_A != 0): #every X wheel turns (define parameter in beggining of code, default = 1)
                                    print("mouse A completed "+str(wheel_turns_OG)+" wheel turn(s), delivering pellet")
                                    GPIO.output(writeFED_A, True) #sends output to FED - turns FED motor on and makes pellet drop
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
                            GPIO.output(writeFED_A, False) #turns FED motor off
                            air_puff('A', airpuff_time) #delivers air puff to animal
                            pellet_counter_A += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse A returned. acquiring weight")
                        print("mouse A rotation counter: "+str(wheel_counter_A))
                        move_door_close('A') #close doors for proper weighting
                        append_rotation(IDtag_A, protocol, wheel_counter_A) #save running wheel rotation data
                        append_pellet(IDtag_A, protocol, pellet_counter_A) #save pellet data
                        
                        wheel_counter_A = 0 #reset wheel rotation counter
                        pellet_counter_A = 0 #reset pellet counter
                        turn_A = 0 #reset wheel turn counter
                        limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_A = dt_A #reset input from wheel 
                        
                        mg_post_mean_A = acquire_weight_post('A', lines_to_chuck, protocol, IDtag_A) #acquire weight and assign mean weight value
                        check_weight_post_A(mg_pre_mean_A, mg_post_mean_A) #compare weights pre and post and delivered stimulus
                        move_door_social('A') #open door to social area
                        animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_A == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everythiong again
                            print("mouse A: cycle over, starting again")
                            MODE_A = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping
                
            elif protocol == "PR": #MODE 2 code for the PR protocol

                move_door_close('A') #THIS WILL LOCK ANIMALS IN MODE 2 - LOCKING ANIMALS IN FEEDING AREAS
                while MODE_A == 2:
                    dtState_A = GPIO.input(dt_A) #read input from running wheel
                    returned_A = animal_in_tube('A') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_A == False: #if animal has not yet returned from feeding area, perform these functions
                        GPIO.output(writeFED_A, True) #sends output to FED - turns FED motor on and makes pellet drop
                        
                        if dtState_A != dtLastState_A: 
                            wheel_counter_A += 1 #running wheel rotation wheel_counter
                            dtLastState_A = dtState_A
                            
                            if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
                                turn_A = wheel_counter_A/cycle_A
                                limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                                print("mouse A wheel turns: "+str(turn_A))
                                
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
                            pellet_counter_A += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse A returned. acquiring weight")
                        print("mouse A rotation counter: "+str(wheel_counter_A))
                        move_door_close('A') #close doors for proper weighting
                        append_rotation(IDtag_A, protocol, wheel_counter_A) #save running wheel rotation data
                        append_pellet(IDtag_A, protocol, pellet_counter_A) #save pellet data
                        GPIO.output(writeFED_A, False) #send output to FED - turns FD motor off
                        
                        wheel_counter_A = 0 #reset wheel rotation counter
                        pellet_counter_A = 0 #reset pellet counter
                        turn_A = 0 #reset wheel turn counter
                        limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_A = dt_A #reset input from wheel 
                        
                        mg_post_mean_A = acquire_weight_post('A', lines_to_chuck, protocol, IDtag_A) #acquire weight and assign mean weight value
                        move_door_social('A') #open door to social area
                        animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_A == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everythiong again
                            print("mouse A: cycle over, starting again")
                            MODE_A = 2 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping


            elif protocol == "FBA": #MODE 2 code for the FBA protocol
                
                while MODE_A == 2:
                    dtState_A = GPIO.input(dt_A) #read input from running wheel
                    returned_A = animal_in_tube('A') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_A == False: #if animal has not yet returned from feeding area, perform these functions
                        GPIO.output(writeFED_A, True) #sends output to FED - turns FED motor on and makes pellet drop
                        
                        if dtState_A != dtLastState_A: 
                            wheel_counter_A += 1 #running wheel rotation wheel_counter
                            dtLastState_A = dtState_A
                            
                            if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
                                turn_A = wheel_counter_A/cycle_A
                                limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                                print("mouse A wheel turns: "+str(turn_A))
                                
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
                            air_puff('A', airpuff_time) #delivers air puff to animal
                            pellet_counter_A += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse A returned. acquiring weight")
                        print("mouse A rotation counter: "+str(wheel_counter_A))
                        move_door_close('A') #close doors for proper weighting
                        append_rotation(IDtag_A, protocol, wheel_counter_A) #save running wheel rotation data
                        append_pellet(IDtag_A, protocol, pellet_counter_A) #save pellet data
                        GPIO.output(writeFED_A, False) #sends output to FED - turns FED motor off

                        wheel_counter_A = 0 #reset wheel rotation counter
                        pellet_counter_A = 0 #reset pellet counter
                        turn_A = 0 #reset wheel turn counter
                        limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_A = dt_A #reset input from wheel 
                        
                        mg_post_mean_A = acquire_weight_post('A', lines_to_chuck, protocol, IDtag_A) #acquire weight and assign mean weight value
                        move_door_social('A') #open door to social area
                        animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_A == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everythiong again
                            print("mouse A: cycle over, starting again")
                            MODE_A = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping

            
            elif protocol == "CBA": #MODE 2 code for the CBA protocol
                
                while MODE_A == 2:
                    dtState_A = GPIO.input(dt_A) #read input from running wheel
                    returned_A = animal_in_tube('A') #checks if animal has returned from feeding area and store it as boolean
                    price_in_wheel_turns = price(pellet_price)
                    
                    if returned_A == False: #if animal has not yet returned from feeding area, perform these functions
                        
                        if dtState_A != dtLastState_A: 
                            wheel_counter_A += 1 #running wheel rotation wheel_counter
                            dtLastState_A = dtState_A
                            
                            if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
                                turn_A = wheel_counter_A/cycle_A
                                limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                                print("mouse A wheel turns: "+str(turn_A))
                                
                                if (turn_A % price_in_wheel_turns == 0) and (turn_A != 0): #each X revolutions
                                    print("mouse A completed  " + str(price_in_wheel_turns) + " wheel turns, delivering pellet")
                                    GPIO.output(writeFED_A, True) #sends output to FED - turns FED motor on and makes pellet drop
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
                            GPIO.output(writeFED_A, False) #turns FED motor off
                            pellet_counter_A += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse A returned. acquiring weight")
                        print("mouse A rotation counter: "+str(wheel_counter_A))
                        move_door_close('A') #close doors for proper weighting
                        append_rotation(IDtag_A, protocol, wheel_counter_A) #save running wheel rotation data
                        append_pellet(IDtag_A, protocol, pellet_counter_A) #save pellet data
                        
                        wheel_counter_A = 0 #reset wheel rotation counter
                        pellet_counter_A = 0 #reset pellet counter
                        turn_A = 0 #reset wheel turn counter
                        limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_A = dt_A #reset input from wheel 
                        
                        mg_post_mean_A = acquire_weight_post('A', lines_to_chuck, protocol, IDtag_A) #acquire weight and assign mean weight value
                        move_door_social('A') #open door to social area
                        animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_A == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everythiong again
                            print("mouse A: cycle over, starting again")
                            MODE_A = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping

            
            elif protocol == "WBA": #MODE 2 code for the WBA protocol

                while MODE_A == 2:
                    dtState_A = GPIO.input(dt_A) #read input from running wheel
                    returned_A = animal_in_tube('A') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_A == False: #if animal has not yet returned from feeding area, perform these functions
                        GPIO.output(writeFED_A, True) #send output to FED - turns motor on and makes pellet drop
                        
                        if dtState_A != dtLastState_A: 
                            wheel_counter_A += 1 #running wheel rotation wheel_counter
                            dtLastState_A = dtState_A
                            
                            if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
                                turn_A = wheel_counter_A/cycle_A
                                limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                                print("mouse A wheel turns: "+str(turn_A))
                                
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_A): #detects signal coming from the FED
                            GPIO.output(writeFED_A, False) #turns FED motor off
                            pellet_counter_A += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse A: "+str(pellet_counter_A))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse A returned. acquiring weight")
                        print("mouse A rotation counter: "+str(wheel_counter_A))
                        move_door_close('A') #close doors for proper weighting
                        append_rotation(IDtag_A, protocol, wheel_counter_A) #save running wheel rotation data
                        append_pellet(IDtag_A, protocol, pellet_counter_A) #save pellet data
                        GPIO.output(writeFED_A, False) #send output to FED - turns motor off
                        
                        wheel_counter_A = 0 #reset wheel rotation counter
                        pellet_counter_A = 0 #reset pellet counter
                        turn_A = 0 #reset wheel turn counter
                        limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_A = dt_A #reset input from wheel 
                        
                        mg_post_mean_A = acquire_weight_post('A', lines_to_chuck, protocol, IDtag_A) #acquire weight and assign mean weight value
                        check_weight_post_A(mg_pre_mean_A, mg_post_mean_A) #compare weights pre and post and delivered stimulus
                        move_door_social('A') #open door to social area
                        animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_A = scan_tube_leaving('A', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_A == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everythiong again
                            print("mouse A: cycle over, starting again")
                            MODE_A = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping



def mouse_B(MODE_B, protocol, wheel_turns_OG, lines_to_chuck, airpuff_time, pellet_price,
            dtLastState_B, wheel_counter_B, turn_B, pellet_counter_B, limit_B, IDtag_B): #define function that runs everything for mouse A
    
    while True: #infinite loop
    
        if MODE_B == 0: 
            move_door_social('B') #move door to social position
            print("\nMODE_B 0\n")
            
            
        while MODE_B == 0:
            proximity_check_B = animal_in_tube('B') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_B == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1B: proximity detected')
                tag_B = RFID_check('B', protocol, IDtag_B) #checks RFID tag and returns bolean 
                    
                if tag_B == True: #CHECK 2: if it's mouse B, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2B: RFID ok')
                    how_many_B = scan_tube_entry('B', lines_to_chuck) #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_B == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3B: weight ok')
                        move_door_close('B') #close doors
                        which_mouse = 'B'
                        MODE_B = 1 #if all 3 checks succeed, assign value 1 to MODE variable
                            
                    else: #CHECK 3
                        print('check 3B fail: weight not >10 and <30g')
                        how_many_B = False
                        proximity_check_B = False
                        tag_B = False
                        pass
                    
                else: #CHECK 2
                    print('check 2B fail: wrong RFID tag')
                    tag_B = False
                    proximity_check_B = False
                    pass
                
            else: #CHECK 1
                proximity_check_B = False
                pass
                
        if MODE_B == 1:
            ser_B.close()
            print("\nMODE_B 1\n")
            mg_pre_mean_B = acquire_weight_pre('B', lines_to_chuck, protocol, IDtag_B) #saves the mean weight data
            move_door_feeding('B') #open door to feeding area
            
            while MODE_B == 1:
                MODE_B = wait_for_animal_to_leave_foor_feeding_area('B', lines_to_chuck) #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_B == 2:
            print("\nMODE_B 2\n")
            ser_B.close()

            if protocol == "OG": #MODE 2 code for the OG protocol
            
                while MODE_B == 2:
                    dtState_B = GPIO.input(dt_B) #read input from running wheel
                    returned_B = animal_in_tube('B') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_B == False: #if animal has not yet returned from feeding area, perform these functions
                        
                        if dtState_B != dtLastState_B: 
                            wheel_counter_B += 1 #running wheel rotation wheel_counter
                            dtLastState_B = dtState_B
                            
                            if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
                                turn_B = wheel_counter_B/cycle_B
                                limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
                                print("mouse B wheel turns: "+str(turn_B))
                                
                                if (turn_B % wheel_turns_OG == 0) and (turn_B != 0): #every X wheel turns (define parameter in beggining of code, default = 1)
                                        print("mouse B completed "+str(wheel_turns_OG)+" wheel turn(s), delivering pellet")
                                        GPIO.output(writeFED_B, True) #sends output to FED - turnd FED motor on and makes pellet drop
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_B): #detects signal coming from the FED
                            GPIO.output(writeFED_B, False) #turns FED motor off
                            air_puff('B', airpuff_time) #delivers air puff to animal
                            pellet_counter_B += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse B returned. acquiring weight")
                        print("mouse B rotation counter: "+str(wheel_counter_B))
                        move_door_close('B') #close doors for proper weighting
                        append_rotation(IDtag_B, protocol, wheel_counter_B) #save running wheel rotation data
                        append_pellet(IDtag_B, protocol, pellet_counter_B) #save pellet data
                        
                        wheel_counter_B = 0 #reset wheel rotation counter
                        pellet_counter_B = 0 #reset pellet counter
                        turn_B = 0 #reset wheel turn counter
                        limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_B = dt_B #reset input from wheel 
                        
                        mg_post_mean_B = acquire_weight_post('B', lines_to_chuck, protocol, IDtag_B) #acquire weight and assign mean weight value
                        check_weight_post_B(mg_pre_mean_B, mg_post_mean_B) #compare weights pre and post and delivered stimulus
                        move_door_social('B') #open door to social area
                        animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_B == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everything again
                            print("mouse B: cycle over, starting again")
                            MODE_B = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping  

            elif protocol == "PR": #MODE 2 code for the PR protocol

                move_door_close('B') #THIS WILL LOCK ANIMALS IN MODE 2 - LOCKING ANIMALS IN FEEDING AREAS
                while MODE_B == 2:
                    dtState_B = GPIO.input(dt_B) #read input from running wheel
                    returned_B = animal_in_tube('B') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_B == False: #if animal has not yet returned from feeding area, perform these functions
                        GPIO.output(writeFED_B, True) #sends output to FED - turns motor on and makes pellet drop
                        
                        if dtState_B != dtLastState_B: 
                            wheel_counter_B += 1 #running wheel rotation wheel_counter
                            dtLastState_B = dtState_B
                            
                            if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
                                turn_B = wheel_counter_B/cycle_B
                                limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
                                print("mouse B wheel turns: "+str(turn_B))
                                
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_B): #detects signal coming from the FED
                            pellet_counter_B += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse B returned. acquiring weight")
                        print("mouse B rotation counter: "+str(wheel_counter_B))
                        move_door_close('B') #close doors for proper weighting
                        append_rotation(IDtag_B, protocol, wheel_counter_B) #save running wheel rotation data
                        append_pellet(IDtag_B, protocol, pellet_counter_B) #save pellet data
                        GPIO.output(writeFED_B, False) #send output to ED - turns motor off
                        
                        wheel_counter_B = 0 #reset wheel rotation counter
                        pellet_counter_B = 0 #reset pellet counter
                        turn_B = 0 #reset wheel turn counter
                        limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_B = dt_B #reset input from wheel 
                        
                        mg_post_mean_B = acquire_weight_post('B', lines_to_chuck, protocol, IDtag_B) #acquire weight and assign mean weight value
                        move_door_social('B') #open door to social area
                        animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_B == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everything again
                            print("mouse B: cycle over, starting again")
                            MODE_B = 2 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping


            elif protocol == "FBA": #MODE 2 code for the FBA protocol

                 while MODE_B == 2:
                    dtState_B = GPIO.input(dt_B) #read input from running wheel
                    returned_B = animal_in_tube('B') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_B == False: #if animal has not yet returned from feeding area, perform these functions
                        GPIO.output(writeFED_B, True) #send output to FED - turns motor on and makes pellet drop
                        
                        if dtState_B != dtLastState_B: 
                            wheel_counter_B += 1 #running wheel rotation wheel_counter
                            dtLastState_B = dtState_B
                            
                            if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
                                turn_B = wheel_counter_B/cycle_B
                                limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
                                print("mouse B wheel turns: "+str(turn_B))
                                
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_B): #detects signal coming from the FED
                            air_puff('B', airpuff_time) #delivers air puff to animal
                            pellet_counter_B += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse B returned. acquiring weight")
                        print("mouse B rotation counter: "+str(wheel_counter_B))
                        move_door_close('B') #close doors for proper weighting
                        append_rotation(IDtag_B, protocol, wheel_counter_B) #save running wheel rotation data
                        append_pellet(IDtag_B, protocol, pellet_counter_B) #save pellet data
                        GPIO.output(writeFED_B, False) #send output to FED - turns FED motor off
                        
                        wheel_counter_B = 0 #reset wheel rotation counter
                        pellet_counter_B = 0 #reset pellet counter
                        turn_B = 0 #reset wheel turn counter
                        limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_B = dt_B #reset input from wheel 
                        
                        mg_post_mean_B = acquire_weight_post('B', lines_to_chuck, protocol, IDtag_B) #acquire weight and assign mean weight value
                        move_door_social('B') #open door to social area
                        animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_B == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everything again
                            print("mouse B: cycle over, starting again")
                            MODE_B = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping


            elif protocol == "CBA": #MODE 2 code for the CBA protocol

                while MODE_B == 2:
                    dtState_B = GPIO.input(dt_B) #read input from running wheel
                    returned_B = animal_in_tube('B') #checks if animal has returned from feeding area and store it as boolean
                    price_in_wheel_turns = price(pellet_price)

                    if returned_B == False: #if animal has not yet returned from feeding area, perform these functions
                        
                        if dtState_B != dtLastState_B: 
                            wheel_counter_B += 1 #running wheel rotation wheel_counter
                            dtLastState_B = dtState_B
                            
                            if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
                                turn_B = wheel_counter_B/cycle_B
                                limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
                                print("mouse B wheel turns: "+str(turn_B))
                                
                                if (turn_B % price_in_wheel_turns == 0) and (turn_B != 0): #each X revolutions
                                    print("mouse B completed  " + str(price_in_wheel_turns) + " wheel turns, delivering pellet")
                                    GPIO.output(writeFED_B, True) #sends output to FED - turnd FED motor on and makes pellet drop
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_B): #detects signal coming from the FED
                            GPIO.output(writeFED_B, False) #turns FED motor off
                            pellet_counter_B += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse B returned. acquiring weight")
                        print("mouse B rotation counter: "+str(wheel_counter_B))
                        move_door_close('B') #close doors for proper weighting
                        append_rotation(IDtag_B, protocol, wheel_counter_B) #save running wheel rotation data
                        append_pellet(IDtag_B, protocol, pellet_counter_B) #save pellet data
                        
                        wheel_counter_B = 0 #reset wheel rotation counter
                        pellet_counter_B = 0 #reset pellet counter
                        turn_B = 0 #reset wheel turn counter
                        limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_B = dt_B #reset input from wheel 
                        
                        mg_post_mean_B = acquire_weight_post('B', lines_to_chuck, protocol, IDtag_B) #acquire weight and assign mean weight value
                        move_door_social('B') #open door to social area
                        animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_B == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everything again
                            print("mouse B: cycle over, starting again")
                            MODE_B = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping  


            elif protocol == "WBA": #MODE 2 code for the WBA protocol

                while MODE_B == 2:
                    dtState_B = GPIO.input(dt_B) #read input from running wheel
                    returned_B = animal_in_tube('B') #checks if animal has returned from feeding area and store it as boolean
                    
                    if returned_B == False: #if animal has not yet returned from feeding area, perform these functions
                        GPIO.output(writeFED_B, True) #send output to FED - turns motor on and makes pellet drop
                        
                        if dtState_B != dtLastState_B: 
                            wheel_counter_B += 1 #running wheel rotation wheel_counter
                            dtLastState_B = dtState_B
                            
                            if wheel_counter_B >= limit_B: #when completes 1 full turn (wheel_counter = 1200)
                                turn_B = wheel_counter_B/cycle_B
                                limit_B = wheel_counter_B + cycle_B #reset limit for 1 extra turn
                                print("mouse B wheel turns: "+str(turn_B))
                                
                            else:
                                pass
                        
                        elif GPIO.event_detected(read_FED_B): #detects signal coming from the FED
                            pellet_counter_B += 1 #counts one pellet
                            print("Pellet retrieved. Pellet counter for mouse B: "+str(pellet_counter_B))
                        
                        else:
                            pass
                        
                    
                    else: #if animal has returned from feeding area, perform these functions
                        print("mouse B returned. acquiring weight")
                        print("mouse B rotation counter: "+str(wheel_counter_B))
                        move_door_close('B') #close doors for proper weighting
                        append_rotation(IDtag_B, protocol, wheel_counter_B) #save running wheel rotation data
                        append_pellet(IDtag_B, protocol, pellet_counter_B) #save pellet data
                        GPIO.output(writeFED_B, False) #send output to FED - turns motor off
                        
                        wheel_counter_B = 0 #reset wheel rotation counter
                        pellet_counter_B = 0 #reset pellet counter
                        turn_B = 0 #reset wheel turn counter
                        limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                        dtLastState_B = dt_B #reset input from wheel 
                        
                        mg_post_mean_B = acquire_weight_post('B', lines_to_chuck, protocol, IDtag_B) #acquire weight and assign mean weight value
                        check_weight_post_B(mg_pre_mean_B, mg_post_mean_B) #compare weights pre and post and delivered stimulus
                        move_door_social('B') #open door to social area
                        animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                        
                        while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                            animal_left_B = scan_tube_leaving('B', lines_to_chuck) #scan tube to check whether animal is still in and stores info as boolean
                            
                        if animal_left_B == True: #if animal leaves the tube, perform these tasks
                            time.sleep(10) #10 seconds timeout before animal can do everything again
                            print("mouse B: cycle over, starting again")
                            MODE_B = 0 #MODE = 0 makes the code start again
                        else:
                            pass #if animal hasn't left tube yet, keep looping    

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
VARIABLES, PARAMETERS AND FUNCTIONS TO EXTRACT WEIGHT(12h) AND PELLET(3h)
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
#import datasets
weight_data = pd.read_csv("/home/pi/Documents/data/dummy_data/weight.csv")
pellet_data = pd.read_csv("/home/pi/Documents/data/dummy_data/pellet.csv")

#set tag variables
A = IDtag_A #put the RFID tag here
B = IDtag_B #put the RFID tag here
#WARNING: if the 'mouse_id' column in the datasets is identified as 'A' or 'B' (instead as their RFID tag number), the code will crash here
#in this case, swap IDtag_A for 'A' and IDtag_B for 'B'

#create datetime filters of the last hours
filt_12h = datetime.now() - timedelta(hours = 12)
filt_3h = datetime.now() - timedelta(hours = 3)
filt_5d = datetime.now() - timedelta(days = 5) #for testing only

#define funtion to convert datatypes of the datasets
def correct_data(weight_data, pellet_data): 
    weight_data.columns = [i.lower() for i in weight_data.columns] #put column names in lower case (easier to work with)
    pellet_data.columns = [i.lower() for i in pellet_data.columns] #put column names in lower case (easier to work with)
    weight_data['weight_mode'].replace('NO MODE', np.nan, inplace=True) #convert 'NO MODE' to NaN
    weight_data['weight_mean'] = weight_data['weight_mean'].astype(float) #convert column to float
    weight_data['weight_median'] = weight_data['weight_median'].astype(float) #convert column to float
    weight_data['weight_mode'] = weight_data['weight_mode'].astype(float) #convert column to float
    pellet_data['pellet'] = pellet_data['pellet'].astype(float) #convert column to float
    weight_data['date_time'] = pd.to_datetime(weight_data['date_time']) #convert date_time to column from string to datetime object
    pellet_data['date_time'] = pd.to_datetime(pellet_data['date_time']) #convert date_time to column from string to datetime object

#define functions that extract the mean weight of the last 12h
def weightA_12h(weight_data, A, filt_12h): #for mouse A
    weightA_filt = (weight_data['mouse_id'] == A) #create filter weight mouse A
    weightA = weight_data[weightA_filt] #apply filter
    filt_12h_weightA = weightA['date_time'] >= filt_12h #create mask series of boolean for the last 12h
    weightA_12h = weightA.loc[filt_12h_weightA] #apply mask series and create a dataset with only data of the last 12h
    weightA_12h_mean = weightA_12h['weight_mean'].mean() #get the mean
    return weightA_12h_mean

def weightB_12h(weight_data, B, filt_12h): #for mouse B
    weightB_filt = (weight_data['mouse_id'] == B) #create filter weight mouse B
    weightB = weight_data[weightB_filt] #apply filter
    filt_12h_weightB = weightB['date_time'] >= filt_12h #create mask series of boolean for the last 12h
    weightB_12h = weightB.loc[filt_12h_weightB] #apply mask series and create a dataset with only data of the last 12h
    weightB_12h_mean = weightB_12h['weight_mean'].mean() #get the mean
    return weightB_12h_mean


#define funtions that extract the mean pellets of the last 3h
def pelletA_3h(pellet_data, A, filt_3h): #for mouse A
    pelletA_filt = (pellet_data['mouse_id'] == A) #create filter pellet mouse A
    pelletA = pellet_data[pelletA_filt] #apply filter
    filt_3h_pelletA = pelletA['date_time'] >= filt_3h #create mask series of boolean for the last 3h
    pelletA_3h = pelletA.loc[filt_3h_pelletA] #apply mask series and create dataset with only data of the last 3h
    pelletA_3h_mean = pelletA_3h['pellet'].mean() #get the mean
    return pelletA_3h_mean

def pelletB_3h(pellet_data, B, filt_3h): #for mouse B
    pelletB_filt = (pellet_data['mouse_id'] == B) #create filter pellet mouse B
    pelletB = pellet_data[pelletB_filt] #apply filter
    filt_3h_pelletB = pelletB['date_time'] >= filt_3h #create mask series of boolean for the last 3h
    pelletB_3h = pelletB.loc[filt_3h_pelletB] #apply mask series and create dataset with only data of the last 3h
    pelletB_3h_mean = pelletB_3h['pellet'].mean() #get the mean
    return pelletB_3h_mean

#define functions that extract the mean weight of the last 5d !!!!!FOR TESTING ONLY!!!!!
def weightA_5d(weight_data, A, filt_5d): #for mouse A
    weightA_filt = (weight_data['mouse_id'] == A) #create filter weight mouse A
    weightA = weight_data[weightA_filt] #apply filter
    filt_5d_weightA = weightA['date_time'] >= filt_5d #create mas series of boolean for the last 5 days
    weightA_5d = weightA.loc[filt_5d_weightA] #apply mas series and create datasheet with only data of the last 5 days
    weightA_5d_mean = weightA_5d['weight_mean'].mean() #get the mean
    return  weightA_5d_mean

def weightB_5d(weight_data, A, filt_5d): #for mouse B
    weightB_filt = (weight_data['mouse_id'] == B) #create filter weight mouse B
    weightB = weight_data[weightB_filt] #apply filter
    filt_5d_weightB = weightB['date_time'] >= filt_5d #create mas series of boolean for the last 5 days
    weightB_5d = weightB.loc[filt_5d_weightB] #apply mas series and create datasheet with only data of the last 5 days
    weightB_5d_mean = weightB_5d['weight_mean'].mean() #get the mean
    return  weightB_5d_mean   
                    
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
#close all RFID antennas serial ports
RFID_A.close()
RFID_B.close()
#close all OpenScales seria ports
ser_A.close()
ser_B.close()
#turn signal to al FEDs low
GPIO.output(writeFED_A, False)
GPIO.output(writeFED_B, False)
#turn signal to all air puffs low
GPIO.output(airpuff_A, False)
GPIO.output(airpuff_B, False)
#turn signal to all feedback LEDs low
GPIO.output(gLED_A, False) #green LED mouse A off
GPIO.output(rLED_A, False) #red LED mouse A off
GPIO.output(gLED_B, False) #green LED mouse B off
GPIO.output(rLED_B, False) #red LED mouse B off
#set MODE variables
MODE_A = 0
MODE_B = 0

print("/n STARTING THREADS /n")

#create thread objects
thread_A = threading.Thread(target=mouse_A, args=(MODE_A, protocol, wheel_turns_OG, lines_to_chuck, airpuff_time, pellet_price, dtLastState_A, wheel_counter_A, turn_A, pellet_counter_A, limit_A, IDtag_A,))
thread_B = threading.Thread(target=mouse_B, args=(MODE_B, protocol, wheel_turns_OG, lines_to_chuck, airpuff_time, pellet_price, dtLastState_B, wheel_counter_B, turn_B, pellet_counter_B, limit_B, IDtag_B,))
#initialize thread objects   
thread_A.start() #start thread for mouse A
thread_B.start() #start thread for mouse B

# because first two threaded functions contain infinite while loops inside them, an infinite while loop for the execution cannot be used
# they will run indefinitely, once started

while True: #infinite loop to constatly run these functions - these variables will inform the mean weight(last 12h) and pellet(last 3h)
    correct_data(weight_data, pellet_data)
    mean_weight_12hA = weightA_12h(weight_data, A, filt_12h)
    mean_weight_12hB = weightB_12h(weight_data, B, filt_12h)
    mean_pellet_3hA = pelletA_3h(pellet_data, A, filt_3h)
    mean_pellet_3hB = pelletB_3h(pellet_data, B, filt_3h)
    mean_weight_5dA = weightA_5d(weight_data, A, filt_5d)
    mean_weight_5dB = weightB_5d(weight_data, A, filt_5d)
