#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int neutral = 70;
int food = 100;
int social = 95;

// SERVO 1
// neutral = 100
// food = 75
// social = 120

// SERVO 2
// neutral = 80
// food = 103
// social = 56

// SERVO 3
// neutral = 80
// food = 100
// social = 60

// SERVO 4
// neutral = 70 
// food = 45
// social = 95


void setup() {
  myservo.attach(3);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  pos = food;
  myservo.write(pos);
}
