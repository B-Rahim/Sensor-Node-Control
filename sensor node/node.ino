#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <PubSubClient.h> // Allows us to connect to, and publish to the MQTT broker
#include <WiFiClientSecure.h>


// WiFi
// Make sure to update this for your own WiFi network!
const char* ssid = "GalaxyA113067";
const char* wifipassword = "bspr3246";

// MQTT
// Make sure to update this for your own MQTT Broker!
const char* mqtt_server = "192.168.43.217";
const char* mqtt_topic_d = "/display";
const char* mqtt_topic_s = "/sensor";
const char* mqtt_username = "iocProject";
const char* mqtt_password = "rahimTT";
// The client id identifies the ESP device. Think of it a bit like a hostname (Or just a name, like Greg).
const char* clientID = "ID";

WiFiClient wifi;

PubSubClient client(mqtt_server, 1883, wifi); // 1883 is the listener port for the Broker

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_RESET     16 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3D ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32

TwoWire twi = TwoWire(1); // our own TwoWire instance on bus 1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &twi, OLED_RESET);

int sensorPin = A0;    // select the input pin for the photo-resistor
int sensorValue = 0;  // variable to store the value coming from the sensor

void setup_Oled(){
  twi.begin(4,15); 
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.setTextSize(2); // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(40, 0);

}

void Oled_disp(String s) {
  display.clearDisplay();
  display.setCursor(1, 1);
  display.print(s);
  display.display();
}

void setup_wifi(){
    Serial.print("Connecting to SSID: ");
    Serial.println(ssid);

    WiFi.begin(ssid, wifipassword);

    while( WiFi.status() != WL_CONNECTED ) {
        Serial.print(".");
        delay(1000);
    }

    Serial.print("Connected to ");
    Serial.println(ssid);
}

void ReceivedMessage(char* topic, byte* payload, unsigned int length) {
  // Output the first character of the message to serial (debug)
  char msg[length+1];

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    msg[i] = (char)payload[i];
    Serial.print((char)payload[i]);
  }
  msg[length]=0;
  Serial.println();  
  if(!strcmp(topic, "/display")){
     Oled_disp(msg);
  }
}
void Connect()
{
  if (client.connect(clientID, mqtt_username, mqtt_password)){
          client.subscribe(mqtt_topic_d);
          Serial.println("Connected to MQTT Broker!");
  }
  else
    Serial.println("Connection to MQTT Broker failed...");
}
void setup_mqtt(){
    client.setCallback(ReceivedMessage);
  // Connect to MQTT Broker
  // client.connect returns a boolean value to let us know if the connection was successful.
  // If the connection is failing, make sure you are using the correct MQTT Username and Password (Setup Earlier in the Instructable)
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(clientID,  mqtt_username, mqtt_password)) {
      Serial.println("connected");
      // Subscribe
      client.subscribe(mqtt_topic_d);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      if(WiFi.status() != WL_CONNECTED)
        Serial.println("not connected to wifi");
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);
    setup_Oled();
    setup_wifi();
    setup_mqtt();
}

int interval = 1000; //in mili seconds
void loop() {
  static unsigned long prevMillis = millis();

  // put your main code here, to run repeatedly:
    if (!client.connected()) {
    Connect();
  }
  // client.loop() just tells the MQTT client code to do what it needs to do itself (i.e. check for messages, etc.)
  client.loop();

  if (millis() - prevMillis >= interval) {
    sensorValue = 4096 - analogRead(sensorPin);
    client.publish(mqtt_topic_s,String(sensorValue).c_str());
    Serial.println(String(sensorValue));
    prevMillis = millis();
  }

}
