import socket
import bluetooth
import time
import os

import subprocess
from wifi import Cell, Scheme
from Crypto.Cipher import AES



secretKey = 'SECRETKEYDELETED'

   
    
def getCurrentNetwork():
    currentNetwork = os.popen("iwconfig wlan0 \
                                | grep 'ESSID' \
                                | awk '{print $4}' \
                                | awk -F\\\" '{print $2}'").read()
    
    return currentNetwork.replace('\n',"").replace(" ", "")

def getKnownNetworks():
    file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "r")
    networks = []
    line = file.readline()
    while line is not "":
        if "network" in line:
            ssid = ""
            passwd = ""
            while True:
                
                if "ssid" in line:
                    temp = (line.strip().replace('ssid=', ''))
                    ssid = temp[1:][:len(temp)-2]
                   
                elif 'psk' in line:
                    temp = (line.strip().replace('psk=', ''))
                    passwd = temp[1:][:len(temp)-2]
                    break
                elif '}' in line:
                    break
                line = file.readline()
            networks.append(tuple([ssid, passwd]))
            ssid = ""
            passwd = "" 
        line = file.readline()
    file.close()
    return networks

def waitForConnection(initTimeout):
    timeout = initTimeout
    checkNetwork = getCurrentNetwork()
    while not checkNetwork and timeout > 0:
        checkNetwork = getCurrentNetwork()
        timeout -= 1
        time.sleep(1)

def returnInfo():
    file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "r")
    ssid = ""
    passwd = ""
    ip = ""
    port = 4420

    for line in file:
        if 'ssid' in line:
           temp = (line.strip().replace('ssid=', ''))
           ssid = temp[1:][:len(temp)-2]
        elif 'psk' in line:
           temp = (line.strip().replace('psk=', ''))
           passwd = temp[1:][:len(temp)-2]
           currentNetwork = getCurrentNetwork()
           if ssid in currentNetwork:
              break
    file.close()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    return  str(ssid + " " + passwd + " " + ip + " " + str(port))


def generateHash(string):
    IV = 16*'\x00'
    mode = AES.MODE_CBC
    encryptor = AES.new(secretKey, mode, IV=IV)
    return encryptor.encrypt(string)

def connectWifi(ssid, passwd):
    
    file = open ('/etc/wpa_supplicant/wpa_supplicant.conf', 'w')    
    file.write(
'''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FI

network={
        ssid="%s"
        psk="%s"
        key_mgmt=WPA-PSK

}
        ''' % (ssid, passwd))
    file.close()
    res = subprocess.call(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"])
    waitForConnection(10)

def main():
    
        
    while True:
        network = getCurrentNetwork()
        print(network)
        if not network:
            #Bluetooth setup routine via android
            print("In android setup")    
            while not getCurrentNetwork():
                server_sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM )
                server_sock.bind(("",bluetooth.PORT_ANY))
                server_sock.listen(3)
                server_sock.settimeout(10)
                port = server_sock.getsockname()[1]

                uuid = "SECRETDUUID"

                bluetooth.advertise_service(server_sock, "Bluetooth-network-beacon",
                            service_id = uuid,
                            service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],
                            profiles = [ bluetooth.SERIAL_PORT_PROFILE ],
                            )
                
               
                try:
                    client, addr = server_sock.accept()
                    client.settimeout(10)
                    inc = client.recv(1024)
                    credentials = inc.decode("UTF-8").split(" ")
                    print(credentials)
                    client.close()
                    server_sock.close()
                    connectWifi(str(credentials[0]), str(credentials[1]))
                    print(getKnownNetworks())
                except Exception as e:
                    print(e)
        else:    
            subprocess.call(["rfkill","unblock", "bluetooth"])
           
            try:
                nearby_devices = bluetooth.discover_devices(lookup_names = True)
               
                for baddr,name in nearby_devices:
                    print(name)
                    if "ESP32" in name:
                        port = 1
                        bSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

                        try:
                            print('Trying to connect')
                            bSocket.connect((baddr, port))
                            inputString = returnInfo();
                            print(inputString)
                            add = 16 - len(inputString) % 16
                            out = inputString + add * ' ';
                            print(generateHash((out).encode("ASCII")))
                            bSocket.sendall(generateHash((out).encode("ASCII")))
                            bSocket.close()
                            
                        except Exception as e:
                            bSocket.close();
                            print(e)
            except Exception as e:
                print(e)
        
        #subprocess.call(["rfkill","block", "bluetooth"])       
        time.sleep(0.5)
main()
