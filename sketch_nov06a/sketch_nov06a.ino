     

int data = 0; 
char userInput; 
int ledPin = 2;
void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);          //  setup serial
    pinMode(ledPin ,OUTPUT);
    pinMode(A0,INPUT);

}

void loop() {
    


    digitalWrite(ledPin, 0 );
    delay(5000);
    digitalWrite(ledPin, 0);
    delay(200000);
    digitalWrite(ledPin, 0);
    delay(5000);
    

  
}
