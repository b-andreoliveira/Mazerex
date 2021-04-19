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
DEFINE FUNCTIONS TO BE USED IN THE CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

'''
MODE 1 FUNCTIONS ########################################################################################
'''


def scan_tube_entry():
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
    while True:    
        line=ser.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg > float(10):
            print("animal on scale. closing doors.")
            return True
        else:
            print("not enough weight on scale.")
            countdown()
          
def move_door_S2N():
    GPIO.output(Pd1_food, False)
    GPIO.output(Pd1_social, False) #NEUTRAL position

        
def acquire_weight_pre():
    print("acquiring weight PRE")
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()   
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_pre = relProb_float*1000
        openscale.append(mg_pre)

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

    
    #appending data to database
    append_weight(weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    print("weight data saved. opening door.")
    
    return weight_data_mean


def move_door_N2F():
    GPIO.output(Pd1_food, True)
    GPIO.output(Pd1_social, False) #NEUTRAL position

def wait_for_animal_to_leave_foor_feeding_area():
    global MODE
    animal_out = False
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): #chuck lines of garbage
        line = ser.readline()
    
    while animal_out == False:
        
        line=ser.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        
        if mg < float(10):
            animal_out = True
            print("animal left for feeding area")
            MODE = 2
            time.process_time()
            return time.process_time() #time stamp start
        else:
            animal_out = False
            
            
'''
MODE 2 FUNCTIONS ########################################################################################
'''

def scan_tube_return():
    a = time.process_time()   #deb flg 
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
    
    line=ser.readline()
    line_as_list = line.split(b',')
    relProb = line_as_list[0]
    relProb_as_list = relProb.split(b'\n')
    relProb_float = float(relProb_as_list[0])
    mg = relProb_float*1000
    b = time.process_time() #deb flg
    c=b-a; print(c)#deb flg
    if mg > float(10):
        print("animal returned from feeding area. closing doors.")
        return True
    else:
        pass

def move_door_F2N():
    GPIO.output(Pd1_food, False)
    GPIO.output(Pd1_social, False) #NEUTRAL position

def acquire_weight_post():
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    for x in range(100): # 100 lines*120ms per line=12s of data 
        line=ser.readline()
#         print(line)    #printing makes it slower
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_post = relProb_float*1000
        
        openscale.append(mg_post)

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

    
    #appending data to database
    append_weight(weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode)
    
    #define variables for comaprison with if clause in the next functuion
    mg_post_mean = weight_data_mean
    mg_post_median = weight_data_median
    
    # change mode and clean up
    del openscale
    
    #return values for comparison
    return mg_post_mean


def move_door_N2S():
    GPIO.output(Pd1_food, False)
    GPIO.output(Pd1_social, True) #NEUTRAL position


def check_weight_post(mg_pre_mean, mg_post_mean):
    global MODE
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        for _ in range(5):
            GPIO.output(buzzer, True); print("buzz")
            time.sleep(0.5)
            GPIO.output(buzzer, False)
            time.sleep(0.5)
        move_door_N2S()
        MODE = 1
        
    else:
        print("not havier than before. opening door")
        move_door_N2S()
        MODE = 1

def animal_returned():
    if proximity_sensor == 0: #if prosimity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned
        

'''
BOTH MODES FUNCTIONS ########################################################################################
'''

#define function to store weight data
def append_weight(weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode):
    
    weight_list = {
    "Weight_Mean": [],
    "Weight_Median": [],
    "Weight_Mode": [],
    "Weight_Max_Mode": [],
    "Date_Time": []
    }
    
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

#define function for storing wheel data
def append_rotation(counter):
    
    rotation_list = {
    "Rotation": [],
    "Date_Time": []
    }
    
    rotation_list.update({"Rotation": [counter]})
    rotation_list.update({"Date_Time": [datetime.now()]})

    df_r = pd.DataFrame(rotation_list)
    print(df_r)

    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)
        

#define countdown function (for testing only)
def countdown():
    for x in range(5,-1, -1):
        print("countdown: " + str(x))
        time.sleep(1)


'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
INITIALIZE PARAMETERS AND VARIABES
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

#initialize serial port for OpenScale
ser = serial.Serial()
ser.port = '/dev/ttyUSB1' #OpenScale serial port ALWAYS CHECK WHETHER THE PORT IS CORRECT!!!!!!!
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

#set pin inputs from running wheel rotary encoder and initialize variables
clk = 37
dt = 38

GPIO.setup(clk,GPIO.IN)
GPIO.setup(dt,GPIO.IN)
clkLastState = GPIO.input(clk)
dtLastState = GPIO.input(dt)

counter = 0;
cycle = 1200; #calibration value
limit = cycle;
turn = 0;

#set pins (bus1 IOPi) for beam break (flying fish) proximity scanner
bus1 = IOPi(0x20) #sets the variable bus1 to the bus 1 adress in IOPi
bus1.set_pin_direction(1, 1) #(pin, direction) #sets pin 1 on bus 1 to as an input pin (1 = input, 0 = output)
bus1.set_pin_pullup(1, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)

proximity_sensor = bus1.read_pin(1) #reas pin 1 (bus 1) of the IOPi as the sensor pin for the proximity sensor

#initialize MODE variable
MODE = 1



'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

while True:
    
#     timer_feed_start = time.process_time()
    
    if MODE == 1:
        ser.close()
        print("\nMODE 1\n")
        countdown()
        animal_entered = scan_tube_entry()
        
        if animal_entered == True:
            move_door_S2N()
            mg_pre_mean = acquire_weight_pre()
            move_door_N2F()
#             timer_feed_start = time.process_time()  #time stamp start
            timer_feed_start = wait_for_animal_to_leave_foor_feeding_area()
            
        else:
            MODE = 1
    
    if MODE == 2:
        ser.close()
        
        while MODE == 2:
            dtState = GPIO.input(dt)
            proximity_sensor = bus1.read_pin(1)
            returned = animal_returned()
            timer_feed_end = time.process_time()
             
            if returned == False:
                if dtState != dtLastState:
                    counter += 1
                    dtLastState = dtState
            
            elif returned == True:
                print("animal returned. acquiring weight")
                move_door_F2N()
                append_rotation(counter)
                counter = 0
                mg_post_mean = acquire_weight_post()
                check_weight_post(mg_pre_mean, mg_post_mean)
                how_long_animal_stayed_in_feeding_area = timer_feed_end - timer_feed_start
            
    
#         
#     if MODE == 2:
#         ser.close()
# #         print("\nMODE 2\n")
#         while MODE == 2:
#             dtState = GPIO.input(dt)
#             timer_feed_end = time.process_time()  #time stamp current update
#             
#             if timer_feed_end - timer_feed_start < 10: #count rotation in 10 second blocks
#                 if dtState != dtLastState:
#                     counter += 1
#                     dtLastState = dtState
#                 
#             elif timer_feed_end - timer_feed_start > 10: #check scale every 10 seconds
#                 #a = time.process_time()
#                 animal_returned = scan_tube_return()
#                 #b = time.process_time()
#                 #c=b-a; print(c)
#                 
#                 if animal_returned == True:
#                     move_door_F2N()
#                     append_rotation(counter)
#                     counter = 0
#                     timer_feed_start = time.process_time()
#                     print("animal returned. acquiring weight.")
#                     mg_post_mean = acquire_weight_post()
#                     check_weight_post(mg_pre_mean, mg_post_mean)
#                     
#                 else:
#                     timer_feed_start = time.process_time()
#                 



