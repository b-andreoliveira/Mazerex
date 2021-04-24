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

def animal_entry():
    global proximity_sensor
    animal_enter = False
    
    while animal_enter == False:
        
        if proximity_sensor == 0: #if prosimity sensor is low (eg detected something)
            print("IR sensor: animal on scale, closing doors.")
            return True #return true if animal returned
            animal_enter = True
        else:
            return False #return false if animal not returned
            animal_enter = False

def scan_tube_entry():
    animal_enter = False
    openscale = [] #store weights here
    ser.close()
    ser.open()
    ser.flush()
    for _ in range(8): # chuck two lines 
        line=ser.readline()
        
    while animal_enter == False:
#         print("while loop started again")
        line = ser.readline()
        line_as_list = line.split(b',')
        relProb = line_as_list[0]
        relProb_as_list = relProb.split(b'\n')
        relProb_float = float(relProb_as_list[0])
        mg = relProb_float*1000
        if mg > float(10):
            print("scale scan: animal on scale, closing doors.")
#             print(line)
            return True
            animal_enter = True
        else:
#             print("not enough weight on scale.")
#             print(line)
            animal_enter = False
#             countdown()
#             ser.close()
#             ser.open()
#             ser.flush()
#             for _ in range(8):
#                 line = ser.readline
#             print(line)
#           
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

def air_puff():
    bus1.write_pin(15, 1) #turns air puff on
    time.sleep(3) #waits for 3 seconds
    bus1.write_pin(15, 0) #turns air puff off


def check_weight_post(mg_pre_mean, mg_post_mean):
    global MODE
    
    if mg_post_mean > mg_pre_mean:
        print("heavier than before. initializing buzzer")
        buzz.start(50)
        bad_buzz()
        air_puff()
        move_door_N2S()
#         MODE = 1
        
    else:
        print("not havier than before. opening door")
        buzz.start(50)
        good_buzz()
        buzz.stop()
        move_door_N2S()
#         MODE = 1

#played when animal is heaveir than chosen weight treshold
def bad_buzz():
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

#played when animal is not heavier tan chosen weight treshold
def good_buzz():
    buzz.start(50)
    for _ in range (10):
        print("good buzz")
        buzz.ChangeFrequency(not_heavier_buzz_1)
        time.sleep(0.1)
        buzz.ChangeFrequency(not_heavier_buzz_2)
        time.sleep(0.1)
    buzz.stop()

def animal_returned():
    global proximity_sensor
    if proximity_sensor == 0: #if prosimity sensor is low (eg detected something)
        return True #return true if animal returned
    else:
        return False #return false if animal not returned

def scan_tube_leaving():
    animal_left = False
    openscale = [] #store weights here
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
#             print("animal still on scale")
            animal_left = False
#             MODE = 1
            return False
#             time.sleep(1)
            
def move_door_close():
    GPIO.output(Pd1_food, False)
    GPIO.output(Pd1_social, False) #NEUTRAL position

#define function for storing wheel data
def append_rotation(wheel_counter):
    
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

#define function for storing pellet retrieval data
def append_pellet(pellet_counter):
    
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
clk = 37
dt = 38

GPIO.setup(clk,GPIO.IN)
GPIO.setup(dt,GPIO.IN)
clkLastState = GPIO.input(clk)
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
MODE = 1



'''
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
CODE EXECUTION
-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
'''

while True:
    
    if MODE == 1:
        ser.close()
        print("\nMODE 1\n")
        countdown()
        animal_entered = scan_tube_entry() #proximity sensor checks if animal is in tube and stores as boolean
#         animal_entered2 = animal_entry() #scan tube to check whether animal is in (>10g) and stores it as boolean (true/false)
        
        if animal_entered == True:
            time.sleep(3) #wait for the animal to get inside the tube before closing door
            ''' IDEA: maybe couple door closing with proximity sensor to be sure tha the animal has entered the tube before closing doors '''
            move_door_S2N() #close door for proper weighting - NEUTRAL position
            mg_pre_mean = acquire_weight_pre() #acquire weight and assign mean weight value
            move_door_N2F() #open door - FOOD position
#             timer_feed_start = time.process_time()  #time stamp start
            timer_feed_start = wait_for_animal_to_leave_foor_feeding_area() #time stamp start
        
            
        else:
            pass
#             countdown()
#             MODE = 1
    
    if MODE == 2:
        ser.close()
        
        while MODE == 2:
            dtState = GPIO.input(dt) #read input from running wheel
            proximity_sensor = bus1.read_pin(1) #read input from proximity sensor
            returned = animal_returned() #checks whether animal has returned and stores as boolean (true/false)
             
            if returned == False: #while animal has not returned, perform these tasks
                if dtState != dtLastState: #running wheel rotation wheel_counter
                    wheel_counter += 1
                    dtLastState = dtState
                
                    if wheel_counter >= limit: #when completes 1 full turn (wheel_counter = 1200)
                        turn = wheel_counter/cycle
#                         faux_turn += 1 #temp variable, used for the subsequent if statement
                        limit = wheel_counter + cycle #reset limit for 1 extra turn
                        print("wheel turns: "+str(turn))
                    
                        if turn % 10 == 0 and turn != 0: #each 10 revolutions
                            print("10 wheel turns, delivering pellet")
#                             print("wheel counter : "+str(wheel_counter))
#                             print(turn)
                            bus2.write_pin(14, 1) #sends output to FED - turnd FED motor on and makes pellet drop
                    else:
                        pass
                        
                elif GPIO.event_detected(read_FED):
                    print("pellet retrieved")
                    bus2.write_pin(14, 0) #turns FED motor off
                    pellet_counter += 1
                    print("pellet counter: "+str(pellet_counter))
                    append_pellet(pellet_counter)
                
                else:
                    pass

            
            elif returned == True: #if animal has returned, perform these tasks
                timer_feed_end = time.process_time() #time stamp current update
                print("animal returned. acquiring weight")
                print("rotation counter: "+str(wheel_counter))
                move_door_F2N() #close doors for proper weighting
                append_rotation(wheel_counter) #save running wheel rotation data
                wheel_counter = 0 #reset wheel rotation counter
                pellet_counter = 0 #reset pellet counter
                turn = 0 #reset wheel turn counter
                limit = cycle #reset wheel turn limit counter (used to coutn when wheel makes 1 complete revolution)
                bus2.write_pin(14, 0) #make sure input to FED is low
                dtLastState = GPIO.input(dt) #reset input from wheel 
                mg_post_mean = acquire_weight_post() #acquire weight and assign mean weight value
                check_weight_post(mg_pre_mean, mg_post_mean) #compare weights pre and post and delivered stimulus
                how_long_animal_stayed_in_feeding_area = timer_feed_end - timer_feed_start
                animal_left = scan_tube_leaving() #scan tube to check whether animal is still in and stores info as boolean
                
                while animal_left == False: #while the animal is still on the tube, perform thee tasks
                    animal_left = scan_tube_leaving() #scan tube to check whether animal is still in and stores info as boolean
                    
                    if animal_left == True: #if animal leaves the tube, perform these tasks
                        time.sleep(2) #wait two seconds for animal to completely leave the tube before closing doors
                        move_door_close()
                        print("cycle over, starting again")
                        MODE = 1 #MODE = 1 makes the code start again
                    else: #if animal hasn't left tube yet, keep looping
                        pass

                    
                    
                
                

