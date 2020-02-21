
//Basic dependencies
#include "esp_system.h"
#include "GreenthumbIoTConfigStandard.h"
#include <stdio.h>
#include "time.h"
#include <driver/adc.h>
#include "GreenthumbIoT.h"

//Bluetooth
#include "BluetoothSerial.h"

//Hash
#include <mbedtls/AES.h>

//Flash memory writer
#include <EEPROM.h>


//Required for wifi
#include <WiFiMulti.h>

//Required for sensor BME280
#include <stdint.h>
#include "SparkFunBME280.h"
#include "Wire.h"

//Required for luminosity sensor
#include "SparkFun_APDS9960.h"

//***Global variables***//
const unsigned int serialKeyLength = 23;

//Variable to distinct whether the connection setup has been done
RTC_DATA_ATTR int connectionSetup = 1;

//Size of connection information written to user space
RTC_DATA_ATTR int flashWriteSize;

//Set Raspberrypi connection settings from GreenthumbIoTConfig.h.h
String WifiName;
String Password;
String Host;
uint16_t Port;

//Serial key
char espId[serialKeyLength];

//Soil sensor port, loaded from GreenthumbIoTConfig.h
const int soilSensor = SOILSENSORPIN;


//Time settings
const char* timeServer = TIMESERVER;
const long gmtOffset_sec = GMTOFFSET;
const int daylightOffset_sec = DAYLIGHTOFFSET;

//Sleep settings
const int microSecondToSecondConvertFactor = 1000000;
const int sleepTime = SLEEP * microSecondToSecondConvertFactor;
const int retrySleepTime = RETRYSLEEP * microSecondToSecondConvertFactor;

//Wifi accesspoint
WiFiMulti wifiMulti;

//Global sensor objects
BME280 atmosphericSensor;

//Luminosity sensor
SparkFun_APDS9960 apds = SparkFun_APDS9960();


void setup() {

    
    delay(500);
    //Serial.begin(115200);
   
    //while(!Serial);
    EEPROM.begin(EEPROM_SIZE);
  
    if(connectionSetup) {
        pinMode(SETUPINDICATORPIN,OUTPUT);
        digitalWrite(SETUPINDICATORPIN,HIGH);
        BluetoothSerial SerialBT;
      
        if(SerialBT.begin("ESP32")){
        
            while(connectionSetup) {
                if(SerialBT.available()) {
                    const int initializationVectorLengthBytes = 16;
                    const int outputMessageLengthBytes = 128;
                    const int secretKeyBitWidth = 256;
                    
                    unsigned char * msg;
                    msg = (unsigned char *)(SerialBT.readString()+ '\0').c_str();
                    mbedtls_aes_context aes;
                 
                    unsigned char iv[initializationVectorLengthBytes] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
                
                    unsigned char output[outputMessageLengthBytes] = {'\0'};
                
                    mbedtls_aes_setkey_dec(&aes,(const unsigned char *)SECRETKEY, secretKeyBitWidth);
               
                    if(!mbedtls_aes_crypt_cbc( &aes, MBEDTLS_AES_DECRYPT, strlen((const char*)msg), iv, msg, output )) {
                        String info = (String)(char *)(output);
                        int i = 0;
                        //Serial.println(info);
                        for(auto c : info) {
                          EEPROM.write(i, (char)c);
                          i++;
                        }
                        flashWriteSize = i;
                        EEPROM.commit();
                        connectionSetup = 0;
                        SerialBT.disconnect();
                        digitalWrite(SETUPINDICATORPIN,LOW);
                    }
                delay(10);
            
            
          }
          
        }
      
      }
         
    }
    //Read from flash memory user space
    String fromMemory = "";
    for(int j = 0; j < flashWriteSize; j++) {
      fromMemory += (char)(EEPROM.read(j));
    }

    //Assign network settings
    WifiName = GreenthumbIoTLibrary::getValue(fromMemory,' ', 0);
    Password = GreenthumbIoTLibrary::getValue(fromMemory,' ', 1);
    Host =  GreenthumbIoTLibrary::getValue(fromMemory, ' ', 2);
    Port = (uint16_t)(GreenthumbIoTLibrary::getValue(fromMemory, ' ', 3).toInt());          

    //Get the serial key of the chip and assign it to the global variable
    uint64_t chipid = ESP.getEfuseMac(); // The chip ID is essentially its MAC address(length: 6 bytes).
    uint16_t chip = (uint16_t)(chipid >> 32);
    snprintf(espId, serialKeyLength, "ESP32-%04X%08X", (uint16_t)chip, (uint32_t)chipid);
   
    
    
    //LOAD BME280 settings from GreenthumbIoTConfig.h
    atmosphericSensor.settings.commInterface = BME280COMINTERFACE;
    atmosphericSensor.settings.I2CAddress = BME280I2CADDRESS;
    atmosphericSensor.settings.runMode = BME280RUNMODE; 
    atmosphericSensor.settings.tStandby = BME280TSTANDBY;
    atmosphericSensor.settings.filter = BME280FILTER;
    atmosphericSensor.settings.tempOverSample = BME280TEMPOVERSAMPLE;
    atmosphericSensor.settings.pressOverSample = BME280PRESSOVERSAMPLE;
    atmosphericSensor.settings.humidOverSample = BME280HUMIDOVERSAMPLE; 
    
    //Start atmosphericSensor
    atmosphericSensor.begin();
    delay(10); //BME280 requires 2ms to start up. 

    
    apds.init();
    delay(10);
    apds.enableLightSensor(false);
    
    //Set wifimode from GreenthumbIoTConfig.h, start wifimodule an disconnect all prior connections if the module was already on. 
    WiFi.mode(WIFIMODE);
    WiFi.disconnect();


    //Wifi connection setup from GreenthumbIoTConfig.h
    wifiMulti.addAP(WifiName.c_str(),Password.c_str());

    //Time server setup
    configTime(gmtOffset_sec, daylightOffset_sec, timeServer);
  
}



void loop() {

    //Connect to the access point. Give time for wifi to connnect, double call to make sure wifi is established bcs of known bugs.
    wifiMulti.run();
    if(!WiFi.isConnected()) wifiMulti.run();
          
    //If wifi connection is established try to connect to raspberry's server
    if(WiFi.isConnected()) {
        //Serial.println(WiFi.localIP());
        WiFiClient client;
        if(client.connect(Host.c_str(),Port)){ 
            //Serial.println("Connected to rasp server.");
            //Collect data from sensors
       
            float temp = atmosphericSensor.readTempC();
            float hum = atmosphericSensor.readFloatHumidity();
            int soil = analogRead(soilSensor);
            uint16_t luminosity = 0; 
            apds.readAmbientLight(luminosity);
            
            time_t timetag = time(NULL);
            int i = 0;
            while(timetag < (time_t)10000 && i < 100){
                timetag = time(NULL);
                i++;
            }
            timetag = timetag + GMTOFFSET;
            String message = GreenthumbIoTLibrary::generateMessage(espId, timetag, temp, hum, soil, luminosity);
          
            //Wrap and send data via socket to the server.
            client.print(message);
            delay(100);
            
            //Disconnect from server
            client.stop();

            //Serial.println("Rasp connection loop finished");
        }
        else {
           Serial.println("No connection to rasp server"); 
        }
        
        
    }
    else {
        Serial.println("No wifi connection");
        WiFi.disconnect();
        delay(100);
        esp_sleep_enable_timer_wakeup(retrySleepTime);
        esp_deep_sleep_start();
    }
    
          
    //Set deep sleep time and start sleeping. After waking up setup is run again.
    WiFi.disconnect();
    //Serial.println(millis());
    delay(100);
    esp_sleep_enable_timer_wakeup(sleepTime);
    esp_deep_sleep_start();
}
 
  

  
  
  
