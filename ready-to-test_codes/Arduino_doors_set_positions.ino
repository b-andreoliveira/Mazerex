#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int neutral = 100;
int food = 120;
int social = 75;

// SERVO 1
// food = 75
// social = 120
// closed = 100

// SERVO 2
// food = 103
// social = 56
// closed = 80

// SERVO 3
// food = 45
// social = 95
// closed = 75

// SERVO 4 
// food = 110
// social = 50
// closed = 75


void setup() {
  myservo.attach(6);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  pos = food;
  myservo.write(pos);
}
