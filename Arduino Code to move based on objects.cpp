#include <Wire.h>

// --- Adjust these to your specific motor driver wiring ---
const int ENA = 9;  
const int IN1 = 8;  
const int IN2 = 7;  
const int ENB = 10; 
const int IN3 = 11; 
const int IN4 = 12; 

const int I2C_ADDRESS = 0x08;
volatile int leftSpeed = 0;
volatile int rightSpeed = 0;

void setup() {
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent); 
}

void loop() {
  driveMotor(ENA, IN1, IN2, leftSpeed);
  driveMotor(ENB, IN3, IN4, rightSpeed);
  delay(10);
}

// Interrupt: Triggers when Pi sends data over I2C
void receiveEvent(int howMany) {
  if (howMany >= 3) { 
    Wire.read(); // Discard the register byte
    // Decode bytes back to -100 to 100 range
    leftSpeed = Wire.read() - 128;
    rightSpeed = Wire.read() - 128; 
  }
}

void driveMotor(int enPin, int in1Pin, int in2Pin, int speed) {
  if (speed > 0) {
    digitalWrite(in1Pin, HIGH); digitalWrite(in2Pin, LOW); // Forward
  } else if (speed < 0) {
    digitalWrite(in1Pin, LOW); digitalWrite(in2Pin, HIGH); // Reverse
    speed = -speed; 
  } else {
    digitalWrite(in1Pin, LOW); digitalWrite(in2Pin, LOW); // Stop
  }
  
  // Convert -100 to 100 speed into 0-255 PWM duty cycle
  int pwmValue = constrain(map(speed, 0, 100, 0, 255), 0, 255); 
  analogWrite(enPin, pwmValue);
}