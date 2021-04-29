#import libraries
import serial
import time
import RPi.GPIO as GPIO
import os
import pandas as pd
import statistics as stats
import time
from datetime import datetime
from IOPi import IOPi

# change directory to document data folder
os.chdir("/home/pi/Documents/data/dummy_data")

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
INITIALIZE PARAMETERS AND VARIABES
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

'''set OpenScales '''
#initialize serial port for OpenScale
ser_A = serial.Serial()
ser_A.port = '/dev/ttyUSB1' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
ser_A.baudrate = 9600
ser_A.timeout = 100000 # we do not want the device to timeout
# test device connection
ser_A.close()
ser_A.open()
ser_A.flush()
if ser_A.is_open==True:
    print("\nScale ok. Configuration:\n")
    print(ser_A, "\n") #print serial parameters
ser_A.close()

'''set RFID readers '''
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
    print("\nRFID reader ok. Configuration:\n")
    print(RFID_A, "\n") #print serial parameters
RFID_A.close()


'''set GPIO numbering mode'''
GPIO.setmode(GPIO.BOARD)

'''set IOPi buses'''
bus1 = IOPi(0x20)
bus1.set_port_direction(0, 0x00) #sets port 0 (pins 1-8) of IOPi bus 1 as outputs (00 in hex = 00000000 in binary)
bus1.set_port_direction(1, 0x00) #sets port 1 (pins 9-16) of IOPi bus 1 as outputs (00 in hex = 00000000 in binary)
bus1.write_port(0, 0x00) #sets the value of port 0 of IOPi bus 1 as false/low
bus1.write_port(1, 0x00) #sets the value of port 1 of IOPi bus 1 as false/low

bus2 = IOPi(0x21)
bus2.set_port_direction(0, 0xFF) #sets port 0 (pins 1-8) of IOPi bus 2 as inputs (FF in hex = 11111111 in binary)

'''set pin outputs to arduino - door controls'''
#mouse A
bus1.set_pin_direction (2, 0) #sets pin 2 of bus 1 as output
PdA_food_ON = bus1.write_pin(2, 1)
PdA_food_OFF = bus1.write_pin(2, 0)

bus1.set_pin_direction(4, 0) #sets pin 4 of bus 1 as output
PdA_social_ON = bus1.write_pin(4, 1)
PdA_social_OFF = bus1.write_pin(4, 0)

#mouse B
bus1.set_pin_direction(6, 0) #sets pin 6 of bus1 as output
PdB_food_ON = bus1.write_pin(6, 1)
PdB_food_OFF = bus1.write_pin(6, 0)

bus1.set_pin_direction(8, 0) #sets pin 8 of bus1 as output
PdB_social_ON = bus1.write_pin(8, 1)
PdB_social_OFF = bus1.write_pin(8, 0)

#mouse C
bus1.set_pin_direction(10, 0) #sets pin 10 of bus1 as output
PdC_food_ON = bus1.write_pin(10, 1)
PdC_food_OFF = bus1.write_pin(10, 0)

bus1.set_pin_direction(12, 0)  #sets pin 12 of bus1 as output
PdC_social_ON = bus1.write_pin(12, 1)
PdC_social_OFF = bus1.write_pin(12, 0)

#mouse D
bus1.set_pin_direction(14, 0)  #sets pin 14 of bus1 as output
PdD_food_ON = bus1.write_pin(14, 1)
PdD_food_OFF = bus1.write_pin(14, 0)

bus1.set_pin_direction(16, 0)  #sets pin 16 of bus1 as output
PdD_social_ON = bus1.write_pin(16, 1)
PdD_social_OFF = bus1.write_pin(16, 0)

#set all doors in the neutral position
PdA_food_OFF; PdA_social_OFF #NEUTRAL POSITION mouse A
PdB_food_OFF; PdB_social_OFF #NEUTRAL POSITION mouse B
PdC_food_OFF; PdC_social_OFF #NEUTRAL POSITION mouse C
PdD_food_OFF; PdD_social_OFF #NEUTRAL POSITION mouse D


'''set pin output to buzzer and LEDs'''
#define buzzer sounds (same for all animals)
heavier_buzz_1 = 700
heavier_buzz_2 = 589
not_heavier_buzz_1 = 131
not_heavier_buzz_2 = 165

#mouse A
buzzer_A = 12
neopix_A = 16
GPIO.setup(buzzer_A, GPIO.OUT)
GPIO.setup(neopix_A, GPIO.OUT)
buzz_A = GPIO.PWM(buzzer_A, 1) #starting frequency is 1 (inaudible)
GPIO.output(buzzer_A, False)
GPIO.output(neopix_A, False)

#mouse B
buzzer_B = 32
neopix_B = 18
GPIO.setup(buzzer_B, GPIO.OUT)
GPIO.setup(neopix_B, GPIO.OUT)
buzz_B = GPIO.PWM(buzzer_B, 1) #starting frequency is 1 (inaudible)
GPIO.output(buzzer_B, False)
GPIO.output(neopix_B, False)

#mouse C
buzzer_C = 33
neopix_C = 22
GPIO.setup(buzzer_C, GPIO.OUT)
GPIO.setup(neopix_C, GPIO.OUT)
buzz_C = GPIO.PWM(buzzer_C, 1) #starting frequency is 1 (inaudible)
GPIO.output(buzzer_C, False)
GPIO.output(neopix_C, False)

#mouse D
buzzer_D = 35
neopix_D = 24
GPIO.setup(buzzer_D, GPIO.OUT)
GPIO.setup(neopix_D, GPIO.OUT)
buzz_D = GPIO.PWM(buzzer_D, 1) #starting frequency is 1 (inaudible)
GPIO.output(buzzer_D, False)
GPIO.output(neopix_D, False)


'''set pin inputs from running wheel rotary encoder and initialize variables'''
#mouse A
bus2.set_pin_direction(1, 1) #sets pin 1 (bus 2) of IOPi as input
dt_A = bus2.read_pin(1)
wheel_counter_A = 0
wheel_turn_A = 0
dtLastState_A = bus2.read_pin(1)
cycle_A = 1200 #calibration value
limit_A = cycle_A

#mouse B
bus2.set_pin_direction(3, 1) #sets pin 3 (bus 2) of IOPi as input
dt_B = bus2.read_pin(3)
wheel_counter_B = 0
wheel_turn_B = 0
dtLastState_B = bus2.read_pin(3)
cycle_B = 1200 #calibration value
limit_B = cycle_B

#mouse C
bus2.set_pin_direction(5, 1) #sets pin 5 (bus 2) of IOPi as input
dt_C = bus2.read_pin(5)
wheel_counter_C = 0
wheel_turn_C = 0
dtLastState_C = bus2.read_pin(5)
cycle_C = 1200 #calibration value
limit_C = cycle_C

#mouse D
bus2.set_pin_direction(7, 1) #sets pin 7 (bus 2) of IOPi as input
dt_D = bus2.read_pin(7)
wheel_counter_D = 0
wheel_turn_D = 0
dtLastState_D = bus2.read_pin(7)
cycle_D = 1200 #calibration value
limit_D = cycle_D


'''set pins (bus2 IOPi) for proximity sensor (flying fish)'''
#mouse A
bus2.set_pin_direction(2, 1) #sets pin as input 2 as input
bus2.set_pin_pullup(2, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
IR_sensor_A = bus2.read_pin(2) #reads pin 2 (bus 2) of IOPi as proximity sensor for mouse A

#mouse B
bus2.set_pin_direction(4, 1) #sets pin 4 as input
bus2.set_pin_pullup(4, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
IR_sensor_B = bus2.read_pin(4) #reads pin 4 (bus 2) of IOPi as prpximity sensor for mouse B

#mouse C
bus2.set_pin_direction(6, 1) #sets pin 6 as input
bus2.set_pin_pullup(6, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
IR_sensor_C = bus2.read_pin(6) #reads pin 5 (bus 2) of IOPi as proximity sensor for mouse C

#mouse D
bus2.set_pin_direction(8, 1) #sets pin 8 as input
bus2.set_pin_pullup(8, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)
IR_sensor_D = bus2.read_pin(8) #reads pin 8 (bus 2) of IOPi as proximity sensor for mouse D


'''set pins (bus1 IOPi) for sending output to FED'''
#mouseA
bus1.set_pin_direction(1, 0) #sets pin 1 (bus 1) of IOPi as ouput
FED_ON_A = bus1.write_pin(1, 1) #sends input to FED - makes pellet drop
FED_OFF_A = bus1.write_pin(1, 0) #stop sending input to FED
FED_OFF_A #sets pin as low

#mouseB
bus1.set_pin_direction(3, 0) #sets pin 3 (bus 1) of IOPi as ouput
FED_ON_B = bus1.write_pin(3, 1) #sends input to FED - makes pellet drop
FED_OFF_B = bus1.write_pin(3, 0) #stop sending input to FED
FED_OFF_B #sets pin as low

#mouseC
bus1.set_pin_direction(5, 0) #sets pin 5 (bus 1) of IOPi as ouput
FED_ON_C = bus1.write_pin(5, 1) #sends input to FED - makes pellet drop
FED_OFF_C = bus1.write_pin(5, 0) #stop sending input to FED
FED_OFF_C #sets pin as low

#mouseD
bus1.set_pin_direction(7, 0) #sets pin 7 (bus 1) of IOPi as ouput
FED_ON_D = bus1.write_pin(7, 1) #sends input to FED - makes pellet drop
FED_OFF_D = bus1.write_pin(7, 0) #stop sending input to FED
FED_OFF_D #sets pin as low


'''set pin for reading input from FED'''
#mouse A
read_FED_A = 26
GPIO.setup(read_FED_A, GPIO.IN) #sets pin as input
GPIO.add_event_detect(read_FED_A, GPIO.RISING) #detects rising voltage
pellet_counter_A = 0

#mouse B
read_FED_B = 36
GPIO.setup(read_FED_B, GPIO.IN) #sets pin as input
GPIO.add_event_detect(read_FED_B, GPIO.RISING) #detects rising voltage
pellet_counter_B = 0

#mouse C
read_FED_C = 38
GPIO.setup(read_FED_C, GPIO.IN) #sets pin as input
GPIO.add_event_detect(read_FED_C, GPIO.RISING) #detects rising voltage
pellet_counter_C = 0

#mouse D
read_FED_D = 40
GPIO.setup(read_FED_D, GPIO.IN) #sets pin as input
GPIO.add_event_detect(read_FED_D, GPIO.RISING) #detects rising voltage
pellet_counter_D = 0

'''set pins for air puffs (bus1 IOPi)'''
#mouse A
bus1.set_pin_direction(9, 0) #sets pin 9 (bus 1) of IOPi as output
air_puff_ON_A = bus1.write_pin(9, 1) #turns air puff on
air_puff_OFF_A = bus.write_pin(9, 0) #turns air puff off
air_puff_OFF_A #sets pin as low/false

#mouse B
bus1.set_pin_direction(11, 0) #sets pin 11 (bus 1) of IOPi as output
air_puff_ON_B = bus1.write_pin(11, 1) #turns air puff on
air_puff_OFF_B = bus.write_pin(11, 0) #turns air puff off
air_puff_OFF_B #sets pin as low/false

#mouse C
bus1.set_pin_direction(13, 0) #sets pin 13 (bus 1) of IOPi as output
air_puff_ON_C = bus1.write_pin(13, 1) #turns air puff on
air_puff_OFF_C = bus.write_pin(13, 0) #turns air puff off
air_puff_OFF_C #sets pin as low/false

#mouse D
bus1.set_pin_direction(15, 0) #sets pin 15 (bus 1) of IOPi as output
air_puff_ON_D = bus1.write_pin(15, 1) #turns air puff on
air_puff_OFF_D = bus.write_pin(15, 0) #turns air puff off
air_puff_OFF_D #sets pin as low/false


'''initialize MODE variable'''
MODE_A = 0 #for mouse A
MODE_B = 0 #for mouse B
MODE_C = 0 #for mouse C
MODE_D = 0 #for mouse D

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
DEFINE FUNCTIONS TO BE USED IN THE CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

'''
--------------------- ALL ANIMALS FUNCTIONS ---------------------
'''
#define countdown function (for testing only)
def countdown():
    for x in range(5,-1, -1):
        print("countdown: " + str(x))
        time.sleep(1)

def append_RFID(which_mouse, tag):
    
    RFID_A_list = {
        "Mouse" : [],
        "RFID_tag" : [],
        "Date_Time" : []
        }
    
    RFID_A_list.update({"Mouse" : [which_mouse]})
    RFID_A_list.update({"RFID_tag" : [tag]})
    RFID_A_list.update({"Date_Time" : [datetime.now()]})
    
    df_rfid = pd.DataFrame(RFID_A_list)
    print(df_rfid)
    
    if not os.path.isfile("rfid_tag.csv"):
        df_rfid.to_csv("rfid_tag.csv", encoding="utf-8-sig", index=False)
    else:
        df_rfid.to_csv("rfid_tag.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)
        
#define function to store weight data
def append_weight(which_mouse,weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode):
    
    weight_list = {
    "Which_Mouse" : [],
    "Weight_Mean": [],
    "Weight_Median": [],
    "Weight_Mode": [],
    "Weight_Max_Mode": [],
    "Date_Time": []
    }
    
    weight_list.update({'Which_Mouse' : [which_mouse]})
    weight_list.update({'Weight_Mean': [weight_data_mean]})
    weight_list.update({'Weight_Median': [weight_data_median]})
    weight_list.update({'Weight_Mode': [weight_data_mode]})
    weight_list.update({'Weight_Max_Mode': [weight_data_max_mode]})
    weight_list.update({'Date_Time': [datetime.now()]})
        
    df_w = pd.DataFrame(weight_list)
    print(df_w)

    if not os.path.isfile("weight.csv"):
        df_w.to_csv("weight.csv", encoding="utf-8-sig", index=False)
    else:
        df_w.to_csv("weight.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

'''
---------------------- MOUSE A ----------------------
'''
'''
##################### MODE_A = ALL ####################
'''
def move_door_social_A():
    PdA_food_OFF 
    PdA_social_ON #SOCIAL position

def move_door_neutral_A():
    PdA_food_OFF
    PdA_social_OFF #NEUTRAL position

def move_door_food_A():
    PdA_food_ON
    PdA_social_OFF #FOOD position

'''
##################### MODE_A = 0 ####################
'''
def RFID_reader_A():
    RFID = []
    RFID_A.close()
    RFID_A.open()
    RFID_A.flush()
    line = RFID_A.readline()
    line_as_str = str(line)
    line_as_list = line_as_str.split(r"b'\x")
    dirty_tag = line_as_list[1]
    tag_as_list = dirty_tag.split("\\r")
    tag = tag_as_list[0]
    RFID.append(tag)
    
    if tag == '020077914A15B9':
        print("mice A detected, opening door")
        which_mouse = "A"
        append_RFID(which_mouse, tag)
        return tag
    else:
        pass

'''
##################### MODE_A = 1 ####################
'''
def animal_entry_A():
    global IR_sensor_A
    animal_enter = False
    
    while animal_enter == False:
        
        if IR_sensor_A == 0: #if prosimity sensor is low (eg detected something)
            print("IR sensor: animal on scale, closing doors.")
            return True #return true if animal returned
            animal_enter = True
        else:
            return False #return false if animal not returned
            animal_enter = False

def scan_tube_entry_A():
    animal_enter = False
    openscale = [] #store weights here
    ser_A.close()
    ser_A.open()
    ser_A.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    while animal_enter == False:
#         print("while loop started again")
        line = ser_A.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg > float(10):
            print("scale scan: animal on scale, closing doors.")
            return True
            animal_enter = True
        else:
            animal_enter = False

def acquire_weight_pre_A():
    print("acquiring weight PRE")
    openscale = [] #store weights here
    ser_A.close()
    ser_A.open()
    ser_A.flush()
    for _ in range(8): # chuck two lines 
        line=ser_A.readline()   
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_A.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_pre = relProb_float*1000
        openscale.append(mg_pre)
#         print("weight in grams PRE: "+str(mg_pre))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
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
        
    #animal ID
    which_mouse = "A"

    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    print("weight data saved. opening door.")
    
    return weight_data_mean

def wait_for_animal_to_leave_foor_feeding_area_A():
    global MODE_A
    animal_out = False
    ser_A.close()
    ser_A.open()
    ser_A.flush()
    for _ in range(8): #chuck lines of garbage
        line = ser_A.readline()
    
    while animal_out == False:
        
        line=ser_A.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        
        if mg < float(10):
            animal_out = True
            print("mouse A left for feeding area")
            MODE_A = 2
            time.process_time()
            return time.process_time() #time stamp start
        else:
            animal_out = False

'''
##################### MODE_A = 2 ####################
'''

def acquire_weight_post_A():
    openscale = [] #store weights here
    ser_A.close()
    ser_A.open()
    ser_A.flush()
    for _ in range(8): # chuck two lines 
        line=ser_A.readline()
        
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_A.readline()
#         print(line)    #printing makes it slower
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_post = relProb_float*1000
        openscale.append(mg_post)
#         print("weight in grams POST: "+str(mg_post))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
        #weight_data_mean = round(weight_data_mean,2) # two digits of precision
        #weight_data_median = roun GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
        #weight_data_mode = round(weight_data_mode,2) # two digits of precision
        
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

    #animal ID
    which_mouse = "A"
    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    
    #define variables for comaprison with if clause in the next functuion
    mg_post_mean = weight_data_mean
    mg_post_median = weight_data_median
    
    # change mode and clean up
    del openscale
    
    #return values for comparison
    return mg_post_mean

def air_puff_A():
    air_puff_ON_A #turns air puff on
    time.sleep(2) #wais for 2 seconds
    air_puff_OFF_A #turns air puff off

def check_weight_post_A(mg_pre_mean_A, mg_post_mean_A):
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        buzz_A.start(50)
        air_puff()
        move_door_social_A()
        
    else:
        print("not havier than before. opening door")
        good_buzz_A()
        move_door_social_A()
        
#played when animal is heaveir than chosen weight treshold
def bad_buzz_A():
    #BAD BUZZ NEOPIXEL CODE
    buzz_A.start(50)
    for _ in range(10):
        print("bad buzz")
        buzz_A.ChangeFrequency(heavier_buzz_1);
        time.sleep(0.1)
        buzz_A.ChangeFrequency(heavier_buzz_2)
        time.sleep(0.1)
    buzz_A.stop()
    #NEOPIXEL OFF

#played when animal is not heavier than chosen weight treshold
def good_buzz_B():
    #GOOD BUZZ NEOPIXEL CODE
    buzz_A.start(50)
    for _ in range (10):
        print("good buzz")
        buzz_A.ChangeFrequency(not_heavier_buzz_1)
        time.sleep(0.1)
        buzz_A.ChangeFrequency(not_heavier_buzz_2)
        time.sleep(0.1)
    buzz_A.stop()
    #NEOPIXEL OFF

check_weight_posdef animal_returned_A():
    global IR_sensor_A
    if IR_sensor_A == 0: #if prosimity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned
    
def scan_tube_leaving_A():
    animal_left = False
    openscale = [] #store weights here
    ser_A.close()
    ser_A.open()
    ser_A.flush()
    for _ in range(8): # chuck two lines 
        line=ser_A.readline()
    while animal_left == False:    
        line=ser_A.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg < float(10):
            print("animal left for social area.")
            animal_left = True
            return True
        else:
            animal_left = False
            return False

#define function for storing wheel data
def append_rotation_A(wheel_counter_A):
    
    which_mouse = "A"
    
    rotation_list = {
    "Which_Mouse" : [],
    "Rotation": [],
    "Date_Time": []
    }
    
    rotation_list.update({"Which_Mouse": [which_mouse]})
    rotation_list.update({"Rotation": [wheel_counter_A]})
    rotation_list.update({"Date_Time": [datetime.now()]})

    df_r = pd.DataFrame(rotation_list)
    print(df_r)

    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
#define function for storing pellet retrieval data
def append_pellet_A(pellet_counter_A):
    
    which_mouse = "A"
    
    pellet_list = {
    "Which_Mouse": [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Which_Mouse": [which_mouse]})
    pellet_list.update({"Pellet": [pellet_counter_A]})
    pellet_list.update({"Date_Time": [datetime.now()]})

    df_p = pd.DataFrame(pellet_list)
    print(df_p)

    if not os.path.isfile("pellet.csv"):
        df_p.to_csv("pellet.csv", encoding = "utf-8-sig", index = False)
    else:
        df_p.to_csv("pellet.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
'''
---------------------- MOUSE B ----------------------
'''
'''
##################### MODE_B = ALL ####################
'''
def move_door_social_B():
    PdB_food_OFF 
    PdB_social_ON #SOCIAL position

def move_door_neutral_B():
    PdB_food_OFF
    PdB_social_OFF #NEUTRAL position

def move_door_food_B():
    PdB_food_ON
    PdB_social_OFF #FOOD position

'''
##################### MODE_B = 0 ####################
'''
def RFID_reader_B():
    RFID = []
    RFID_B.close()
    RFID_B.open()
    RFID_B.flush()
    line = RFID_B.readline()
    line_as_str = str(line)
    line_as_list = line_as_str.split(r"b'\x")
    dirty_tag = line_as_list[1]
    tag_as_list = dirty_tag.split("\\r")
    tag = tag_as_list[0]
    RFID.append(tag)
    
    if tag == '00779148D977':
        print("mice B detected, opening door")
        which_mouse = "B"
        append_RFID(which_mouse, tag)
        return tag
    else:
        pass

'''
##################### MODE_B = 1 ####################
'''
def animal_entry_B():
    global IR_sensor_B
    animal_enter = False
    
    while animal_enter == False:
        
        if IR_sensor_B == 0: #if prosimity sensor is low (eg detected something)
            print("IR sensor: animal on scale, closing doors.")
            return True #return true if animal returned
            animal_enter = True
        else:
            return False #return false if animal not returned
            animal_enter = False

def scan_tube_entry_B():
    animal_enter = False
    openscale = [] #store weights here
    ser_B.close()
    ser_B.open()
    ser_B.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    while animal_enter == False:
#         print("while loop started again")
        line = ser_B.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg > float(10):
            print("scale scan: animal on scale, closing doors.")
            return True
            animal_enter = True
        else:
            animal_enter = False

def acquire_weight_pre_B():
    print("acquiring weight PRE B")
    openscale = [] #store weights here
    ser_B.close()
    ser_B.open()
    ser_B.flush()
    for _ in range(8): # chuck two lines 
        line=ser_B.readline()   
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_B.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_pre = relProb_float*1000
        openscale.append(mg_pre)
#         print("weight in grams PRE: "+str(mg_pre))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
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
        
    #animal ID
    which_mouse = "B"

    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    print("weight data saved. opening door.")
    
    return weight_data_mean

def wait_for_animal_to_leave_foor_feeding_area_B():
    global MODE_B
    animal_out = False
    ser_B.close()
    ser_B.open()
    ser_B.flush()
    for _ in range(8): #chuck lines of garbage
        line = ser_B.readline()
    
    while animal_out == False:
        
        line=ser_B.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        
        if mg < float(10):
            animal_out = True
            print("mouse B left for feeding area")
            MODE_B = 2
            time.process_time()
            return time.process_time() #time stamp start
        else:
            animal_out = False

'''
##################### MODE_B = 2 ####################
'''

def acquire_weight_post_B():
    openscale = [] #store weights here
    ser_B.close()
    ser_B.open()
    ser_B.flush()
    for _ in range(8): # chuck two lines 
        line=ser_B.readline()
        
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_B.readline()
#         print(line)    #printing makes it slower
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_post = relProb_float*1000
        openscale.append(mg_post)
#         print("weight in grams POST: "+str(mg_post))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
        #weight_data_mean = round(weight_data_mean,2) # two digits of precision
        #weight_data_median = roun GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
        #weight_data_mode = round(weight_data_mode,2) # two digits of precision
        
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

    #animal ID
    which_mouse = "B"
    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    
    #define variables for comaprison with if clause in the next functuion
    mg_post_mean = weight_data_mean
    mg_post_median = weight_data_median
    
    # change mode and clean up
    del openscale
    
    #return values for comparison
    return mg_post_mean

def air_puff_B():
    air_puff_ON_B #turns air puff on
    time.sleep(2) #wais for 2 seconds
    air_puff_OFF_B #turns air puff off

def check_weight_post_B(mg_pre_mean_B, mg_post_mean_B):
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        bad_buzz_B()
        air_puff()
        move_door_social_B()
        
    else:
        print("not havier than before. opening door")
        good_buzz_B()
        move_door_social_B()
        
#played when animal is heaveir than chosen weight treshold
def bad_buzz_B():
    #BAD BUZZ NEOPIXEL CODE
    buzz_B.start(50)
    for _ in range(10):
        print("bad buzz")
        buzz_B.ChangeFrequency(heavier_buzz_1);
        time.sleep(0.1)
        buzz_B.ChangeFrequency(heavier_buzz_2)
        time.sleep(0.1)
    buzz_B.stop()
    #NEOPIXEL OFF

#played when animal is not heavier than chosen weight treshold
def good_buzz_B():
    #GOOD BUZZ NEOPIXEL CODE
    buzz_B.start(50)
    for _ in range (10):
        print("good buzz")
        buzz_B.ChangeFrequency(not_heavier_buzz_1)
        time.sleep(0.1)
        buzz_B.ChangeFrequency(not_heavier_buzz_2)
        time.sleep(0.1)
    buzz_B.stop()
    #NEOPIXEL OFF

def animal_returned_B():
    global IR_sensor_B
    if IR_sensor_B == 0: #if prosimity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned
    
def scan_tube_leaving_B():
    animal_left = False
    openscale = [] #store weights here
    ser_B.close()
    ser_B.open()
    ser_B.flush()
    for _ in range(8): # chuck two lines 
        line=ser_B.readline()
    while animal_left == False:    
        line=ser_B.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg < float(10):
            print("animal left for social area.")
            animal_left = True
            return True
        else:
            animal_left = False
            return False

#define function for storing wheel data
def append_rotation_B(wheel_counter_B):
    
    which_mouse = "B"
    
    rotation_list = {
    "Which_Mouse" : [],
    "Rotation": [],
    "Date_Time": []
    }
    
    rotation_list.update({"Which_Mouse": [which_mouse]})
    rotation_list.update({"Rotation": [wheel_counter_B]})
    rotation_list.update({"Date_Time": [datetime.now()]})

    df_r = pd.DataFrame(rotation_list)
    print(df_r)

    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
#define function for storing pellet retrieval data
def append_pellet_B(pellet_counter_B):
    
    which_mouse = "B"
    
    pellet_list = {
    "Which_Mouse": [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Which_Mouse": [which_mouse]})
    pellet_list.update({"Pellet": [pellet_counter_B]})
    pellet_list.update({"Date_Time": [datetime.now()]})

    df_p = pd.DataFrame(pellet_list)
    print(df_p)

    if not os.path.isfile("pellet.csv"):
        df_p.to_csv("pellet.csv", encoding = "utf-8-sig", index = False)
    else:
        df_p.to_csv("pellet.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)


'''
---------------------- MOUSE C ----------------------
'''
'''
##################### MODE_C = ALL ####################
'''
def move_door_social_C():
    PdC_food_OFF 
    PdC_social_ON #SOCIAL position

def move_door_neutral_C():
    PdC_food_OFF
    PdC_social_OFF #NEUTRAL position

def move_door_food_C():
    PdC_food_ON
    PdC_social_OFF #FOOD position

'''
##################### MODE_C = 0 ####################
'''
def RFID_reader_C():
    RFID = []
    RFID_C.close()
    RFID_C.open()
    RFID_C.flush()
    line = RFID_C.readline()
    line_as_str = str(line)
    line_as_list = line_as_str.split(r"b'\x")
    dirty_tag = line_as_list[1]
    tag_as_list = dirty_tag.split("\\r")
    tag = tag_as_list[0]
    RFID.append(tag)
    
    if tag == '00779149E14E':
        print("mice C detected, opening door")
        which_mouse = "C"
        append_RFID(which_mouse, tag)
        return tag
    else:
        pass

'''
##################### MODE_C = 1 ####################
'''
def animal_entry_C():
    global IR_sensor_C
    animal_enter = False
    
    while animal_enter == False:
        
        if IR_sensor_C == 0: #if prosimity sensor is low (eg detected something)
            print("IR sensor: animal on scale, closing doors.")
            return True #return true if animal returned
            animal_enter = True
        else:
            return False #return false if animal not returned
            animal_enter = False

def scan_tube_entry_C():
    animal_enter = False
    openscale = [] #store weights here
    ser_C.close()
    ser_C.open()
    ser_C.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    while animal_enter == False:
#         print("while loop started again")
        line = ser_C.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg > float(10):
            print("scale scan: animal on scale, closing doors.")
            return True
            animal_enter = True
        else:
            animal_enter = False

def acquire_weight_pre_C():
    print("acquiring weight PRE B")
    openscale = [] #store weights here
    ser_C.close()
    ser_C.open()
    ser_C.flush()
    for _ in range(8): # chuck two lines 
        line=ser_C.readline()   
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_C.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_pre = relProb_float*1000
        openscale.append(mg_pre)
#         print("weight in grams PRE: "+str(mg_pre))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
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
        
    #animal ID
    which_mouse = "C"

    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    print("weight data saved. opening door.")
    
    return weight_data_mean

def wait_for_animal_to_leave_foor_feeding_area_C():
    global MODE_C
    animal_out = False
    ser_C.close()
    ser_C.open()
    ser_C.flush()
    for _ in range(8): #chuck lines of garbage
        line = ser_C.readline()
    
    while animal_out == False:
        
        line=ser_C.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        
        if mg < float(10):
            animal_out = True
            print("mouse C left for feeding area")
            MODE_C = 2
            time.process_time()
            return time.process_time() #time stamp start
        else:
            animal_out = False

'''
##################### MODE_C = 2 ####################
'''

def acquire_weight_post_C():
    openscale = [] #store weights here
    ser_C.close()
    ser_C.open()
    ser_C.flush()
    for _ in range(8): # chuck two lines 
        line=ser_C.readline()
        
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_C.readline()
#         print(line)    #printing makes it slower
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_post = relProb_float*1000
        openscale.append(mg_post)
#         print("weight in grams POST: "+str(mg_post))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
        #weight_data_mean = round(weight_data_mean,2) # two digits of precision
        #weight_data_median = roun GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
        #weight_data_mode = round(weight_data_mode,2) # two digits of precision
        
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

    #animal ID
    which_mouse = "C"
    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    
    #define variables for comaprison with if clause in the next functuion
    mg_post_mean = weight_data_mean
    mg_post_median = weight_data_median
    
    # change mode and clean up
    del openscale
    
    #return values for comparison
    return mg_post_mean

def air_puff_C():
    air_puff_ON_C #turns air puff on
    time.sleep(2) #wais for 2 seconds
    air_puff_OFF_C #turns air puff off

def check_weight_post_C(mg_pre_mean_C, mg_post_mean_C):
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        bad_buzz_C()
        air_puff()
        move_door_social_C()
        
    else:
        print("not havier than before. opening door")
        good_buzz_C()
        move_door_social_C()
        
#played when animal is heaveir than chosen weight treshold
def bad_buzz_C():
    #BAD BUZZ NEOPIXEL CODE
    buzz_C.start(50)
    for _ in range(10):
        print("bad buzz")
        buzz_C.ChangeFrequency(heavier_buzz_1);
        time.sleep(0.1)
        buzz_C.ChangeFrequency(heavier_buzz_2)
        time.sleep(0.1)
    buzz_C.stop()
    #NEOPIXEL OFF

#played when animal is not heavier than chosen weight treshold
def good_buzz_C():
    #GOOD BUZZ NEOPIXEL CODE
    buzz_C.start(50)
    for _ in range (10):
        print("good buzz")
        buzz_C.ChangeFrequency(not_heavier_buzz_1)
        time.sleep(0.1)
        buzz_C.ChangeFrequency(not_heavier_buzz_2)
        time.sleep(0.1)
    buzz_C.stop()
    #NEOPIXEL OFF

def animal_returned_C():
    global IR_sensor_C
    if IR_sensor_C == 0: #if prosimity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned
    
def scan_tube_leaving_C():
    animal_left = False
    openscale = [] #store weights here
    ser_C.close()
    ser_C.open()
    ser_C.flush()
    for _ in range(8): # chuck two lines 
        line=ser_C.readline()
    while animal_left == False:    
        line=ser_C.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg < float(10):
            print("animal left for social area.")
            animal_left = True
            return True
        else:
            animal_left = False
            return False

#define function for storing wheel data
def append_rotation_C(wheel_counter_C):
    
    which_mouse = "C"
    
    rotation_list = {
    "Which_Mouse" : [],
    "Rotation": [],
    "Date_Time": []
    }
    
    rotation_list.update({"Which_Mouse": [which_mouse]})
    rotation_list.update({"Rotation": [wheel_counter_C]})
    rotation_list.update({"Date_Time": [datetime.now()]})

    df_r = pd.DataFrame(rotation_list)
    print(df_r)

    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
#define function for storing pellet retrieval data
def append_pellet_C(pellet_counter_C):
    
    which_mouse = "C"
    
    pellet_list = {
    "Which_Mouse": [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Which_Mouse": [which_mouse]})
    pellet_list.update({"Pellet": [pellet_counter_C]})
    pellet_list.update({"Date_Time": [datetime.now()]})

    df_p = pd.DataFrame(pellet_list)
    print(df_p)

    if not os.path.isfile("pellet.csv"):
        df_p.to_csv("pellet.csv", encoding = "utf-8-sig", index = False)
    else:
        df_p.to_csv("pellet.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)


'''
---------------------- MOUSE D ----------------------
'''
'''
##################### MODE_D = ALL ####################
'''
def move_door_social_D():
    PdA_food_OFF 
    PdA_social_ON #SOCIAL position

def move_door_neutral_D():
    PdA_food_OFF
    PdA_social_OFF #NEUTRAL position

def move_door_food_D():
    PdA_food_ON
    PdA_social_OFF #FOOD position

'''
##################### MODE_D = 0 ####################
'''
def RFID_reader_D():
    RFID = []
    RFID_D.close()
    RFID_D.open()
    RFID_D.flush()
    line = RFID_D.readline()
    line_as_str = str(line)
    line_as_list = line_as_str.split(r"b'\x")
    dirty_tag = line_as_list[1]
    tag_as_list = dirty_tag.split("\\r")
    tag = tag_as_list[0]
    RFID.append(tag)
    
    if tag == '000C0BCE2AE3':
        print("mice D detected, opening door")
        which_mouse = "D"
        append_RFID(which_mouse, tag)
        return tag
    else:
        pass

'''
##################### MODE_D = 1 ####################
'''
def animal_entry_D():
    global IR_sensor_D
    animal_enter = False
    
    while animal_enter == False:
        
        if IR_sensor_D == 0: #if prosimity sensor is low (eg detected something)
            print("IR sensor: animal on scale, closing doors.")
            return True #return true if animal returned
            animal_enter = True
        else:
            return False #return false if animal not returned
            animal_enter = False

def scan_tube_entry_D():
    animal_enter = False
    openscale = [] #store weights here
    ser_D.close()
    ser_D.open()
    ser_D.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    while animal_enter == False:
#         print("while loop started again")
        line = ser_D.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg > float(10):
            print("scale scan: animal on scale, closing doors.")
            return True
            animal_enter = True
        else:
            animal_enter = False

def acquire_weight_pre_D():
    print("acquiring weight PRE B")
    openscale = [] #store weights here
    ser_D.close()
    ser_D.open()
    ser_D.flush()
    for _ in range(8): # chuck two lines 
        line=ser_D.readline()   
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_D.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_pre = relProb_float*1000
        openscale.append(mg_pre)
#         print("weight in grams PRE: "+str(mg_pre))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
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
        
    #animal ID
    which_mouse = "D"

    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    print("weight data saved. opening door.")
    
    return weight_data_mean

def wait_for_animal_to_leave_foor_feeding_area_D():
    global MODE_D
    animal_out = False
    ser_D.close()
    ser_D.open()
    ser_D.flush()
    for _ in range(8): #chuck lines of garbage
        line = ser_D.readline()
    
    while animal_out == False:
        
        line=ser_D.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        
        if mg < float(10):
            animal_out = True
            print("mouse D left for feeding area")
            MODE_D = 2
            time.process_time()
            return time.process_time() #time stamp start
        else:
            animal_out = False

'''
##################### MODE_D = 2 ####################
'''

def acquire_weight_post_D():
    openscale = [] #store weights here
    ser_D.close()
    ser_D.open()
    ser_D.flush()
    for _ in range(8): # chuck two lines 
        line=ser_D.readline()
        
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser_D.readline()
#         print(line)    #printing makes it slower
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_post = relProb_float*1000
        openscale.append(mg_post)
#         print("weight in grams POST: "+str(mg_post))

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
        #weight_data_mean = round(weight_data_mean,2) # two digits of precision
        #weight_data_median = roun GPIO.output(buzzer, True); time.sleep(0.5); print("buzz")
        #weight_data_mode = round(weight_data_mode,2) # two digits of precision
        
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

    #animal ID
    which_mouse = "D"
    
    #appending data to database
    append_weight(which_mouse, weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    
    #define variables for comaprison with if clause in the next functuion
    mg_post_mean = weight_data_mean
    mg_post_median = weight_data_median
    
    # change mode and clean up
    del openscale
    
    #return values for comparison
    return mg_post_mean

def air_puff_D():
    air_puff_ON_D #turns air puff on
    time.sleep(2) #wais for 2 seconds
    air_puff_OFF_D #turns air puff off

def check_weight_post_D(mg_pre_mean_D, mg_post_mean_D):
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        bad_buzz_D()
        air_puff()
        move_door_social_D()
        
    else:
        print("not havier than before. opening door")
        good_buzz_D()
        move_door_social_D()
        
#played when animal is heaveir than chosen weight treshold
def bad_buzz_D():
    #BAD BUZZ NEOPIXEL CODE
    buzz_D.start(50)
    for _ in range(10):
        print("bad buzz")
        buzz_D.ChangeFrequency(heavier_buzz_1);
        time.sleep(0.1)
        buzz_D.ChangeFrequency(heavier_buzz_2)
        time.sleep(0.1)
    buzz_D.stop()
    #NEOPIXEL OFF

#played when animal is not heavier than chosen weight treshold
def good_buzz_D():
    #GOOD BUZZ NEOPIXEL CODE
    buzz_D.start(50)
    for _ in range (10):
        print("good buzz")
        buzz_D.ChangeFrequency(not_heavier_buzz_1)
        time.sleep(0.1)
        buzz_D.ChangeFrequency(not_heavier_buzz_2)
        time.sleep(0.1)
    buzz_D.stop()
    #NEOPIXEL OFF

def animal_returned_D():
    global IR_sensor_D
    if IR_sensor_D == 0: #if prosimity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned
    
def scan_tube_leaving_D():
    animal_left = False
    openscale = [] #store weights here
    ser_D.close()
    ser_D.open()
    ser_D.flush()
    for _ in range(8): # chuck two lines 
        line=ser_D.readline()
    while animal_left == False:    
        line=ser_D.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg < float(10):
            print("animal left for social area.")
            animal_left = True
            return True
        else:
            animal_left = False
            return False

#define function for storing wheel data
def append_rotation_D(wheel_counter_D):
    
    which_mouse = "D"
    
    rotation_list = {
    "Which_Mouse" : [],
    "Rotation": [],
    "Date_Time": []
    }
    
    rotation_list.update({"Which_Mouse": [which_mouse]})
    rotation_list.update({"Rotation": [wheel_counter_D]})
    rotation_list.update({"Date_Time": [datetime.now()]})

    df_r = pd.DataFrame(rotation_list)
    print(df_r)

    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        
#define function for storing pellet retrieval data
def append_pellet_D(pellet_counter_D):
    
    which_mouse = "D"
    
    pellet_list = {
    "Which_Mouse": [],
    "Pellet": [],
    "Date_Time": []
    }
    
    pellet_list.update({"Which_Mouse": [which_mouse]})
    pellet_list.update({"Pellet": [pellet_counter_D]})
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
CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''
move_door_neutral_A()
move_door_neutral_B()
move_door_neutral_C()
move_door_neutral_D()

while True:
    
'''
##################### MOUSE A #####################
'''
    
    if MODE_A == 0:
        print("\nMODE_A = 0\n")
        tag = RFID_reader_A()
        
        if tag == '020077914A15B9':
            move_door_social_A()
            MODE_A = 1
        else:
            pass
        
    if MODE_A == 1:
        ser.close()
        print("\nMODE_A = 1\n")
        animal_entered_A = scan_tube_entry_A() #proximity sensor checks if animal is in tube and stores as boolean
        
        if animal_entered == True:
            time.sleep(3) #wait for the animal to get inside the tube before closing door
            ''' IDEA: maybe couple door closing with proximity sensor to be sure tha the animal has entered the tube before closing doors '''
            move_door_neutral_A() #close door for proper weighting - NEUTRAL position
            mg_pre_mean_A = acquire_weight_pre_A() #acquire weight and assign mean weight value
            move_door_food_A() #open door - FOOD position
#             timer_feed_start = time.process_time()  #time stamp start
            timer_feed_start_A = wait_for_animal_to_leave_foor_feeding_area() #time stamp start
        
            
        else:
            pass
        
    if MODE_A == 2:
        ser_A.close()
        
        while MODE_A == 2:
            dtState_A = dt_A #read input from running wheel
            sensor_A = IR_sensor_A #read inpu from proximity sensor
            returned_A = animal_returned_A() #checks whether animal has returned and stores as boolean (true/false)
            
            if returned_A == False: #if mouse A hs not returned, perform these tasks:
                if dtState_A != dtLastState_A:
                    wheel_counter_A += 1
                    dtLastState_A = dtState_A
                    
                    if wheel_counter_A >= limit_A: #when completes 1 full turn (wheel_counter = 1200)
                        wheel_turn_A = wheel_counter_A/cycle_A
                        limit_A = wheel_counter_A + cycle_A #reset limit for 1 extra turn
                        print("Mouse A wheel turns: "+str(wheel_turn_A))
                        
                        if wheel_turn_A % 10 == 0 and wheel_turn != 0: #each 10 revolutions
                            print ("Mouse A has completed 10 wheel turns, delivring pellet")
                            FED_ON_A #sends output to FED - turnd FED motor on and makes pellet drop
                    else:
                        pass
            
                elif GPIO.event_detected(read_FED_A):
                    print("Mouse A retrieved pellet")
                    FED_OFF_A #turns FED motor off
                    pellet_counter_A += 1
                    append_pellet_A(pellet_counter_A)
                    
                else:
                    pass
                
            elif returned_A == True: #if mouse A has returned, perform these tasks
                print("Mouse A returned from feeding area. Acquiring weight")
                move_door_neutral_A() #NEUTRAL position - close doors fir weighting
                append_rotation_A(wheel_counter_A) #save runing wheel rotation data
                wheel_counter_A = 0 #reset wheel rotation counter
                pellet_counter_A = 0 #reset pellet counter
                wheel_turn_A = 0 #reset wheel turn counter
                limit_A = cycle_A #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                FED_OFF_A #make sure input to FED is low
                dtLastState_A = bus2.read_pin(1) #reset input from wheel
                mg_post_mean_A = acquire_weight_post_A() #acquire weight and assign mean weight value
                check_weight_post_A(mg_pre_mean_A, mg_post_mean_A) #compare weights means pre and post and deliver proper stimulus
                animal_left_A = scan_tube_leaving_A() #scan tube to check whether animal is still in and stores info as boolean
                
                while animal_left_A == False: #while the animal is still on the tube, perform thee tasks
                    animal_left_A = scan_tube_leaving_A() #continue to scan tube to check whether animal is still in and stores info as boolean
                    
                    if animal_left_A == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_neutral_A()
                        print("cycle over. starting again")
                        MODE_A = 0
                    else: #if animal hasn't left tube yet, keep looping
                        pass
                        
            
'''
##################### MOUSE B #####################
'''            



