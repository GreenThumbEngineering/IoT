'''
Created on 31.10.2019
@author: Lauri
'''
import requests
import socket
import sqlite3
import xml.etree.ElementTree as ET
import threading

#Locking access to sensorDict to one thread at a time
sensorLock = threading.Lock()

#Dictionary holding the image of plant states
SensorDict = {
    
}

def getSerial():
    serial = ""
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == "Serial":
                serial = line[10:26]
        f.close()
        return serial
    except:
        return "NULL"
serialID = "RASP-"+getSerial()
print(serialID)
#Image of all plant states transferred to XML-format
def sensorDictXMLString():
    system = ET.Element("Batch")
    for key, sensorChip in SensorDict.items():
        sensor = ET.Element("Sensor")
        for sensorName, sensorValue in sensorChip.items():
            innerChild = ET.Element(sensorName)
            innerChild.text = str(sensorValue)
            sensor.append(innerChild)
        sensor.set('id', key)
        system.append(sensor)
    system.set('systemId', serialID)
    return ET.tostring(system)



db = sqlite3.connect('sensorData.db')
cursor = db.cursor()
cursor.executescript("""
CREATE TABLE IF NOT EXISTS SensorData(
    deviceID String NOT NULL,
    Time String NOT NULL,
    Temperature Double,
    Humidity Double,
    Pressure Double,
    Soil Double,
    ColorTemp Integer,
    Lux Integer,
    RGB String,
    PRIMARY KEY(Time)
);
""")
def handleData(client):
    data = ''
    
    while 1: 
           
            try:
                content = client.recv(1024)
                if not content:
                    break
                for char in content:
                    data += chr(char)
                print(data)
            except:
                break
    
    if "</Object>" in data:         
        xml = ET.fromstring(data)
        TelemetryDict = {
            "deviceID": '',
            "Time":'',
            "Temperature": '',
            "Humidity":'',
            "Pressure": '',
            "Soil": '',
            "ColorTemp": '',
            "Lux": '',
            "RGB": ''
        }
        for table in xml.iter('Object'):
            for child in table:
                if(child.tag in TelemetryDict): 
                    TelemetryDict[child.tag] = child.text
        sensorLock.acquire()
        print("Locked")
        SensorDict[TelemetryDict["deviceID"]] = TelemetryDict;
        insertion = "INSERT INTO SensorData(deviceID,Time,Temperature,Humidity, Pressure, Soil, ColorTemp, Lux, RGB) VALUES(?,?,?,?,?,?,?,?,?)"
        cursor.execute(insertion,(TelemetryDict["deviceID"],TelemetryDict["Time"],TelemetryDict["Temperature"],TelemetryDict["Humidity"],TelemetryDict["Pressure"],TelemetryDict["Soil"],TelemetryDict["ColorTemp"],TelemetryDict["Lux"],TelemetryDict["RGB"]))            
        db.commit()
        request ="""
<omiEnvelope xmlns="http://www.opengroup.org/xsd/omi/1.0/" version="1.0" ttl="0">
    <write msgformat="odf">
        <msg>
            <Objects xmlns="http://www.opengroup.org/xsd/odf/1.0/">
                <Object>
                    <id>""" + serialID + """</id>
                        <Object> 
                        <id>""" + TelemetryDict["deviceID"] + """</id>"""
                        
        for key in TelemetryDict.keys():
            request += """
                        <InfoItem name=\""""+ str(key) + """\">
                            <value>""" + str(TelemetryDict[key]) + """</value> 
                        </InfoItem>\n"""
        request += """
                        </Object>
                </Object>
            </Objects>
        </msg>
     </write>
</omiEnvelope>"""
        print(request)
        requests.post("http://82.130.44.157:8080", request)
        sensorLock.release()
        
        print("Released")
        
''' ServerCode '''
s = socket.socket()
s.bind(('0.0.0.0', 4420))
s.listen(10)

'''Loop'''
while True:
    
    client, addr = s.accept()
    client.settimeout(0.1)
    threading.Thread(target = handleData(client)).start()
    
    #print(SensorDict)
