#include<Servo.h>
Servo servo1;     // Servo 1
#include<Servo.h>
Servo servo2;     
#include<Servo.h>
Servo servo3;     
#include<Servo.h>
Servo servo4;     

const int servoPin1 = 5;      // output to servos 1-4
const int servoPin2 = 6;
const int servoPin3 = 3;
const int servoPin4 = 9;
int d1_f=LOW;

                           //servo positions; calibrate manually
//SERVO 1
const int d1_food = 75;   
const int d1_social = 125;  
const int d1_close = 100;

//SERVO 2 
const int d2_food = 120;   
const int d2_social = 75;  
const int d2_close = 100; 

//SERVO 3
const int d3_food = 45;   
const int d3_social = 95;  
const int d3_close = 75; 

//SERVO 4
const int d4_food = 110;   
const int d4_social = 50;  
const int d4_close = 75; 

// input commands from Pi 
const int Pd1_food = 2;  
const int Pd1_social = 4;

const int Pd2_food = 7;      
const int Pd2_social = 8;

const int Pd3_food = 10;   
const int Pd3_social = 11;

const int Pd4_food = 12;      
const int Pd4_social = 13;

void setup() {
  // put your setup code here, to run once:
  
//check door operation
servo1.attach(servoPin1);
servo1.write(d1_food);
delay(500);
servo1.write(d1_close);
delay(500);
servo1.write(d1_social);
delay(500);

servo2.attach(servoPin2);
servo2.write(d2_food);
delay(500);
servo2.write(d2_close);
delay(500);
servo2.write(d2_social);
delay(500);

servo3.attach(servoPin3);
servo3.write(d3_food);
delay(500);
servo3.write(d3_close);
delay(500);
servo3.write(d3_social);
delay(500);

servo4.attach(servoPin4);
servo4.write(d4_food);
delay(500);
servo4.write(d4_close);
delay(500);
servo4.write(d4_social);
delay(500);

pinMode(Pd1_food, INPUT);// input commands from Pi
pinMode(Pd1_social, INPUT);
pinMode(Pd2_food, INPUT);
pinMode(Pd2_social, INPUT);
pinMode(Pd3_food, INPUT);// input commands from Pi
pinMode(Pd3_social, INPUT);
pinMode(Pd4_food, INPUT);
pinMode(Pd4_social, INPUT);

servo1.write(d1_close);
servo2.write(d2_close);
servo3.write(d3_close);
servo4.write(d4_close);

Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:

//SERVO 1
  
if ((digitalRead(Pd1_social) == HIGH)) {
  servo1.write(d1_social);
  }
if ((digitalRead(Pd1_food) == HIGH)) {
  servo1.write(d1_food);
  }
if ((digitalRead(Pd1_food) == LOW) && (digitalRead(Pd1_social) == LOW)) {
    servo1.write(d1_close);
  }

//SERVO 2
if ((digitalRead(Pd2_social) == HIGH)) {
  servo2.write(d2_social);
  }
if ((digitalRead(Pd2_food) == HIGH)) {
  servo2.write(d2_food);
  }
if ((digitalRead(Pd2_food) == LOW) && (digitalRead(Pd2_social) == LOW)) {
    servo2.write(d2_close);
  }

//SERVO 3
if ((digitalRead(Pd3_social) == HIGH)) {
  servo3.write(d3_social);
  }
if ((digitalRead(Pd3_food) == HIGH)) {
  servo3.write(d3_food);
  }
if ((digitalRead(Pd3_food) == LOW) && (digitalRead(Pd3_social) == LOW)) {
  servo3.write(d3_close);
  }

//SERVO 4
if ((digitalRead(Pd4_social) == HIGH)) {
  servo4.write(d4_social);
  }
if ((digitalRead(Pd4_food) == HIGH)) {
  servo4.write(d4_food);
  }
if ((digitalRead(Pd4_food) == LOW) && (digitalRead(Pd4_social) == LOW)) {
  servo4.write(d4_close);
  }

}
