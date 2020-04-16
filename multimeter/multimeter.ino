#define ratio 0.091

float input_voltage = 0.0;
float temp=0.0;

void setup() {
    Serial.begin(9600);     //  opens serial port, sets data rate to 9600 bps
}

void loop() {
    int analog_value = analogRead(A0);
    temp = (analog_value * 5.0) / 1023.0; 
    input_voltage = temp / ratio ; 
    Serial.println(input_voltage);
    delay(10);
}
