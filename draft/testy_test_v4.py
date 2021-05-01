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
ALL MODES FUNCTIONS ########################################################################################
'''

def countdown():#define countdown function (for testing only)
    for x in range(5,-1, -1):
        print("countdown: " + str(x))
        time.sleep(1)

def move_door_social():#define function for seting door at social position
    GPIO.output(Pd1_food, False)
    GPIO.output(Pd1_social, True) #SOCIAL position

def move_door_feeding():#define function for seting door at feeding position
    GPIO.output(Pd1_food, True)
    GPIO.output(Pd1_social, False) #FEEDING position

def move_door_close():#define function for seting door at neutral position
    GPIO.output(Pd1_food, False)
    GPIO.output(Pd1_social, False) #NEUTRAL position    
    
def append_weight(weight_data_mean, weight_data_median,
                  weight_data_mode, weight_data_max_mode): #define function for storing weight data
    
    weight_list = {  #make dictionary to store variable values
    "Weight_Mean": [],
    "Weight_Median": [],
    "Weight_Mode": [],
    "Weight_Max_Mode": [],
    "Date_Time": []
    }
    
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

def RFID_check_A(): #define function to check ID of the animal
    RFID_A.close()
    RFID_A.open()
    RFID_A.flush()
    
    for _ in range (5): #perform this check 5 times (if there's more than 1 animal in tube, it will detect it and return the tag)
        line = RFID_A.readline() #rad serial input from RFID antenna
        line_as_str = str(line)
        line_as_list = line_as_str.split(r"b'\x")
        dirty_tag = line_as_list[1]
        tag_as_list = dirty_tag.split("\\r")
        tag = tag_as_list[0] #atfer processing data from RFID antenna, stores it in tag
        
        if tag == '020077914A15B9':
            print("mice A detected")
            which_mouse = "A"
            ID_tag = "mouse A"
#             append_RFID(which_mouse, tag)
            return ID_tag
        elif tag == '00779148D977':
            print("not mouse A")
            ID_tag = "mouse B"
            return ID_tag
        elif tag == '00779149E14E':
            print("not mouse A")
            ID_tag = "mouse C"
            return ID_tag
        elif tag == '000C0BCE2AE3':
            print("not mouse A")
            ID_tag = "mouse D"
            return ID_tag
        else:
            pass
    
    

def append_RFID(which_mouse, tag): #define function  to save which animal was detected and when
    
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

def scan_tube_entry_A(): #define function to check wether there is only one animal in scale
    animal_enter = False
    animal_alone = False
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    while animal_enter == False and animal_alone == False:
#         print("while loop started again")
        line = ser.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        
        if mg > float(10) and mg < float(30):
            print("scale scan: animal on scale, closing doors.")
#             print(line)
            return 'mouse A'
            animal_enter = True
            animal_alone = True
        elif mg >= float(30):
            print("more than one animal on scale, restarting")
            return 'not mouse A'
            animal_enter = True
            animal_alone = False
        else:
            return 'not mouse A'
            animal_enter = False
            animal_alone = False

'''
MODE 1 FUNCTIONS ########################################################################################
'''

def acquire_weight_pre(): #define function to acquire and sotre weight data
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
        print("weight in grams PRE: "+str(mg_pre))

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


def wait_for_animal_to_leave_foor_feeding_area(): #define function for determining if animal has left the tube 
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
        
        if mg < float(5):
            animal_out = True
            print("animal left for feeding area")
            time.process_time()
            return 2 #return value to be assigned to MODE
        else:
            animal_out = False
            return 1
        
'''
MODE 2 FUNCTIONS ########################################################################################
'''

def animal_returned(): #define function t determine whether animal hs returned from feeding area and stores as boolean
    proximity_sensor = bus1.read_pin(1)
    if proximity_sensor == 0: #if proximity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned


def acquire_weight_post(): #define function to acquire and save weight data
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
        print("weight in grams POST: "+str(mg_post))

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
    
    #define variables for comaprison with if clause in the next functuion
    mg_post_mean = weight_data_mean
    mg_post_median = weight_data_median
    
    # change mode and clean up
    del openscale
    
    #return values for comparison
    return mg_post_mean
    

def check_weight_post(mg_pre_mean, mg_post_mean): #define function that compares pre and post weights and deliver proper stimulus
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        buzz.start(50)
        bad_buzz()
        air_puff()
        
    else:
        print("not havier than before. opening door")
        buzz.start(50)
        good_buzz()
        buzz.stop()

def air_puff(): #define function for delivering air puff
    bus1.write_pin(15, 1) #turns air puff on
    time.sleep(3) #waits for 3 seconds
    bus1.write_pin(15, 0) #turns air puff off
        
def bad_buzz(): #define funtion tp be executed when animal is heaveir than chosen weight treshold
    buzz.start(50)
    for _ in range(10):
        print("bad buzz")
        buzz.ChangeFrequency(heavier_buzz_1);
        GPIO.output(redLED, True)
        GPIO.output(greenLED, True)
        time.sleep(0.1)
        buzz.ChangeFrequency(heavier_buzz_2)
        GPIO.output(redLED, False)
        GPIO.output(greenLED, False)
        time.sleep(0.1)
    buzz.stop()

def good_buzz(): #define function to be executed when animal is not heavier tan chosen weight treshold
    buzz.start(50)
    for _ in range (10):
        print("good buzz")
        buzz.ChangeFrequency(not_heavier_buzz_1)
        time.sleep(0.1)
        buzz.ChangeFrequency(not_heavier_buzz_2)
        time.sleep(0.1)
    buzz.stop()
    
def scan_tube_leaving(): #define function for checking if animal has left the scale
    animal_left = False
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
    while animal_left == False:    
        line=ser.readline()
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

def append_rotation(wheel_counter): #define function for storing wheel data
    
    rotation_list = {
    "Rotation": [],
    "Date_Time": []
    }
    
    rotation_list.update({"Rotation": [wheel_counter]})
    rotation_list.update({"Date_Time": [datetime.now()]})

    df_r = pd.DataFrame(rotation_list)
    print(df_r)

    if not os.path.isfile("_rotations.csv"):
        df_r.to_csv("_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv("_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)

def append_pellet(pellet_counter):#define function for storing pellet retrieval data
    
    pellet_list = {
    "Pellet": [],
    "Date_Time": []
    }
    
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

#initialize serial port for RFID reader
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


# set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# set pin outputs to arduino
Pd1_food = 16
Pd1_social = 11
GPIO.setup(Pd1_food,GPIO.OUT)
GPIO.setup(Pd1_social, GPIO.OUT)
GPIO.output(Pd1_food,False)
GPIO.output(Pd1_social, False) #NEUTRAL position

#set pin output to buzzer and LEDs
buzzer = 12
redLED = 35
greenLED = 33
GPIO.setup(buzzer, GPIO.OUT)
buzz = GPIO.PWM(buzzer, 1) #starting frequency is 1 (inaudible)
GPIO.setup(redLED, GPIO.OUT)
GPIO.setup(greenLED, GPIO.OUT)
GPIO.output(buzzer, False)
GPIO.output(redLED, False)
GPIO.output(greenLED, False)

heavier_buzz_1 = 700
heavier_buzz_2 = 589
not_heavier_buzz_1 = 131
not_heavier_buzz_2 = 165


#set pin inputs from running wheel rotary encoder and initialize variables
dt = 38
GPIO.setup(dt,GPIO.IN)
dtLastState = GPIO.input(dt)

wheel_counter = 0;
cycle = 1200; #calibration value
limit = cycle;
turn = 0;
faux_turn = 0

#set pins (bus1 IOPi) for beam break (flying fish) proximity scanner
bus1 = IOPi(0x20) #sets the variable bus1 to the bus 1 adress in IOPi
bus1.set_pin_direction(1, 1) #(pin, direction) #sets pin 1 on bus 1 to as an input pin (1 = input, 0 = output)
bus1.set_pin_pullup(1, 1) #this method allows to enable or disable IOPi to use internall pull-up resistors (1 = enable, 0 = disable)

proximity_sensor = bus1.read_pin(1) #reas pin 1 (bus 1) of the IOPi as the sensor pin for the proximity sensor

#set pins (bus2 IOPi) for output to FED
bus2 = IOPi(0x21)
# bus2.set_pin_direction(13, 1) #input
# bus2.set_pin_pullup(13, 0) #pullup resistors (1 = enabled / 2 = disabled)
bus2.set_pin_direction(14, 0) #output
bus2.write_pin(14, 0) #sets pin 14 as low

#set pin for input from FED
read_FED = 31
GPIO.setup(read_FED, GPIO.IN)
GPIO.add_event_detect(read_FED, GPIO.RISING) #detects rising voltage
pellet_counter = 0

#set pins for air puffs
bus1.set_pin_direction(15, 0) #pin 15 as output
bus1.write_pin(15, 0) #set pin 15 to low/false

#initialize MODE variable
MODE = 0

'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

while True:
    
    if MODE == 0:
        print("\nMODE 0\n")
        move_door_social()
        tagA = RFID_check_A()
        
        if tagA == "mouse A": #CHECK 1: if mouse A is detected, scan tube to check how much weight there is on it
            if_mouse_A = scan_tube_entry_A()
            
            if if_mouse_A == 'mouse A': #CHECK 2: if there is only one mouse, double check that it is mouse A
                tag2A = RFID_check_A()
                        
                if tag2A == "mouse A": #CHECK 3: check RFID tag again, if it is mouse A, then close doors and acquire weight
                    move_door_close() #close doors
                    which_mouse = 'A'
                    MODE = 1
                    
                else:
                    tagA = "not mouse A"
                    MODE = 0
            
            else:
                tagA = "not mouse A"
                MODE = 0
        
        else:# tagA != "mouse A":
            print("not mouse A")
            MODE = 0
                
    elif MODE == 1:
        ser.close()
        print("\nMODE 1\n")
        mg_pre_mean = acquire_weight_pre() #saves the mean weight data
        move_door_feeding() #open door to feeding area
        
        while MODE == 1:
            MODE = wait_for_animal_to_leave_foor_feeding_area() #checks if there is still weight on scale and assign value to MODE variable (1 if animal still in, 2 i animal has left)
        
    elif MODE == 2:
        ser.close()
        
        while MODE == 2:
            dtState = GPIO.input(dt) #read input from running wheel
            returned = animal_returned() #checks if animal has returned from feeding area and store it as boolean
            
            if returned == False: #if animal has not yet returned from feeding area, perform these functions
                
                if dtState != dtLastState: 
                    wheel_counter += 1 #running wheel rotation wheel_counter
                    dtLastState = dtState
                    
                    if wheel_counter >= limit: #when completes 1 full turn (wheel_counter = 1200)
                        turn = wheel_counter/cycle
                        limit = wheel_counter + cycle #reset limit for 1 extra turn
                        print("wheel turns: "+str(turn))
                        
                        if turn % 10 == 0 and turn != 0: #each 10 revolutions
                            print("10 wheel turns, delivering pellet")
                            bus2.write_pin(14, 1) #sends output to FED - turnd FED motor on and makes pellet drop
                    else:
                        pass
                
                elif GPIO.event_detected(read_FED): #detects signal coming from the FED
                    bus2.write_pin(14, 0) #turns FED motor off
                    air_puff() #delivers air puff to animal
                    pellet_counter += 1 #counts one pellet
                    print("Pellet retrieved. Pellet counter: "+str(pellet_counter))
                
                else:
                    pass
                
            
            
            else: #if animal has returned from feeding area, perform these functions
                print("animal returned. acquiring weight")
                print("rotation counter: "+str(wheel_counter))
                move_door_close() #close doors for proper weighting
                append_rotation(wheel_counter) #save running wheel rotation data
                append_pellet(pellet_counter) #save pellet data
                
                wheel_counter = 0 #reset wheel rotation counter
                pellet_counter = 0 #reset pellet counter
                turn = 0 #reset wheel turn counter
                limit = cycle #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                bus2.write_pin(14, 0) #make sure input to FED is low
                dtLastState = GPIO.input(dt) #reset input from wheel 
                
                mg_post_mean = acquire_weight_post() #acquire weight and assign mean weight value
                check_weight_post(mg_pre_mean, mg_post_mean) #compare weights pre and post and delivered stimulus
                move_door_social() #open door to social area
                animal_left = scan_tube_leaving() #scan tube to check whether animal is still in and stores info as boolean
                
                while animal_left == False: #while the animal is still on the tube, perform thee tasks
                    animal_left = scan_tube_leaving() #scan tube to check whether animal is still in and stores info as boolean
                    
                    if animal_left == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_close() #close doors
                        time.sleep(5) #wait for 5 seconds before animal can get in again (timeout)
                        print("cycle over, starting again")
                        MODE = 0 #MODE = 0 makes the code start again
                    else:
                        pass #if animal hasn't left tube yet, keep looping
                        
                
           
