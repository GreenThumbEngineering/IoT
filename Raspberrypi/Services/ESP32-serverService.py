'''
Created on 31.10.2019
@author: Lauri
'''
import requests
import socket
import sqlite3
import xml.etree.ElementTree as ET
import threading



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




def handleData(client):
    data = ''
    
    while 1: 
           
            try:
                content = client.recv(1024)
                if not content:
                    break
                for char in content:
                    data += chr(char)
               
            except:
                break
    
    if "</Object>" in data:         
        xml = ET.fromstring(data)
        TelemetryDict = {
            "SystemId": serialID,
            "DeviceId": '',
            "MeasurementTime":'',
            "Temperature": '',
            "Humidity":'',
            "SoilMoisture": '',
            "Luminosity": ''
        }
        for table in xml.iter('Object'):
            for child in table:
                if(child.tag in TelemetryDict): 
                    TelemetryDict[child.tag] = child.text

       
        try:

            requests.post("http://greenthumb.cs.aalto.fi/postdata/", data = TelemetryDict)
            client.close()
            print(TelemetryDict['DeviceId'] + " write passed to greenthumb.cs.aalto.fi")
        except:
            print("No connection to greenthumb.cs.aalto.fi")
            client.close()
        
        
        
        
''' ServerCode '''
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind(('0.0.0.0', 4420))
s.listen(10)

'''Server function'''
while True:
    try:
        client, addr = s.accept()
        client.settimeout(10)
        threading.Thread(target = handleData(client)).start()
    except Exception as e:
        print(e)
    
    