#import libraries
import os
import time
import serial
import threading
import pandas as pd
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

''' set door pins '''
#mouse A
PdA_food = 3
PdA_social = 5
GPIO.setup(PdA_food,GPIO.OUT)
GPIO.setup(PdA_social, GPIO.OUT)
GPIO.output(PdA_food,False)
GPIO.output(PdA_social, True) #SOCIAL position

#mouse B
PdB_food = 7
PdB_social = 11
GPIO.setup(PdB_food,GPIO.OUT)
GPIO.setup(PdB_social, GPIO.OUT)
GPIO.output(PdB_food,False)
GPIO.output(PdB_social, True) #SOCIAL position

''' set pins for buzzers and LEDs '''
#buzzer tones
heavier_buzz_1 = 700
heavier_buzz_2 = 589
not_heavier_buzz_1 = 131
not_heavier_buzz_2 = 165

#mouse A
#set pin output to buzzer and LEDs
gLED_A = 22
rLED_A = 24
buzzer_A = 26
GPIO.setup(gLED_A, GPIO.OUT)
GPIO.setup(rLED_A, GPIO.OUT)
GPIO.setup(buzzer_A, GPIO.OUT)
buzz_A = GPIO.PWM(buzzer_A, 1) #starting frequency is 1 (inaudible)
GPIO.setup(gLED_A, GPIO.OUT)
GPIO.setup(rLED_A, GPIO.OUT)
GPIO.output(gLED_A, False)
GPIO.output(rLED_A,False)

#mouse B
gLED_B = 36
rLED_B = 32
buzzer_B = 40
GPIO.setup(gLED_B, GPIO.OUT)
GPIO.setup(rLED_B, GPIO.OUT)
GPIO.setup(buzzer_B, GPIO.OUT)
buzz_B = GPIO.PWM(buzzer_B, 1) #starting frequency is 1 (inaudible)
GPIO.setup(gLED_B, GPIO.OUT)
GPIO.setup(rLED_B, GPIO.OUT)
GPIO.output(gLED_B, False)
GPIO.output(rLED_B,False)

''' set pins for running wheel '''
#mouse A
#set pin inputs from running wheel rotary encoder and initialize variables
dt_A = 12
GPIO.setup(dt_A, GPIO.IN)
dtLastState_A = GPIO.input(dt_A)
wheel_counter_A = 0;
cycle_A = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_A = cycle_A;
turn_A = 0;

#mouse B
#set pin inputs from running wheel rotary encoder and initialize variables
dt_B = 15
GPIO.setup(dt_B, GPIO.IN)
dtLastState_B = GPIO.input(dt_B)
wheel_counter_B = 0;
cycle_B = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_B = cycle_B;
turn_B = 0;

''' set pins for IR proximity detectors '''
#mouse A
#set pins for beam break (flying fish) proximity scanner
IR_A = 8
GPIO.setup(IR_A, GPIO.IN)

#mouse B
#set pins for beam break (flying fish) proximity scanner
IR_B = 13
GPIO.setup(IR_B, GPIO.IN)

''' sets pins for sending commands to the FED (Pi --> FED) '''
#mouse A
#set pins for output to FED_A
writeFED_A = 18
GPIO.setup(writeFED_A, GPIO.OUT)
GPIO.output(writeFED_A, False)

#mouse B
#set pins for output to FED_B
writeFED_B = 21
GPIO.setup(writeFED_B, GPIO.OUT)
GPIO.output(writeFED_B, False)

''' set pins for reading input from FED (FED --> Pi) '''
#mouse A
#set pin for input from FED_A
read_FED_A = 16
GPIO.setup(read_FED_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #CHANGING HERE
GPIO.add_event_detect(read_FED_A, GPIO.RISING) #detects rising voltage
pellet_counter_A = 0

#mouse B
#set pin for input from FED_B
read_FED_B = 19
GPIO.setup(read_FED_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(read_FED_B, GPIO.RISING) #detects rising voltage
pellet_counter_B = 0

''' set pins for air puffs '''
#mouse A
airpuff_A = 33
GPIO.setup(airpuff_A, GPIO.OUT)
GPIO.output(airpuff_A, False)

#mouse B
airpuff_B = 35
GPIO.setup(airpuff_B, GPIO.OUT)
GPIO.setup(airpuff_B, False)

'''initialize MODE variable'''
MODE_A = 0
MODE_B = 0

lines_to_chuck = 15

protocol = "CBA" #specify the protocol
'''
"OG" = original, refers to the base code (double_trouble_thread_NOHAT.py)
"PR" = practice mode, animals have full access to food and no feedback of any kind (PR_mode_AB.py) 
"FBA" = fear based anorexia (FBA_mode_AB.py)
"CBA" = cost based anorexia (CBA_mode_AB.py)
"WBA" = weight based anorexia (WBA_mode_AB.py)
'''

print("please define pellet price (in wheel turns): \n 0 = 1 \n 1 = 5 \n 2 = 10 \n 3 = 25 \n 4 = 50 \n 5 = 100 ")

pellet_price = input()

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
                tag = tag_as_list_2[1] #atfer processing data from RFID antenna, stores it in tag
        
            if tag == '020077914A15B9' or tag == '0077914A15B9':
                print("mouse A detected")
                which_mouse = "A"
                ID_tag = "mouse A"
                protocol = "CBA"
                append_RFID(which_mouse, protocol, tag)
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
                protocol = "CBA"
                append_RFID(which_mouse, protocol, tag)
                return True
            else:
                print("not mouse B")
                return False
        
        RFID_B.close()
        
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

def scan_tube_entry(X): #define function to check wether there is only one animal in scale
    animal_enter = False
    animal_alone = False
    global lines_to_chuck
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        
        for _ in range(lines_to_chuck):
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
        
        for _ in range(lines_to_chuck):
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
    else:
        print('something wrong. find me: scan_tube_entry(X)')
        
'''
MODE 1 FUNCTIONS ########################################################################################
'''

def acquire_weight_pre(X): #define function to acquire and sotre weight data
    
    global lines_to_chuck
    
    if X == 'A':
        print("acquiring weight PRE - mouse A")
        openscale = [] #store weights here
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(lines_to_chuck): # chuck two lines 
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
        
            mouse = 'A' #mouse ID
            when = 'pre' #specify if pre pre or post
            protocol = "CBA" #specifiy which protocol is being used
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
        for _ in range(lines_to_chuck): # chuck two lines 
            line = ser_B.readline()   
        for x in range(100): # 100 lines*120ms per line=12s of data
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
        
            mouse = 'B' #mouse ID
            when = 'pre' #specify if pre pre or post
            protocol = "CBA" #specifiy which protocol is being used
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

def wait_for_animal_to_leave_foor_feeding_area(X): #define function for determining if animal has left the tube
    
    animal_out = False
    global lines_to_chuck
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        
        for _ in range(lines_to_chuck):
            line = ser_A.readline()
        
        while animal_out == False:
                    
            line = ser_A.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
        
            if mg < float(10):
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
        
        for _ in range(lines_to_chuck):
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
            
    else:
        print('something wrong. find me: wait_for_animal_to_leave_foor_feeding_area(X)')

'''
MODE 2 FUNCTIONS ########################################################################################
'''

def acquire_weight_post(X): #define function to acquire and save weight data
    
    global lines_to_chuck
    
    if X == 'A':
        openscale = [] #store weights here
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(lines_to_chuck): # chuck two lines 
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
        
            mouse = 'A' #ID
            when = 'post' #specify if pre or post
            protocol = "CBA" #specifiy which protocol is being used
            weight_data_mean = stats.mean(openscale) #mean
            weight_data_median = stats.median(openscale) #median
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
        for _ in range(lines_to_chuck): # chuck two lines 
            line = ser_B.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data
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
        
            mouse = 'B' #ID
            when = 'post' #specify if pre or post
            protocol = "CBA" #specifiy which protocol is being used
            weight_data_mean = stats.mean(openscale) #mean
            weight_data_median = stats.median(openscale) #median
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
    
    if mg_post_mean_A > mg_pre_mean_A:
        print("mouse A is heavier than before. initializing buzzer")
        bad_buzz('A')
        air_puff('A')
        
    else:
        print("mouse A is not havier than before. opening door")
        good_buzz('A')
    
    GPIO.output(airpuff_A, False) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function
        
def check_weight_post_B(mg_pre_mean_B, mg_post_mean_B): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_B > mg_pre_mean_B:
        print("mouse B is heavier than before. initializing buzzer")
        bad_buzz('B')
        air_puff('B')
        
    else:
        print("mouse B is not havier than before. opening door")
        good_buzz('B')
    
    GPIO.output(airpuff_B, False) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function

def air_puff(X): #define function for delivering air puff
    
    if X == 'A':
        GPIO.output(airpuff_A, True) #turns air puff ON
        time.sleep(1.5) #waits for 1.5 seconds
        GPIO.output(airpuff_A, False) #turns air puff OFF
        
    elif X == 'B':
        GPIO.output(airpuff_B, True) #turns air puff ON
        time.sleep(1.5)
        GPIO.output(airpuff_B, False) #turns air puff OFF
    
    else:
        print('something wrong. find me: air_puff(X)')
        
    GPIO.output(airpuff_A, False) #turns air puff OFF
    GPIO.output(airpuff_B, False) #turns air puff OFF  #this is to ensure both air puffs are off by the end of the function

def bad_buzz(X): #define funtion to be executed when animal is heaveir than chosen weight treshold

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
        
def good_buzz(X): #define funtion to be executed when animal is heaveir than chosen weight treshold
    
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
        
def scan_tube_leaving(X): #define function for checking if animal has left the scale
    
    animal_left = False
    global lines_to_chuck
    
    if X == 'A':
        ser_A.close()
        ser_A.open()
        ser_A.flush()
        for _ in range(lines_to_chuck):
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
        for _ in range(lines_to_chuck):
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
            
    else:
        print('something wrong. find me: scan_tube_leaving(X)')

def append_rotation(X, protocol, wheel_counter): #define function for storing wheel data
    
    rotation_list = {
    "Mouse_ID" : [],
    "Protocol" : [],
    "Rotation" : [],
    "Date_Time" : []
    }
    
    rotation_list.update({"Mouse_ID" : [X]})
    rotation_list.update({"Protocol" : [protocol]})
    rotation_list.update({"Rotation" : [wheel_counter]})
    rotation_list.update({"Date_Time" : [datetime.now()]})
    
    df_r = pd.DataFrame(rotation_list)
    print(df_r)
    
    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
def append_pellet(X, protocol, pellet_counter):#define function for storing pellet retrieval data
    
    pellet_list = {
    "Mouse_ID" : [],
    "Protocol" : [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Mouse_ID" : [X]})
    pellet_list.update({"Protocol" : [protocol]})
    pellet_list.update({"Pellet": [pellet_counter]})
    pellet_list.update({"Date_Time": [datetime.now()]})

    df_p = pd.DataFrame(pellet_list)
    print(df_p)

    if not os.path.isfile("pellet.csv"):
        df_p.to_csv("pellet.csv", encoding = "utf-8-sig", index = False)
    else:
        df_p.to_csv("pellet.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)

def price(pellet_price):

    if pellet_price == '0':
        return 1
    elif pellet_price == '1':
        return 5
    elif pellet_price == '2':
        return 10
    elif pellet_price == '3':
        return 25
    elif pellet_price == '4':
        return 50
    elif pellet_price == '5':
        return 100    

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
    global protocol
    
    while True:
    
        if MODE_A == 0: 
            move_door_social('A')
            print("\nMODE_A 0\n")
            
            
        while MODE_A == 0:
            proximity_check_A = animal_in_tube('A') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_A == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1A: proximity detected')
                tag_A = RFID_check('A') #checks RFID tag and returns bolean 
                    
                if tag_A == True: #CHECK 2: if it's mouse B, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2A: RFID ok')
                    how_many_A = scan_tube_entry('A') #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_A == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3A: weight ok')
                        move_door_close('A') #close doors
                        which_mouse = 'A'
                        MODE_A = 1 
                            
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
            mg_pre_mean_A = acquire_weight_pre('A') #saves the mean weight data
            move_door_feeding('A') #open door to feeding area
            
            while MODE_A == 1:
                MODE_A = wait_for_animal_to_leave_foor_feeding_area('A') #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_A == 2:
            print("\nMODE_A 2\n")
            ser_A.close()
            
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
                            
                            if (turn_A % int(price_in_wheel_turns) == 0) and (turn_A != 0): #each X revolutions
                                print("mouse A completed  " + str(price_in_wheel_turns) + " wheel turns, delivering pellet")
                                GPIO.output(writeFED_A, True) #sends output to FED - turnd FED motor on and makes pellet drop
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
                    append_rotation('A', protocol, wheel_counter_A) #save running wheel rotation data
                    append_pellet('A', protocol, pellet_counter_A) #save pellet data
                    
                    wheel_counter_A = 0 #reset wheel rotation counter
                    pellet_counter_A = 0 #reset pellet counter
                    turn_A = 0 #reset wheel turn counter
                    limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                    dtLastState_A = dt_A #reset input from wheel 
                    
                    mg_post_mean_A = acquire_weight_post('A') #acquire weight and assign mean weight value
                    move_door_social('A') #open door to social area
                    animal_left_A = scan_tube_leaving('A') #scan tube to check whether animal is still in and stores info as boolean
                    
                    while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                        animal_left_A = scan_tube_leaving('A') #scan tube to check whether animal is still in and stores info as boolean
                        
                    if animal_left_A == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
#                         move_door_close('A') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse A: cycle over, starting again")
                        MODE_A = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping

def mouse_B(MODE_B): #define function that runs everything for mouse A
    
    global dtLastState_B
    global wheel_counter_B
    global turn_B
    global pellet_counter_B
    global limit_B
    global protocol
    
    while True:
    
        if MODE_B == 0: 
            move_door_social('B')
            print("\nMODE_B 0\n")
            
            
        while MODE_B == 0:
            proximity_check_B = animal_in_tube('B') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_B == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1B: proximity detected')
                tag_B = RFID_check('B') #checks RFID tag and returns bolean 
                    
                if tag_B == True: #CHECK 2: if it's mouse B, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2B: RFID ok')
                    how_many_B = scan_tube_entry('B') #checks weight to confirm it's only 1 mouse and return boolean
                                
                    if how_many_B == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3B: weight ok')
                        move_door_close('B') #close doors
                        which_mouse = 'B'
                        MODE_B = 1 
                            
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
            mg_pre_mean_B = acquire_weight_pre('B') #saves the mean weight data
            move_door_feeding('B') #open door to feeding area
            
            while MODE_B == 1:
                MODE_B = wait_for_animal_to_leave_foor_feeding_area('B') #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
            
        if MODE_B == 2:
            print("\nMODE_B 2\n")
            ser_B.close()

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
                            
                            if turn_B % int(price_in_wheel_turns) == 0 and turn_B != 0: #each X revolutions
                                print("mouse A completed " + str(price_in_wheel_turns) + " wheel turns, delivering pellet")
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
                    append_rotation('B', protocol, wheel_counter_B) #save running wheel rotation data
                    append_pellet('B', protocol, pellet_counter_B) #save pellet data
                    
                    wheel_counter_B = 0 #reset wheel rotation counter
                    pellet_counter_B = 0 #reset pellet counter
                    turn_B = 0 #reset wheel turn counter
                    limit_B = cycle_B #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                    dtLastState_B = dt_B #reset input from wheel 
                    
                    mg_post_mean_B = acquire_weight_post('B') #acquire weight and assign mean weight value
                    move_door_social('B') #open door to social area
                    animal_left_B = scan_tube_leaving('B') #scan tube to check whether animal is still in and stores info as boolean
                    
                    while animal_left_B == False: #while the animal is still on the tube, perform thee tasks
                        animal_left_B = scan_tube_leaving('B') #scan tube to check whether animal is still in and stores info as boolean
                        
                    if animal_left_B == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
#                         move_door_close('B') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse B: cycle over, starting again")
                        MODE_B = 0 #MODE = 0 makes the code start again
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
#set MODE variables
MODE_A = 0
MODE_B = 0

#create thread objects
thread_A = threading.Thread(target=mouse_A, args=(MODE_A,))
thread_B = threading.Thread(target=mouse_B, args=(MODE_B,))
#initialize thread objects   
thread_A.start()
thread_B.start()