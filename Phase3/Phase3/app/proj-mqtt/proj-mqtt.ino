#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

DHTesp dht;
const char* ssid = "";
const char* password = "";
const char* mqtt_server = "192.168.";
const int pResistor = A0; // Photoresistor at Arduino analog pin A0
int value;
const int ledPin = D3; // LED at Arduino digital pin D3

WiFiClient vanieriot;
PubSubClient client(vanieriot);

void setup_wifi(){
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(String topic, byte* message, unsigned int length){
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;

  for(int i = 0; i < length; i++){
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }
}

void reconnect(){
  while(!client.connected()){
    Serial.print("Attempting MQTT connection...");
    if(client.connect("vanieriot")){
      Serial.println("connected");
    }else{
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      // Wait 5 seconds before retrying
      delay(3000);    
    }
  }  
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  pinMode(pResistor, INPUT); 
  pinMode(ledPin, OUTPUT);
  dht.setup(4, DHTesp::DHT11);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(!client.connected()){
    reconnect();  
  }
  if(!client.loop()){
    client.connect("vanieriot");
  }
    value = analogRead(pResistor);
    float temp= dht.getTemperature();
    //float temp= 30;
    float hum= dht.getHumidity();
    
    Serial.print("Light intensity is: ");
    Serial.println(value);
    char photoArr[8];

    char tempArr[8];
    dtostrf(temp, 6, 2, tempArr);
    Serial.print("Temperature is: ");
    Serial.println(tempArr);
    
    char humArr[8];
    dtostrf(hum, 6, 2, humArr);
    Serial.print("Humidity is: ");
    Serial.println(humArr);

    sprintf(photoArr, "%d", value);
    client.publish("vanieriot/photoValue", photoArr);
    client.publish("vanieriot/temperature", tempArr);
    client.publish("vanieriot/humidity", humArr);
    
 if (value < 650) {
    digitalWrite(ledPin, HIGH);
    Serial.println("LED is on");
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("LED is off");
  }
    delay(3000);
}
