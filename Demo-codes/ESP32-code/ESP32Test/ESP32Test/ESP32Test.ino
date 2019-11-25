#pragma once
//Basic dependencies
#include <stdio.h>
#include "time.h"
#include <driver/adc.h>

//Required for wifi
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <Arduino.h>

//Required for sensor BME280
#include <stdint.h>
#include "SparkFunBME280.h"
#include "Wire.h"
#include "SPI.h"

//Required for RGB sensor
#include "Adafruit_TCS34725.h"

//Global variables
#include "esp_system.h"

uint64_t chipid = ESP.getEfuseMac(); // The chip ID is essentially its MAC address(length: 6 bytes).
uint16_t chip = (uint16_t)(chipid >> 32);
char ssid[23];
const char* timeServer = "time.google.com";
const long  gmtOffset_sec = 7200;
const int   daylightOffset_sec = 0;
const int sleepTime = 10 * 1000000;
const uint16_t port = 4420;
const char * host = "192.168.43.46";
 
WiFiMulti wifiMulti;
//Global sensor object
BME280 atmosphericSensor;
Adafruit_TCS34725 rgbSensor;
//Soil sensor port 
const int soilSensor = 34;

void setup() {
   delay(500);
   snprintf(ssid, 23, "ESP32-%04X%08X", (uint16_t)chip, (uint32_t)chipid);

   adc1_config_width(ADC_WIDTH_BIT_10);
   adc1_config_channel_atten(ADC1_CHANNEL_0,ADC_ATTEN_DB_11);
   Serial.begin(9600);
    //***Driver settings********************************//
    //commInterface can be I2C_MODE or SPI_MODE
    //specify chipSelectPin using arduino pin names
    //specify I2C address.  Can be 0x77(default) or 0x76

    //For I2C, enable the following and disable the SPI section
    atmosphericSensor.settings.commInterface = I2C_MODE;
    atmosphericSensor.settings.I2CAddress = 0x77;
    
    //For SPI enable the following and dissable the I2C section
    //atmosphericSensor.settings.commInterface = SPI_MODE;
    //atmosphericSensor.settings.chipSelectPin = 10;


    //***Operation settings*****************************//

    //runMode can be:
    //  0, Sleep mode
    //  1 or 2, Forced mode
    //  3, Normal mode
    atmosphericSensor.settings.runMode = 3; //Forced mode

    //tStandby can be:
    //  0, 0.5ms
    //  1, 62.5ms
    //  2, 125ms
    //  3, 250ms
    //  4, 500ms
    //  5, 1000ms
    //  6, 10ms
    //  7, 20ms
    atmosphericSensor.settings.tStandby = 0;

    //filter can be off or number of FIR coefficients to use:
    //  0, filter off
    //  1, coefficients = 2
    //  2, coefficients = 4
    //  3, coefficients = 8
    //  4, coefficients = 16
    atmosphericSensor.settings.filter = 0;

    //tempOverSample can be:
    //  0, skipped
    //  1 through 5, oversampling *1, *2, *4, *8, *16 respectively
    atmosphericSensor.settings.tempOverSample = 1;

    //pressOverSample can be:
    //  0, skipped
    //  1 through 5, oversampling *1, *2, *4, *8, *16 respectively
    atmosphericSensor.settings.pressOverSample = 1;

    //humidOverSample can be:
    //  0, skipped
    //  1 through 5, oversampling *1, *2, *4, *8, *16 respectively
    atmosphericSensor.settings.humidOverSample = 1;
    delay(10);  //Make sure sensor had enough time to turn on. BME280 requires 2ms to start up.         Serial.begin(57600);
    while(!Serial);
    Serial.print("Starting BME280... result of .begin(): 0x");
    //Calling .begin() causes the settings to be loaded
    Serial.println(atmosphericSensor.begin(), HEX);
    delay(100);

    rgbSensor = Adafruit_TCS34725();
    if(rgbSensor.begin()) {
      Serial.println("Sensor started");
    }
    
    delay(50);
 
  
  //Start wifimodule, disconnect all prior connection if the module was already on. 
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  
  
  //Connection setup
  const char *WifiName = "Moto";
  const char *Password = "test1234";
  wifiMulti.addAP(WifiName,Password);
  
}



void loop() {
  //if(!WiFi.isConnected()) wifiMulti.run();
  wifiMulti.run();
  
  if(WiFi.isConnected()) {
    Serial.println("In Wifi.isConnected");
    WiFiClient client;
    if(client.connect(host,port)){
      uint16_t r, g, b, c, colorTemp, lux;
  
      rgbSensor.getRawData(&r, &g, &b, &c);
      // colorTemp = tcs.calculateColorTemperature(r, g, b);
      colorTemp = rgbSensor.calculateColorTemperature_dn40(r, g, b, c);
      lux = rgbSensor.calculateLux(r, g, b);
    
      float temp = atmosphericSensor.readTempC();
      float hum = atmosphericSensor.readFloatHumidity();
      float pres = atmosphericSensor.readFloatPressure();
      int soil = analogRead(soilSensor);
      configTime(gmtOffset_sec, daylightOffset_sec, timeServer);
      time_t timetag = time(NULL);
      while(timetag < (time_t)10000){
        timetag = time(NULL);
      }
      client.print("<Object>\n\t<deviceID>"+String(ssid)+"</deviceID>\n\t<Time>"+ (String)timetag + "</Time><Temperature>" + (String)temp + "</Temperature>\n\t<Humidity>" + String(hum) + "</Humidity>\n\t<Pressure>" + String(pres) + "</Pressure>\n\t<Soil>+" + (String)soil + "</Soil>\n\t<ColorTemp>" + (String)colorTemp + "</ColorTemp>\n\t<Lux>" + (String)lux + "</Lux>\n\t<RGB>(" + (String)r + "," + String(g) + "," + (String)b + ")</RGB>\n</Object>");
      delay(50);
      Serial.println("Sent");
      
      client.stop();
      //15 min 900000
      //delay(10000);
      WiFi.disconnect();
      esp_sleep_enable_timer_wakeup(sleepTime);
      esp_deep_sleep_start();
    }
    }
    delay(100);
    Serial.println(WiFi.status());
    WiFi.disconnect();
    esp_sleep_enable_timer_wakeup(sleepTime);
    esp_deep_sleep_start();
}
 
  

  
  
  
