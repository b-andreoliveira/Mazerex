#include<Servo.h>
Servo servo1;     // Servo 1
#include<Servo.h>
Servo servo2;     
#include<Servo.h>
Servo servo3;     
#include<Servo.h>
Servo servo4;     

const int servoPin1 = 5;  // output to servos 1-4
const int servoPin2 = 6;
const int servoPin3 = 3;
const int servoPin4 = 9;

const int slowness = 8;   //slowness factor, ms wait between 1deg movements, change to set speed
                           
//SERVO 1
const int d1_food = 75;   //servo positions; calibrate manually//servo positions; calibrate manually
const int d1_social = 125;  
const int d1_close = 100;

//SERVO 2 
const int d2_food = 120;   
const int d2_social = 75;  
const int d2_close = 100; 

//SERVO 3
const int d3_food = 100;   
const int d3_social = 60;  
const int d3_close = 80; 

//SERVO 4
const int d4_food = 45;   
const int d4_social = 95;  
const int d4_close = 70; 

// input commands from Pi 
const int Pd1_food = 2;  
const int Pd1_social = 4;

const int Pd2_food = 7;      
const int Pd2_social = 8;

const int Pd3_food = 10;   
const int Pd3_social = 11;

const int Pd4_food = 12;      
const int Pd4_social = 13;

int pos1_current = d1_food; //initial position variables for servos
int pos1_target = d1_food;
int pos2_current = d2_food; //initial position variables for servos
int pos2_target = d2_food;
int pos3_current = d3_food; //initial position variables for servos
int pos3_target = d3_food;
int pos4_current = d4_food; //initial position variables for servos
int pos4_target = d4_food;

void setup() {
  // put your setup code here, to run once:
  
//check door operation
servo1.attach(servoPin1);
servo1.write(pos1_current); 
pos1_target=d1_close; //will go slowly to closed when arduino code runs correctly without pi input.
delay(500);
servo2.attach(servoPin2);
servo2.write(pos2_current); 
pos2_target=d2_close;
delay(500);
servo3.attach(servoPin3);
servo3.write(pos3_current); 
pos3_target=d3_close;
delay(500);
servo4.attach(servoPin4);
servo4.write(pos4_current); 
pos4_target=d4_close;
delay(500);

pinMode(Pd1_food, INPUT);// input commands from Pi
pinMode(Pd1_social, INPUT);
pinMode(Pd2_food, INPUT);
pinMode(Pd2_social, INPUT);
pinMode(Pd3_food, INPUT);// input commands from Pi
pinMode(Pd3_social, INPUT);
pinMode(Pd4_food, INPUT);
pinMode(Pd4_social, INPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  
//new servo if loops
  if (pos1_current<pos1_target) //SERVO 1
  {
    pos1_current=pos1_current+1;
    servo1.write(pos1_current);     
    delay(slowness); 
  }
  if (pos1_current>pos1_target)
  {
    pos1_current=pos1_current-1;
    servo1.write(pos1_current);     
    delay(slowness); 
  }
  
  if (pos2_current<pos2_target) //SERVO 2
  {
    pos2_current=pos2_current+1;
    servo2.write(pos2_current);     
    delay(slowness); 
  }
  if (pos2_current>pos2_target)
  {
    pos2_current=pos2_current-1;
    servo2.write(pos2_current);     
    delay(slowness); 
  }

  if (pos3_current<pos3_target) //SERVO 3
  {
    pos3_current=pos3_current+1;
    servo3.write(pos3_current);     
    delay(slowness); 
  }
  if (pos3_current>pos3_target)
  {
    pos3_current=pos3_current-1;
    servo3.write(pos3_current);     
    delay(slowness); 
  }
  
  if (pos4_current<pos4_target) //SERVO 4
  {
    pos4_current=pos4_current+1;
    servo4.write(pos4_current);     
    delay(slowness); 
  }
  if (pos4_current>pos4_target)
  {
    pos4_current=pos4_current-1;
    servo4.write(pos4_current);     
    delay(slowness); 
  }
  
  //target commands
  
  //SERVO 1
    
  if ((digitalRead(Pd1_social) == HIGH)) 
    {
    pos1_target=d1_social;
    }
  if ((digitalRead(Pd1_food) == HIGH)) 
    {
    pos1_target=d1_food;
    }
  if ((digitalRead(Pd1_food) == LOW) && (digitalRead(Pd1_social) == LOW)) 
    {
    pos1_target=d1_close;
    }
  
  //SERVO 2
  if ((digitalRead(Pd2_social) == HIGH)) 
    {
    pos2_target=d2_social;
    }
  if ((digitalRead(Pd2_food) == HIGH)) 
    {
    pos2_target=d2_food;
    }
  if ((digitalRead(Pd2_food) == LOW) && (digitalRead(Pd2_social) == LOW)) 
    {
    pos2_target=d2_close;
    }
  
  //SERVO 3
  if ((digitalRead(Pd3_social) == HIGH)) 
    {
    pos3_target=d3_social;
    }
  if ((digitalRead(Pd3_food) == HIGH)) 
    {
    pos3_target=d3_food;
    }
  if ((digitalRead(Pd3_food) == LOW) && (digitalRead(Pd3_social) == LOW)) 
    {
    pos3_target=d3_close;
    }
  
  //SERVO 4
  if ((digitalRead(Pd4_social) == HIGH)) 
    {
    pos4_target=d4_social;
    }
  if ((digitalRead(Pd4_food) == HIGH)) 
    {
    pos4_target=d4_food;
    }
  if ((digitalRead(Pd4_food) == LOW) && (digitalRead(Pd4_social) == LOW)) 
    {
    pos4_target=d4_close;
    }

}
