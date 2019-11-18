'''
Created on 31.10.2019
@author: Lauri
'''

import socket
import sqlite3
import xml.etree.ElementTree as ET
import threading

#Locking access to sensorDict to one thread at a time
sensorLock = threading.Lock()

SensorDict = {
    
}
db = sqlite3.connect('sensorData.db')
cursor = db.cursor()
cursor.executescript("""
CREATE TABLE IF NOT EXISTS SensorData(
    ID String NOT NULL,
    Time String NOT NULL,
    Plant String,
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
    while(not "</Object>" in data): 
            content = client.recv(1024)
            for char in content:
                data += chr(char)
            
            
    #print(data)
    xml = ET.fromstring(data)
    TelemetryDict = {
        "ID": '',
        "Timetag":'',
        "Plant": '',
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
    SensorDict[TelemetryDict["ID"]] = TelemetryDict;
    insertion = "INSERT INTO SensorData(ID,Time,Plant,Temperature,Humidity, Pressure,Soil,ColorTemp, Lux, RGB) VALUES(?,?,?,?,?,?,?,?,?,?)"
    cursor.execute(insertion,(TelemetryDict["ID"],TelemetryDict["Timetag"],TelemetryDict["Plant"],TelemetryDict["Temperature"],TelemetryDict["Humidity"],TelemetryDict["Pressure"],TelemetryDict["Soil"],TelemetryDict["ColorTemp"],TelemetryDict["Lux"],TelemetryDict["RGB"]))            
    db.commit()
    sensorLock.release()
    
''' ServerCode '''
s = socket.socket()
s.bind(('0.0.0.0', 4420))
s.listen(0)

'''Loop'''
while True:
    
    client, addr = s.accept()
    threading.Thread(target = handleData(client)).start()
    print(SensorDict)
