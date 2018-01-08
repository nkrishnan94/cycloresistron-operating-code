 int i, c;

int numIteration = 10;

#include <SerialCommand.h>

// SerialCommand object
SerialCommand sCmd;


void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);          //  setup serial
    
    pinMode(A0, INPUT);
    for (i = 2; i < 5; i++) {
      pinMode(i, OUTPUT);
      digitalWrite(i, 0);
      }

    sCmd.addCommand("PUMP", pumpCtrl); // Turn on/off peristaltic pump 
    
    sCmd.addCommand("MEASURE", readSensorAll);
}

void loop() {
  
  sCmd.readSerial(); // We don't do much, just process serial commands
  

}

void pumpCtrl() {
  //
  //  Syntax: PUMP <pin no.> <1/0>
  //     e.g. "PUMP 28 1" (turn on a waster pump connected to pin 28)
  //

  int pNum; // waste pump number 
  int pState; // pump state 
  char *arg;
  int readOK; 
  
  //Serial.println("We're in processCommand");

  // read pump number 
  arg = sCmd.next();
  if (arg != NULL) {
    pNum = atoi(arg); // N-th pump (N=0-8?)
    
    // read pump state
    arg = sCmd.next();
    if (arg != NULL) {
      pState = atoi(arg); // 0 or 1
      
      // set pump state 
     digitalWrite(pNum, pState); 
    }
  }
}


void readSensorAll() {
  //
  //  Syntax:  "MEASURE" (No parameter. Read all 8 analog inputs)
  // 

  for (i = 0; i < 16; i++) { 
    // initialise buffer variable
    unsigned long voltagebuff = 0; 

    // call analogRead once to switch the pin to the ADC.
    // this will help the measurement accurate and consistent. 
    // see http://forums.adafruit.com/viewtopic.php?f=25&t=11597
    analogRead(54+i);  
    delay(1);

    // read sensor <numIteration> times 
    for (c = 0; c <= numIteration; c++) {
      // Read from A0-A7. 
      // pin assignments are A0=54, A1=55, and so on. See c:/Program Files (x86)/Arduino/hardware/arduino/variants/mega/pins_arduino.h for details.
      voltagebuff += analogRead(54+i);  
      delayMicroseconds(1);
      //delay(1);
    }  
    // return averaged value
    Serial.println(voltagebuff/numIteration, DEC);
    //Serial.print(" ");  
  }
  //Serial.print("\n");  
}

