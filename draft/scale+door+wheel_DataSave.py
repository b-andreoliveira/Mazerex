#import libraries
import serial
import time
import RPi.GPIO as GPIO
import os
import pandas as pd
import statistics as stats
import time
from datetime import datetime

# change directory to document data folder
os.chdir("/home/pi/Documents/data/dummy_data")

'''
-------------------------------------------------------------------------------------------------------------------
DEFINE FUNCTIONS TO BE USED IN THE CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
'''

#define countdown function (for testing only)
def countdown():
    for x in range(5,-1, -1):
        print("countdown: " + str(x))
        time.sleep(1)


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


#define function to acquire weight data PRE
def acquire_weight_pre():
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    for x in range(50): # 100 lines*120ms per line=12s of data 
        line=ser.readline()
#         print(line)    #printing makes it slower
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg_pre = relProb_float*1000
        
        openscale.append(mg_pre)

        for i in range(len(openscale)):   #in case mode is not important, delete
            openscale[i] = round(openscale[i],3)
        
        #weight_data_mean = round(weight_data_mean,2) # two digits of precision
        #weight_data_median = round(weight_data_median,2) # two digits of precision
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
    mg_pre_mean = weight_data_mean
    mg_pre_median = weight_data_median
    
    #return values for comparison
    return mg_pre_mean
    
    # change mode and clean up
    del openscale
    

#define function to acquire weight data POST
def acquire_weight_post():
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    for x in range(50): # 100 lines*120ms per line=12s of data 
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
        #weight_data_median = round(weight_data_median,2) # two digits of precision
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

#define function for checking if there`s enought weight on the load cell: SOCIAL TO FOOD
def check_weight_pre(mg_pre_mean):
    global MODE
    if mg_pre_mean > float(10) and MODE == 1:
        ser.close()
        GPIO.output(Pd1_food, False)
        GPIO.output(Pd1_social, False) #NEUTRAL position
        ser.open()
        ser.flush()
        time.sleep(5)
        print("PRE animal on scale. acquiring weight")
#         openscale.append(mg_pre_mean)
        GPIO.output(Pd1_food, True)
        GPIO.output(Pd1_social, False) #FOOD position
        print("\nMODE 2\n")
        MODE = 2
    else:
        print("PRE not enough weight on scale")
        MODE = 1
                

#define function for checking if there`s enought weight on the load cell: FOOD TO SOCIAL
def check_weight_post(mg_pre_mean, mg_post_mean):
    global MODE
    global animal_returned
    if mg_post_mean > float(10) and MODE == 2:
        animal_returned = True #if >10g, animal has returned from the feeding area
        print("animal_returned = True")
        ser.close()
#         del openscale
        GPIO.output(Pd1_food, False)
        GPIO.output(Pd1_social, False) #NEUTRAL position
        ser.open()
        ser.flush()
#         time.sleep(5)
#         openscale.append(mg_post)
        
        print("POST animal on scale. acquiring weight")       
                
        if mg_post_mean > mg_pre_mean:
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
                    
            GPIO.output(Pd1_food, False)
            GPIO.output(Pd1_social, True) #SOCIAL position
            print("\nMODE 1\n")
#             del mg_pre
#             del mg_post
            MODE = 1
                    
        else :
            print("not heavier than before. opening door")
#             animal_returned = True
#             print("animal_returned = True")
            GPIO.output(Pd1_food, False)
            GPIO.output(Pd1_social, True) #SOCIAL position
            print("\nMODE 1\n")
#             del mg_pre
#             del mg_post
            MODE = 1
            
                    
    elif mg_post_mean < float(10):
        animal_returned = False #if less than 10g on scale, animal has not returned yet
        print("END not enought weight on scale.")
        print("animal_returned = False")
        MODE = 2
    
    return animal_returned #returns wether the animal has returned from feeding area (TRUE) or not (FALSE)
    
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


'''
-------------------------------------------------------------------------------------------------------------------
INITIALIZE PARAMETERS AND VARIABES
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

#initialize MODE variable
MODE = 1

'''
-------------------------------------------------------------------------------------------------------------------
CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
'''

print("About to enter while loop")
time.sleep(1)

while True:
    
    dtState = GPIO.input(dt)
    
    if MODE == 1:
        ser.close()
        print("\nMODE 1\n")
        openscale = [] #store weight list
        ser.open()
        ser.flush()
        print("animal in social area. put weight (>10g) on scale")
        countdown()
        mg_pre_mean = acquire_weight_pre()
        check_weight_pre(mg_pre_mean)
        timer_start = time.process_time()
#         food_clk_start = time.process_time()
    
    if MODE == 2:
        ser.close()
        #print("\nMODE 2\n")
        #print("animal in feeding area. put weight (>10g) on scale")
        timer_end = time.process_time()
        
        if timer_end - timer_start < 10:
            if dtState != dtLastState:
                counter += 1
                dtLastState = dtState
        
        elif timer_end - timer_start> 10:
            append_rotation(counter)
            mg_post_mean = acquire_weight_post()
            check_weight_post(mg_pre_mean, mg_post_mean)

        
#         openscale = [] #store weight list
#         ser.open()
#         ser.flush()            
#         countdown()
# 
#         mg_post_mean = acquire_weight_post()
#         check_weight_post(mg_pre_mean, mg_post_mean)
    
#     if dtState != dtLastState:
#         counter += 1
#         print(counter)
# #         counter_list.append(counter)
# #         counter_list.append(datetime.now())
#         dtLastState = dtState
#         append_rotation(counter)
