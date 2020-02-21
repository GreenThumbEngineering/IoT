import socket
import bluetooth
import time
import os
import subprocess
from Crypto.Cipher import AES

def returnInfo():
    file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "r")
    ssid = ""
    passwd = ""
    ip = ""
    port = 4420

    for line in file:
        if 'ssid' in line:
           ssid = line.strip().replace('ssid=', '').replace('\"', "")
        elif 'psk' in line:
           passwd = line.strip().replace('psk=', '').replace('\"', "")
           currentNetwork = os.popen("iwconfig wlan0 \
                                | grep 'ESSID' \
                                | awk '{print $4}' \
                                | awk -F\\\" '{print $2}'").read()
           if ssid in currentNetwork:
              break
    file.close()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    return  str(ssid + " " + passwd + " " + ip + " " + str(port))

secretKey = 'f8f2be4d-a9ae-458f-a4e9-542fbc4a'

def generateHash(string):
    IV = 16*'\x00'
    mode = AES.MODE_CBC
    encryptor = AES.new(secretKey, mode, IV=IV)
    return encryptor.encrypt(string)

while True:
    time.sleep(0.5)
    try:
        nearby_devices = bluetooth.discover_devices()
        for baddr in nearby_devices:
            
            if "ESP32" in str(bluetooth.lookup_name(baddr)):
                port = 1
                bSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

                try:
                    bSocket.connect((baddr, port))
                    inputString = returnInfo();
                    print(inputString)
                    add = 16 - len(inputString) % 16
                    out = inputString + add * ' ';
                    bSocket.sendall(generateHash((out).encode("ASCII")))
                    bSocket.close()
                    
                except Exception as e:
                    bSocket.close();
                    print(e)
    except Exception as e:
        print(e)
    
    time.sleep(5)