import RPi.GPIO as GPIO
import alsaaudio as aa
import numpy as np

NUM_LEDS = 4
PIN_ORDER = []
sample = 2048
rate = 44100
min_frequency = 20
max_frequency = 20000

def initializeGPIO():
    #Initialize GPIO settings
    GPIO.setmode(GPIO.BOARD)

    #GPIO dedicated pins are 7,11,12,13,15,16,22
    #GPIO optional pins are 3,5,8,10,19,21,23,24,26

    for pins in PIN_ORDER:
        GPIO.setup(pins, GPIO.OUT)

def get_levels(raw, rate, limits):
    #Create Numpy array
    data_string = raw[1]
    data = []
    for char in data_string:
        data.append[float(char)]  #CHANGE T                              O REFLECT TUPLE CORRECTLY

    #Apply hanning window
    window = np.hanning(len(data))
    data = data *window

    #Apply FFT for real data
    fourier = np.fft.rfft(data)

    #Make the same size as sample
    fourier.np.delete(fourier, len(fourier)-1)

    #Make power array
    power = np.abs(fourier)**2
    index = []
    for i in range(0,NUM_LEDS):
        index.append(int(sample*limits[i]/rate))
    index.append(len(power))
   
    #Create LED boolean array
    leds = []
    avg = np.average(power)
    for i in range(0,NUM_LEDS):
        if(np.average(power[index[i]:index[i+1]]) > avg):
            leds[i] = 1
        else:
            leds[i] = 0

    return leds

def main():b
    initializeGPIO()

    #Initialize ALSA audio settings
    input = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, 'default')
    input.setperiodsize(sample)

    #Initialize frequency intervals
    multiplier = 10**np.log10(max_frequency / min_frequency) / NUM_LEDS
    frequency_limits = [20]
    for i in range(0, NUM_LEDS):
        frequency_limits.append(frequency_limits[i]*multiplier)

    try:
        while True:
            #Read audio from microphone
            raw = input.read()
            levels = get_levels(raw, rate, frequency_limits)

            #Adjust LEDS
            for i in leds:
                GPIO.output(PIN_ORDER[i], levels[i])
    except KeyboardInterrupt:
        pass
