#ifndef GREENTHUMBIOTCONFIG_H_
#define GREENTHUMBIOTCONFIG_H_




//BLUETOOTH ENCRYPTION KEY
	#define SECRETKEY "f8f2be4d-a9ae-458f-a4e9-542fbc4a"

//FLASH MEMORY BYTES TO ACCESS
    #define EEPROM_SIZE 500
  
//WIFI SETTINGS
    #define WIFIMODE WIFI_STA



//SLEEP SETTINGS
	
	//Sleep time in seconds(default = 1800)
	#define SLEEP 1800
    
    //Connection retry sleep time, if connection failed(default = 60)
    #define RETRYSLEEP 60
    

//TIME SETTINGS
	#define TIMESERVER "time.google.com"
	#define GMTOFFSET 0
	#define DAYLIGHTOFFSET 0
	


//SENSOR SETTINGS

//BME280 settings
 
    /**
        commInterface can be I2C_MODE or SPI_MODE
        specify chipSelectPin using arduino pin names
        specify I2C address.  Can be 0x77(default) or 0x76
    **/
    
    //For I2C, enable the following and disable the SPI section
    
	#define BME280COMINTERFACE I2C_MODE
    #define BME280I2CADDRESS 0x77
    /**
          For SPI enable the following and dissable the I2C section
          atmosphericSensor.settings.commInterface = SPI_MODE;
          atmosphericSensor.settings.chipSelectPin = 10;
    **/

    //OPERATIONAL SETTINGS

    /**
      runMode can be:
      0, Sleep mode
      1 or 2, Forced mode
      3, Normal mode 
    **/
    #define BME280RUNMODE 3 
    /**
        tStandby can be:
        0, 0.5ms
        1, 62.5ms
        2, 125ms
        3, 250ms
        4, 500ms
        5, 1000ms
        6, 10ms
        7, 20ms
    **/
    
    #define BME280TSTANDBY 0
    /**
        filter can be off or number of FIR coefficients to use:
        0, filter off
        1, coefficients = 2
        2, coefficients = 4
        3, coefficients = 8
        4, coefficients = 16
    **/
    #define BME280FILTER 0
    /**
    tempOverSample can be:
    0, skipped
    1 through 5, oversampling *1, *2, *4, *8, *16 respectively
    **/
    
    #define BME280TEMPOVERSAMPLE 1

    /**
        pressOverSample can be:
        0, skipped
        1 through 5, oversampling *1, *2, *4, *8, *16 respectively
    **/
    #define BME280PRESSOVERSAMPLE 1
    /**
        humidOverSample can be:
        0, skipped
        1 through 5, oversampling *1, *2, *4, *8, *16 respectively
    **/
    #define BME280HUMIDOVERSAMPLE 1

//RGBSENSOR SETTINGS



//SOIL SENSOR

	#define SOILSENSORPIN 34

//INDICATOR LED SETTINGS
    #define SETUPINDICATORPIN 14
#endif
