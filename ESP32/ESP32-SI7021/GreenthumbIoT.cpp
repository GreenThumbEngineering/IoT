#include "GreenthumbIoT.h"

String GreenthumbIoTLibrary::getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}


String GreenthumbIoTLibrary::generateMessage(const char *espId, time_t timetag, float temp, float hum, int soil, uint16_t luminosity) {
        return "<Object>\n\t<DeviceId>"+String(espId)+"</DeviceId>\n\t<MeasurementTime>"+ (String)timetag + "</MeasurementTime><Temperature>" + (String)temp + "</Temperature>\n\t<Humidity>" + String(hum) + "</Humidity>\n\t<SoilMoisture>+" + (String)soil + "</SoilMoisture>\n\t<Luminosity>" + (String)luminosity + "</Luminosity>\n</Object>";
}
