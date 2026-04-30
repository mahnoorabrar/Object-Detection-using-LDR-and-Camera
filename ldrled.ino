// Arduino code for LDR reading and LED control

const int ledPin = 11;  // LED connected to pin 11
const int ldrPin = A0;  // LDR sensor connected to analog pin A0
int ldrValue = 0;       // Variable to store LDR value
char incomingByte;      // Variable to store incoming serial data

void setup() {
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  
  // Configure pin modes
  pinMode(ledPin, OUTPUT);
  pinMode(ldrPin, INPUT);
  
  // Initialize LED to OFF state
  digitalWrite(ledPin, LOW);
  
  // Wait for serial connection to stabilize
  delay(1000);
  
  // Indicate Arduino is ready
  Serial.println("Arduino Ready");
}

void loop() {
  // Read the LDR value
  ldrValue = analogRead(ldrPin);
  
  // Send LDR value to Python
  Serial.println(ldrValue);
  
  // Check if data is available from Python
  if (Serial.available() > 0) {
    // Read the incoming byte
    incomingByte = Serial.read();
    
    // Process the command from Python
    if (incomingByte == '1') {
      
      digitalWrite(ledPin, HIGH);
      Serial.println("LED ON");
    } 
    else if (incomingByte == '0') {
      
      digitalWrite(ledPin, LOW);
      Serial.println("LED OFF");
    }
  }
  
  // Small delay 
  delay(100);
}