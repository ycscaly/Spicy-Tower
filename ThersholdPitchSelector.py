import keyboard
import time

import pyaudio
import sys
import numpy as np
import aubio

left_pressed = False
right_pressed = False
LEFT_KEY = "a"
RIGHT_KEY = "d"

def avg(l):
    return reduce(lambda x, y: x + y, l) / len(l)

def round(num, by):
    return (num if(num % by == 0) else (num - (num % by)))


def unpress():
    global right_pressed
    global left_pressed

    if left_pressed:
        print LEFT_KEY + " unpressed"
        keyboard.release(LEFT_KEY)
        left_pressed = False
    if right_pressed:
        print RIGHT_KEY + " unpressed"
        keyboard.release(RIGHT_KEY)
        right_pressed = False
def press(key):
    global right_pressed
    global left_pressed

    if key == RIGHT_KEY:
        if not right_pressed:
            if left_pressed:
                print LEFT_KEY + " unpressed"
                keyboard.release(LEFT_KEY)
                left_pressed = False
            print RIGHT_KEY + " pressed"
            keyboard.press(RIGHT_KEY)
            right_pressed = True
    if key == LEFT_KEY:
        if not left_pressed:
            if right_pressed:
                print RIGHT_KEY + " unpressed"
                keyboard.release(RIGHT_KEY)
                right_pressed = False
            print LEFT_KEY + " pressed"
            keyboard.press(LEFT_KEY)
            left_pressed = True

# initialise pyaudio
p = pyaudio.PyAudio()

# open stream
buffer_size = 1024
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio.paFloat32,
    channels=1, rate=44100, input=True,
    frames_per_buffer=1024)

# Aubio's pitch detection.
pDetection = aubio.pitch("default", 2048,
    2048//2, 44100)
# Set unit.
pDetection.set_unit("Hz")
pDetection.set_silence(-50)

outputsink = None
record_duration = None

press_interval = 0.1
record_interval = 0.2
total_time = 1200
stime = time.time()
right_threshold = 350
volume_threshold = 0.1
sleep_between_rounds = 0.01
pitch = None

print "Starting"
while True:
    try:
        pitches = []
        t = time.time()

        while( time.time() <  t + record_interval):
            
            audiobuffer = stream.read(buffer_size)

            signal = np.fromstring(audiobuffer, dtype=np.float32)

            data = stream.read(1024)
            samples = np.fromstring(data, dtype=aubio.float_type)
            pitch = round(int(pDetection(samples)[0]), 100)
            
            volume = np.sum(samples**2)/len(samples)
            if(volume > volume_threshold):
                pitches += [pitch]

        if pitches:
            pitch = avg(pitches)
            print pitch
            if pitch > 20:
                if(pitch > right_threshold):
                    press(RIGHT_KEY)
                else:
                    press(LEFT_KEY)
            else:
                unpress()
                pitch = None
        else:
            unpress()
            pitch = None
        
        time.sleep(sleep_between_rounds)

    except KeyboardInterrupt, e:
        print "Stopping"
        break

stream.stop_stream()
stream.close()
p.terminate()
print "Exiting"