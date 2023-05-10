#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN D8
#define RST_PIN D0
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key;
// Init array that will store new NUID
byte nuidPICC[4];

DHTesp dht;
const char* ssid = "Sunny";
const char* password = "iotproject";
const char* mqtt_server = "192.168.30.220";

const int pResistor = A0; // Photoresistor at Arduino analog pin A0
int value;
const int ledPin = 0; // LED at Arduino digital pin D3

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
  Serial.println("Program starting");
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  pinMode(pResistor, INPUT); 
  pinMode(ledPin, OUTPUT);
  dht.setup(4, DHTesp::DHT11);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
  Serial.println();
  Serial.print(F("Reader: "));
  rfid.PCD_DumpVersionToSerial();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  Serial.println();
  Serial.println(F("This code scan the MIFARE Classic NUID."));
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
    client.publish("vanieriot/photoValue1", photoArr);
    client.publish("vanieriot/temperature1", tempArr);
    client.publish("vanieriot/humidity1", humArr);

  if (value < 650) {
    digitalWrite(ledPin, HIGH);
    Serial.println("LED is on");
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("LED is off");
  }
    delay(3000);

    if ( ! rfid.PICC_IsNewCardPresent())
      return;
    if ( ! rfid.PICC_ReadCardSerial())
      return;
    String RFIDStr = "";
    Serial.print(F("PICC type: "));
    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);  
    Serial.println(rfid.PICC_GetTypeName(piccType));
    Serial.print(F("Tag ID: "));
    printDec(rfid.uid.uidByte, rfid.uid.size);
    Serial.println(); 
    // Check is the PICC of Classic MIFARE type
    if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
        piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
        piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
          Serial.println(F("Your tag is not of type MIFARE Classic."));
          return;
    }
       // Check if the tag is different from the previous one
    /*if (rfid.uid.uidByte[0] != nuidPICC[0] ||
        rfid.uid.uidByte[1] != nuidPICC[1] ||
        rfid.uid.uidByte[2] != nuidPICC[2] ||
        rfid.uid.uidByte[3] != nuidPICC[3] ) {*/

      Serial.println(F("A card has been detected."));

      // Store NUID into nuidPICC array
      for (byte i = 0; i < 4; i++) {
        nuidPICC[i] = rfid.uid.uidByte[i];
        String temp = String(rfid.uid.uidByte[i], HEX);
        RFIDStr += temp;
      }

      Serial.println(F("The NUID tag is:"));
      Serial.print(F("In dec: "));
      printDec(rfid.uid.uidByte, rfid.uid.size);
      Serial.println();

//      char RFIDStr[3*rfid.uid.size + 1]; // Initialize a char array to hold the RFID value as a string
//      for (int i = 0; i < rfid.uid.size; i++) {
//        sprintf(&RFIDStr[3*i], "%02X ", rfid.uid.uidByte[i]); // Convert each byte to a two-digit hexadecimal string
//      }
//      RFIDStr[3*rfid.uid.size - 1] = '\0'; // Null-terminate the string

      client.publish("vanieriot/RFID", RFIDStr.c_str());
      //client.publish("vanieriot/RFID", RFIDStr);
      Serial.println(RFIDStr.c_str());
      //Serial.println(RFIDStr);
    //}
    // Halt PICC
    rfid.PICC_HaltA();

    // Stop encryption on PCD
    rfid.PCD_StopCrypto1();
}

void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}
