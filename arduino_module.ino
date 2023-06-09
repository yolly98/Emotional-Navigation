#define BUTTON 2
#define LED 3

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
    Serial.println("PENDING");
  }

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    if (cmd == "ON"){
      digitalWrite(LED, HIGH);
    }
    else if (cmd == "OFF"){
      digitalWrite(LED, LOW);
      started = false;
    }
 }
 delay(100);
}