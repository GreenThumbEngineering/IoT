#ifndef GREENTHUMBIOT_H_
#define GREENTHUMBIOT_H_

#include "Arduino.h"
#include <stdint.h>
#include "time.h"
namespace GreenthumbIoTLibrary {
	
	//Split and the value at the specified index
	String getValue(String data, char separator, int index);


    //Generates communcation format string from the given input.
    String generateMessage(const char *espId, time_t timetag, float temp, float hum, int soil, uint16_t luminosity);
}


#endif
