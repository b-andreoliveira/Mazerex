#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int neutral = 95;
int food = 68;
int social = 120;

// SERVO 1
// neutral = 95
// food = 68
// social = 120

// SERVO 2
// neutral = 70
// food = 100
// social = 53

void setup() {
  myservo.attach(2);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  pos = food;
  myservo.write(pos);
} 
