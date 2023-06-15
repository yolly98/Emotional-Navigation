#define BUTTON 3
#define LED 2

bool started = false;

void setup() {
  pinMode(BUTTON, INPUT_PULLDOWN);
  pinMode(LED, OUTPUT);
  Serial.begin(9600);

  digitalWrite(LED, LOW);
}

void loop() {

  bool buttonState = digitalRead(BUTTON);

  if (buttonState == HIGH && !started) {
    started = true;
    Serial.println("PRESSED");
  }
  else if(buttonState == LOW) {
    started = false;
  }

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    if (cmd == "ON"){
      digitalWrite(LED, HIGH);
    }
    else if (cmd == "OFF"){
      digitalWrite(LED, LOW);
    }
 }
 delay(100);
}