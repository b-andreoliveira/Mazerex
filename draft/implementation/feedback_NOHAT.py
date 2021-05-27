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

'''set GPIO numbering mode'''
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

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
        
while True:
    
    bad_buzz('A')
    time.sleep(1)
    bad_buzz('B')
    time.sleep(1)
    good_buzz('A')
    time.sleep(1)
    good_buzz('B')
    time.sleep(1)