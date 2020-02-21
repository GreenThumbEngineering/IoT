from picamera import PiCamera,Color
from time import sleep
import sys
import pytz
from datetime import datetime
def main():
    rg, bg = (5.0,5.0)
    outName = ""
    try:
        rg = float(sys.argv[1])
        bg = float(sys.argv[2])
    except:
        rg = 0
        bg = 0
    try:
        outName = sys.argv[3]
    except:
        outName = "unknown"
    print("AWB values: " + "RG " + str(rg) + ", BG " + str(bg)) 
    camera = PiCamera()
    camera.resolution = (1280, 720)
    camera.awb_mode='off'
    camera.awb_gains = (rg, bg)
    sleep(5)
    timezone = pytz.timezone('Europe/Helsinki')
    time = datetime.now(timezone).strftime("%m-%d-%y_%H-%M")
    camera.capture('/home/pi/Desktop/'+ outName + '.jpg')

main()
