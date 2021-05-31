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
turns=1 #turns of wheel for pellet
'''set GPIO numbering mode'''
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

''' set serial ports for getting OpenScale data '''
#initialize serial port for OpenScale mouse C
ser_C = serial.Serial()
ser_C.port = '/dev/ttyUSB0' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_C.baudrate = 9600
ser_C.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_C.close()
ser_C.open()
ser_C.flush()
if ser_C.is_open==True:
    print("\nScale A ok. Configuration:\n")
    print(ser_C, "\n") #print serial parameters
ser_C.close()

#initialize serial port for OpenScale mouse D
ser_D = serial.Serial()
ser_D.port = '/dev/ttyUSB1' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_D.baudrate = 9600
ser_D.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_D.close()
ser_D.open()
ser_D.flush()
if ser_D.is_open==True:
    print("\nScale B ok. Configuration:\n")
    print(ser_D, "\n") #print serial parameters
ser_D.close()

''' set serial ports for getting RFID antenna signal '''
#initialize serial port for RFID reader mouse C
RFID_C = serial.Serial()
RFID_C.port = '/dev/ttyS0' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
RFID_C.baudrate = 9600
RFID_C.timeout = 100000 # we do not want the device to timeout
# test device connection
RFID_C.close()
RFID_C.open()
RFID_C.flush()
if RFID_C.is_open==True:
    print("\nRFID reader A ok. Configuration:\n")
    print(RFID_C, "\n") #print serial parameters
RFID_C.close()

#initialize serial port for RFID reader mouse D
RFID_D = serial.Serial()
RFID_D.port = '/dev/ttyAMA1' #RFID antenna serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
RFID_D.baudrate = 9600
RFID_D.timeout = 100000 # we do not want the device to timeout
# test device connection
RFID_D.close()
RFID_D.open()
RFID_D.flush()
if RFID_D.is_open==True:
    print("\nRFID reader B ok. Configuration:\n")
    print(RFID_D, "\n") #print serial parameters
RFID_D.close()

''' set door pins '''
#mouse C
PdA_food = 3
PdA_social = 5
GPIO.setup(PdA_food,GPIO.OUT)
GPIO.setup(PdA_social, GPIO.OUT)
GPIO.output(PdA_food,False)
GPIO.output(PdA_social, True) #SOCIAL position

#mouse D
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

#mouse C
#set pin output to buzzer and LEDs
gLED_C = 22
rLED_C = 24
buzzer_C = 26
GPIO.setup(gLED_C, GPIO.OUT)
GPIO.setup(rLED_C, GPIO.OUT)
GPIO.setup(buzzer_C, GPIO.OUT)
buzz_C = GPIO.PWM(buzzer_C, 1) #starting frequency is 1 (inaudible)
GPIO.setup(gLED_C, GPIO.OUT)
GPIO.setup(rLED_C, GPIO.OUT)
GPIO.output(gLED_C, False)
GPIO.output(rLED_C,False)

#mouse D
gLED_D = 36
rLED_D = 32
buzzer_D = 40
GPIO.setup(gLED_D, GPIO.OUT)
GPIO.setup(rLED_D, GPIO.OUT)
GPIO.setup(buzzer_D, GPIO.OUT)
buzz_D = GPIO.PWM(buzzer_D, 1) #starting frequency is 1 (inaudible)
GPIO.setup(gLED_D, GPIO.OUT)
GPIO.setup(rLED_D, GPIO.OUT)
GPIO.output(gLED_D, False)
GPIO.output(rLED_D,False)

''' set pins for running wheel '''
#mouse C
#set pin inputs from running wheel rotary encoder and initialize variables
dt_C = 12
GPIO.setup(dt_C, GPIO.IN)
dtLastState_C = GPIO.input(dt_C)
wheel_counter_C = 0;
cycle_C = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_C = cycle_C;
turn_C = 0;

#mouse D
#set pin inputs from running wheel rotary encoder and initialize variables
dt_D = 15
GPIO.setup(dt_D, GPIO.IN)
dtLastState_D = GPIO.input(dt_D)
wheel_counter_D = 0;
cycle_D = 160; #calibration value (1200 for old wheels, 160 for new ones)
limit_D = cycle_D;
turn_D = 0;

''' set pins for IR proximity detectors '''
#mouse C
#set pins for beam break (flying fish) proximity scanner
IR_C = 8
GPIO.setup(IR_C, GPIO.IN)

#mouse D
#set pins for beam break (flying fish) proximity scanner
IR_D = 13
GPIO.setup(IR_D, GPIO.IN)

''' sets pins for sending commands to the FED (Pi --> FED) '''
#mouse C
#set pins for output to FED_C
writeFED_C = 18
GPIO.setup(writeFED_C, GPIO.OUT)
GPIO.output(writeFED_C, False)

#mouse D
#set pins for output to FED_D
writeFED_D = 21
GPIO.setup(writeFED_D, GPIO.OUT)
GPIO.output(writeFED_D, False)

''' set pins for reading input from FED (FED --> Pi) '''
#mouse C
#set pin for input from FED_C
read_FED_C = 16
GPIO.setup(read_FED_C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #CHANGING HERE
GPIO.add_event_detect(read_FED_C, GPIO.RISING) #detects rising voltage
pellet_counter_C = 0

#mouse D
#set pin for input from FED_D
read_FED_D = 19
GPIO.setup(read_FED_D, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(read_FED_D, GPIO.RISING) #detects rising voltage
pellet_counter_D = 0

''' set pins for air puffs '''
#mouse C
airpuff_C = 33
GPIO.setup(airpuff_C, GPIO.OUT)
GPIO.output(airpuff_C, False)

#mouse D
airpuff_D = 35
GPIO.setup(airpuff_D, GPIO.OUT)
GPIO.setup(airpuff_D, False)

'''initialize MODE variable'''
MODE_C = 0
MODE_D = 0

lines_to_chuck = 15

protocol = "WBA" #specify the protocol
'''
"OG" = original, refers to the base code (double_trouble_thread_NOHAT_C&D.py)
"PR" = practice mode, animals have full access to food and no feedback of any kind (PR_mode_CD.py)
"FBA" = fear based anorexia (FBA_mode_CD.py)
"CBA" = cost based anorexia (CBA_mode_CD.py)
"WBA" = weight based anorexia (WBA_mode_CD.py)
""
'''

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
    
    if X == 'C':
        PdA_food_OFF = GPIO.output(PdA_food, False)
        PdA_social_ON = GPIO.output(PdA_social, True)
        PdA_food_OFF; PdA_social_ON #SOCIAL position
    
    elif X == 'D':
        PdB_food_OFF = GPIO.output(PdB_food, False)
        PdB_social_ON = GPIO.output(PdB_social, True)
        PdB_food_OFF; PdB_social_ON #SOCIAL position

def move_door_feeding(X):#define function for seting door at feeding position
    
    if X == 'C': 
        PdA_food_ON = GPIO.output(PdA_food, True)
        PdA_social_OFF = GPIO.output(PdA_social, False)
        PdA_food_ON; PdA_social_OFF #FEEDING position
    
    elif X == 'D':
        PdB_food_ON = GPIO.output(PdB_food, True)
        PdB_social_OFF = GPIO.output(PdB_social, False)
        PdB_food_ON; PdB_social_OFF #FEEDING position

def move_door_close(X):#define function for seting door at neutral position
    
    if X == 'C':
        PdA_food_OFF = GPIO.output(PdA_food, False)
        PdA_social_OFF = GPIO.output(PdA_social, False)
        PdA_food_OFF; PdA_social_OFF #NEUTRAL position
    
    elif X == 'D':
        PdB_food_OFF = GPIO.output(PdB_food, False)
        PdB_social_OFF = GPIO.output(PdB_social, False)
        PdB_food_OFF; PdB_social_OFF #NEUTRAL position

def animal_in_tube(X): #define function that determine whether animal has entered scale and return boolean
    
    if X == 'C':
        IR_sensor = GPIO.input(IR_C)
    elif X == 'D':
        IR_sensor = GPIO.input(IR_D)
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
    
    if X == 'C':
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
        
            if tag == '020077914A15B9' or tag == '0077914A15B9':
                print("mouse C detected")
                which_mouse = "A"
                ID_tag = "mouse C"
                protocol = "WBA"
                append_RFID(which_mouse, protocol, tag)
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
            
            if tag == '0200779148D977' or tag == '00779148D977':
                print("mouse D detected")
                which_mouse = "B"
                ID_tag = "mouse D"
                protocol = "WBA"
                append_RFID(which_mouse, protocol, tag)
                return True
            else:
                print("not mouse D")
                return False
        
        RFID_D.close()
        
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
    
    if X == 'C':
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        
        for _ in range(lines_to_chuck):
            line = ser_C.readline()
        
        while animal_enter == False and animal_alone == False:
            line = ser_C.readline()
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
        
        for _ in range(lines_to_chuck):
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
    
    global lines_to_chuck
    
    if X == 'C':
        print("acquiring weight PRE - mouse C")
        openscale = [] #store weights here
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        for _ in range(lines_to_chuck): # chuck two lines 
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
        
            mouse = 'C' #mouse ID
            when = 'pre' #specify if pre pre or post
            protocol = "WBA" #specifiy which protocol is being used - OG = original (base code)
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
        print("mouse C weight data saved. opening door.")
#         ser_C.close()
        return weight_data_mean
        
    elif X == 'D':
        print("acquiring weight PRE - mouse D")
        openscale = [] #store weights here
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        for _ in range(lines_to_chuck): # chuck two lines 
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
        
            mouse = 'D' #mouse ID
            when = 'pre' #specify if pre pre or post
            protocol = "WBA" #specifiy which protocol is being used - OG = original (base code)
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
        print("mouse D weight data saved. opening door.")
        ser_D.close()
        return weight_data_mean   

    else:
        print('something wrong. find me: acquire_weight_pre(X)')

def wait_for_animal_to_leave_foor_feeding_area(X): #define function for determining if animal has left the tube
    
    animal_out = False
    global lines_to_chuck
    
    if X == 'C':
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        
        for _ in range(lines_to_chuck):
            line = ser_C.readline()
        
        while animal_out == False:
                    
            line = ser_C.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg = relProb_float*1000
        
            if mg < float(10):
                animal_out = True
                print("mouse C left for feeding area")
                ser_C.close()
                return 2 #return value to be assigned to MODE_C
            else:
                animal_out = False
                return 1       
        
    elif X == 'D':
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        
        for _ in range(lines_to_chuck):
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
                return 2 #return value to be assigned to MODE_C
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
    
    if X == 'C':
        openscale = [] #store weights here
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        for _ in range(lines_to_chuck): # chuck two lines 
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
        
            mouse = 'C' #ID
            when = 'post' #specify if pre or post
            protocol = "WBA" #specifiy which protocol is being used - OG = original (base code)
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
        ser_C.close()
        
        #return values for comparison
        return mg_post_mean
        
    elif X == 'D':
        openscale = [] #store weights here
        ser_D.close()
        ser_D.open()
        ser_D.flush()
        for _ in range(lines_to_chuck): # chuck two lines 
            line = ser_D.readline()
        
        for x in range(100): # 100 lines*120ms per line=12s of data
            ''' RANGE 10 HERE BECAUSE OPSEN SCALE 2 IS REPORTING TOO SLOWLY! CHANGE BACK TO 100 WHEN THAT'S FIXED'''
            line = ser_D.readline()
            line_as_list = line.split(b',')
            relProb = line_as_list[0]
            relProb_as_list = relProb.split(b'\n')
            relProb_float = float(relProb_as_list[0])
            mg_post = relProb_float*1000
            openscale.append(mg_post)
            print("mouse D weight in grams POST: "+str(mg_post))

            for i in range(len(openscale)):   #in case mode is not important, delete
                openscale[i] = round(openscale[i],3)
        
            mouse = 'D' #ID
            when = 'post' #specify if pre or post
            protocol = "WBA" #specifiy which protocol is being used - OG = original (base code)
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
        ser_D.close()
        
        #return values for comparison
        return mg_post_mean
    
    else:
        print('something wrong. find me: acquire_weight_post(X)')
        
def check_weight_post_C(mg_pre_mean_C, mg_post_mean_C): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_C > mg_pre_mean_C:
        print("mouse C is heavier than before. initializing buzzer")
        bad_buzz('C')
        air_puff('C')
        
    else:
        print("mouse C is not havier than before. opening door")
        good_buzz('C')
    
    GPIO.output(airpuff_C, False) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function
        
def check_weight_post_D(mg_pre_mean_D, mg_post_mean_D): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean_D > mg_pre_mean_D:
        print("mouse D is heavier than before. initializing buzzer")
        bad_buzz('D')
        air_puff('D')
        
    else:
        print("mouse D is not havier than before. opening door")
        good_buzz('D')
    
    GPIO.output(airpuff_D, False) #turns air puff OFF #this is to ensure both air puffs are off by the end of the function

def air_puff(X): #define function for delivering air puff
    
    if X == 'C':
        GPIO.output(airpuff_C, True) #turns air puff ON
        time.sleep(1.5) #waits for 1.5 seconds
        GPIO.output(airpuff_C, False) #turns air puff OFF
        
    elif X == 'D':
        GPIO.output(airpuff_D, True) #turns air puff ON
        time.sleep(1.5)
        GPIO.output(airpuff_D, False) #turns air puff OFF
    
    else:
        print('something wrong. find me: air_puff(X)')
        
    GPIO.output(airpuff_C, False) #turns air puff OFF
    GPIO.output(airpuff_D, False) #turns air puff OFF  #this is to ensure both air puffs are off by the end of the function

def bad_buzz(X): #define funtion to be executed when animal is heaveir than chosen weight treshold

    if X == 'C':
        buzz_C.start(50)
        for _ in range(10):
            print("bad buzz mouse C")
            buzz_C.ChangeFrequency(heavier_buzz_1) #1st tone
            GPIO.output(rLED_C,True) #turns red led ON
            time.sleep(0.1)
            buzz_C.ChangeFrequency(heavier_buzz_2) #2nd tone
            GPIO.output(rLED_C,False) #turns red led OFF
            time.sleep(0.1)
        buzz_C.stop()

    elif X == 'D':
        buzz_D.start(50)
        for _ in range(10):
            print("bad buzz mouse D")
            buzz_D.ChangeFrequency(heavier_buzz_1) #1st tone
            GPIO.output(rLED_D,True) #turns red led ON
            time.sleep(0.1)
            buzz_D.ChangeFrequency(heavier_buzz_2) #2nd tone
            GPIO.output(rLED_D,False) #turns red led OFF
            time.sleep(0.1)
        buzz_D.stop()
        
    else:
        print('something wrong. find me: bad_buzz(X)')
        
def good_buzz(X): #define funtion to be executed when animal is heaveir than chosen weight treshold
    
    if X == 'C':
        buzz_C.start(50)
        for _ in range(10):
            print("good buzz mouse C")
            buzz_C.ChangeFrequency(not_heavier_buzz_1) #1st tone
            GPIO.output(gLED_C,True) #turns green led ON
            time.sleep(0.1)
            buzz_C.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            GPIO.output(gLED_C,False) #turns green led OFF
            time.sleep(0.1)
        buzz_C.stop()
        
    elif X == 'D':
        buzz_D.start(50)
        for _ in range(10):
            print("good buzz mouse D")
            buzz_D.ChangeFrequency(not_heavier_buzz_1) #1st tone
            GPIO.output(gLED_D,True) #turns green led ON
            time.sleep(0.1)
            buzz_D.ChangeFrequency(not_heavier_buzz_2) #2nd tone
            GPIO.output(gLED_D,False) #turns green led OFF
            time.sleep(0.1)
        buzz_D.stop()
        
    else:
        print('something wrong. find me: good_buzz(X)')
        
def scan_tube_leaving(X): #define function for checking if animal has left the scale
    
    animal_left = False
    global lines_to_chuck
    
    if X == 'C':
        ser_C.close()
        ser_C.open()
        ser_C.flush()
        for _ in range(lines_to_chuck):
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
        for _ in range(lines_to_chuck):
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
        
'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
FUNCTIONS FOR THREADING
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
def mouse_C(MODE_C): #define function that runs everything for mouse C
    
    global dtLastState_C
    global wheel_counter_C
    global turn_C
    global pellet_counter_C
    global limit_C
    global protocol
    
    while True:
    
        if MODE_C == 0: 
            move_door_social('C')
            print("\nMODE_C 0\n")
            
            
        while MODE_C == 0:
            proximity_check_C = animal_in_tube('C') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_C == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1C: proximity detected')
                tag_C = RFID_check('C') #checks RFID tag and returns bolean 
                    
                if tag_C == True: #CHECK 2: if it's mouse D, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2C: RFID ok')
                    how_many_C = scan_tube_entry('C') #checks weight to confirm it's only 1 mouse Cnd return boolean
                                
                    if how_many_C == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3C: weight ok')
                        move_door_close('C') #close doors
                        which_mouse = 'C'
                        MODE_C = 1 
                            
                    else: #CHECK 3
                        print('check 3C fail: weight not >10 and <30g')
                        how_many_C = False
                        proximity_check_C = False
                        tag_C = False
                        pass
                    
                else: #CHECK 2
                    print('check 2C fail: wrong RFID tag')
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
                dtState_C = GPIO.input(dt_C) #read input from running wheel
                returned_C = animal_in_tube('C') #checks if animal has returned from feeding area and store it as boolean
                
                if returned_C == False: #if animal has not yet returned from feeding area, perform these functions
                    GPIO.output(writeFED_C, True)
                    
                    if dtState_C != dtLastState_C: 
                        wheel_counter_C += 1 #running wheel rotation wheel_counter
                        dtLastState_C = dtState_C
                        
                        if wheel_counter_C >= limit_C: #when completes 1 full turn (wheel_counter = 1200)
                            turn_C = wheel_counter_C/cycle_C
                            limit_C = wheel_counter_C + cycle_C #reset limit for 1 extra turn
                            print("mouse C wheel turns: "+str(turn_C))
                            
                        else:
                            pass
                    
                    elif GPIO.event_detected(read_FED_C): #detects signal coming from the FED
                        pellet_counter_C += 1 #counts one pellet
                        print("Pellet retrieved. Pellet counter for mouse C: "+str(pellet_counter_C))
                    
                    else:
                        pass
                    
                
                else: #if animal has returned from feeding area, perform these functions
                    print("mouse C returned. acquiring weight")
                    print("mouse C rotation counter: "+str(wheel_counter_C))
                    GPIO.output(writeFED_C, False)
                    move_door_close('C') #close doors for proper weighting
                    append_rotation('C', protocol, wheel_counter_C) #save running wheel rotation data
                    append_pellet('C', protocol, pellet_counter_C) #save pellet data
                    
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
#                         move_door_close('C') #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("mouse C: cycle over, starting again")
                        MODE_C = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping

def mouse_D(MODE_D): #define function that runs everything for mouse C
    
    global dtLastState_D
    global wheel_counter_D
    global turn_D
    global pellet_counter_D
    global limit_D
    global protocol
    
    while True:
    
        if MODE_D == 0: 
            move_door_social('D')
            print("\nMODE_D 0\n")
            
            
        while MODE_D == 0:
            proximity_check_D = animal_in_tube('D') #checks if an animal entered the scale tube (IR sensor) and retun as boolean
                
            if proximity_check_D == True: #CHECK 1: if a mouse is detected, open RFID antenna to check which mouse it is
                print('check 1D: proximity detected')
                tag_D = RFID_check('D') #checks RFID tag and returns bolean 
                    
                if tag_D == True: #CHECK 2: if it's mouse D, open OpenScale to check weight (if there's more than one mouse)
                    print('check 2D: RFID ok')
                    how_many_D = scan_tube_entry('D') #checks weight to confirm it's only 1 mouse Cnd return boolean
                                
                    if how_many_D == True: #CHECK 3: if there's only 1 mouse (weight >10g and <30g), proceed
                        print('check 3D: weight ok')
                        move_door_close('D') #close doors
                        which_mouse = 'D'
                        MODE_D = 1 
                            
                    else: #CHECK 3
                        print('check 3D fail: weight not >10 and <30g')
                        how_many_D = False
                        proximity_check_D = False
                        tag_D = False
                        pass
                    
                else: #CHECK 2
                    print('check 2D fail: wrong RFID tag')
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
                dtState_D = GPIO.input(dt_D) #read input from running wheel
                returned_D = animal_in_tube('D') #checks if animal has returned from feeding area and store it as boolean
                
                if returned_D == False: #if animal has not yet returned from feeding area, perform these functions
                    GPIO.output(writeFED_D, True)

                    if dtState_D != dtLastState_D: 
                        wheel_counter_D += 1 #running wheel rotation wheel_counter
                        dtLastState_D = dtState_D
                        
                        if wheel_counter_D >= limit_D: #when completes 1 full turn (wheel_counter = 1200)
                            turn_D = wheel_counter_D/cycle_D
                            limit_D = wheel_counter_D + cycle_D #reset limit for 1 extra turn
                            print("mouse D wheel turns: "+str(turn_D))
                            
                        else:
                            pass
                    
                    elif GPIO.event_detected(read_FED_D): #detects signal coming from the FED
                        pellet_counter_D += 1 #counts one pellet
                        print("Pellet retrieved. Pellet counter for mouse D: "+str(pellet_counter_D))
                    
                    else:
                        pass
                    
                
                else: #if animal has returned from feeding area, perform these functions
                    print("mouse D returned. acquiring weight")
                    print("mouse D rotation counter: "+str(wheel_counter_D))
                    GPIO.output(writeFED_D, False)
                    move_door_close('D') #close doors for proper weighting
                    append_rotation('D', protocol, wheel_counter_D) #save running wheel rotation data
                    append_pellet('D', protocol, pellet_counter_D) #save pellet data
                    
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
#                         move_door_close('D') #close doors
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
move_door_social('C')
move_door_social('D')
#close all RFID antennas serial ports
RFID_C.close()
RFID_D.close()
#close all OpenScales seria ports
ser_C.close()
ser_D.close()
#turn signal to al FEDs low
GPIO.output(writeFED_C, False)
GPIO.output(writeFED_D, False)
#turn signal to all air puffs low
GPIO.output(airpuff_C, False)
GPIO.output(airpuff_D, False)
#set MODE variables
MODE_C = 0
MODE_D = 0

#create thread objects
thread_C = threading.Thread(target=mouse_C, args=(MODE_C,))
thread_D = threading.Thread(target=mouse_D, args=(MODE_D,))
#initialize thread objects   
thread_C.start()
thread_D.start()
