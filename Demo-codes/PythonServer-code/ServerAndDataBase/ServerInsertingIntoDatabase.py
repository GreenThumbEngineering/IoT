'''
Created on 31.10.2019

@author: Lauri
'''

import socket
import sqlite3
import xml.etree.ElementTree as ET
import pyodbc 


server = 'tcp:fruttidiaaltotest.database.windows.net' 
database = 'SensorData' 
username = 'Almighty' 
password = 'fruttidiaalto1234!' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
azureCursor = cnxn.cursor()
string = """
IF OBJECT_ID('dbo.SensorData', 'U') IS NULL 
    CREATE TABLE SensorData(
        ID VARCHAR(255) NOT NULL,
        Time VARCHAR(255) NOT NULL PRIMARY KEY,
        Plant VARCHAR(255),\n  Temperature float,
        Humidity float,
        Pressure float,
        Soil float,
        ColorTemp Integer,
        Lux Integer,
        RGB VARCHAR(255)
        )

"""
azureCursor.execute(string)
cnxn.execute('commit')


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

''' ServerCode '''
s = socket.socket()
s.bind(('0.0.0.0', 4420))
s.listen(0)

'''Loop'''
while True:
    
    client, addr = s.accept()
    data = ''
    while(not "</Object>" in data): 
            content = client.recv(1024)
            for char in content:
                data += chr(char)
            
            
    print(data)
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
    
    insertion = "INSERT INTO SensorData(ID,Time,Plant,Temperature,Humidity, Pressure,Soil,ColorTemp, Lux, RGB) VALUES(?,?,?,?,?,?,?,?,?,?)"
    cursor.execute(insertion,(TelemetryDict["ID"],TelemetryDict["Timetag"],TelemetryDict["Plant"],TelemetryDict["Temperature"],TelemetryDict["Humidity"],TelemetryDict["Pressure"],TelemetryDict["Soil"],TelemetryDict["ColorTemp"],TelemetryDict["Lux"],TelemetryDict["RGB"]))            
    azureCursor.execute(insertion,TelemetryDict["ID"],TelemetryDict["Timetag"],TelemetryDict["Plant"],TelemetryDict["Temperature"],TelemetryDict["Humidity"],TelemetryDict["Pressure"],TelemetryDict["Soil"],TelemetryDict["ColorTemp"],TelemetryDict["Lux"],TelemetryDict["RGB"])
    cnxn.commit()
    db.commit()            
                