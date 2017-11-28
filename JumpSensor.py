import serial
import time
import keyboard

com = serial.Serial("COM6")
press_sleep = 0.1

while True:
    dist = com.readline()
    print dist

    print "pressed space"
    keyboard.press("space")
    t = time.time()
    while time.time() > t + press_sleep:
        dist = com.readline()
    print "unpressed space"
    keyboard.release("space")