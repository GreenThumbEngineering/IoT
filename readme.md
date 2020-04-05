### ESP32

ESP32 directory contains codes for different boards and their setups, since different libraries have to be included. This can be done in more elegant fashion in the later versions. Directories inside the initial ESP32-directory are for different temp/hum sensors indicated in the name of the directory. For now, both of them contain the same headerfiles for settings when using different types of boards.

----


### Raspberrypi

Raspberrypi directory contains current services running on Raspberrypi and their systemd setupfiles. Their targets/wants are not listed yet, which have to be taken into account for the setup to work properly. Raspberrypi also contains the code snippet for taking pictures with raspberrypi camera module. Bluetooth-serialkey service extends pyBluez's examples. 

----

### BluetoothApp

Plain app for configuring networking on Raspberrypi. 
----