import RPi.GPIO as GPIO
import alsaaudio as aa
import numpy as np

PIN_ORDER = [19, 18, 16, 15, 13, 12, 11, 10, 8, 7, 5, 3]
NUM_LEDS = len(PIN_ORDER)
SAMPLE = 2048
RATE = 44100
MIN_FREQUENCY = 20
MAX_FREQUENCY = 16000

def initializeGPIO():
    #Initialize GPIO settings
    GPIO.setwarnings(FALSE)
    GPIO.setmode(GPIO.BOARD)
    for pins in PIN_ORDER:
        GPIO.setup(pins, GPIO.OUT)

def closeGPIO():
    #Turns off all LEDs to end program
    for pins in PIN_ORDER:
           GPIO.output(pins, 0)

def get_levels(raw, limits):
    #Convert raw data to integers and filter the signal
    data = np.fromstring(raw, dtype='int16')
    window = np.hanning(len(data))
    data = data*window

    #Convert the signal to the frequency domain using numpy's
    #   discrete, real, fast fourier transform
    fourier = np.fft.rfft(data)
    fourier.np.delete(fourier, len(fourier)-1)

    #Calculate the power distribution and average power
    power = np.abs(fourier)**2
    avg_power = np.average(power)

    #Set LED multiplier based on power of signal.
    #   These numbers were experimentally decided and
    #   are for the headphone jack of an iPhone 5S
    #   with the signal split. If in doubt, set mult=1.
    #More work should be done to calculate this numbers to
    #   reflect other devices or direct input (not split)
    #The multiplier makes it so a softer sound will have
    #   less LEDs on, while a louder sound will have more.
    #   the logarithmic nature of loudness can be seen in
    #   the chosen multiplier threshholds.
    mult = 1.3
    if(avg_power > 999999999*10):
        mult = 1.2
    if(avg_power > 999999999*80):
        mult = 1.1
    if(avg_power > 999999999*800):
        mult = 1
    if(avg_power > 999999999*10000):
        mult = 0.9
    leds = []

    #If the signal is loud enough, turn on some LEDs
    if(avg_power > 999999999*5):
        #Calculate frequency limit indices for the power array
        index = []
        for i in range(0,NUM_LEDS):
            index.append(int(SAMPLE*limits[i]/RATE))
        index.append(len(power))
   
        #Calculate the average power of each frequency range
        led_power = []
        for i in range(0, NUM_LEDS):
            led_power.append(np.log10(np.sum(power[index[i]:index[i+1]])))

        #Get the maximum average power of a frequency range for
        #   it to be On. It is based on the average of all the
        #   frequency range averages and the total average power.
        max = np.average(led_power)*mult

        #Set LEDs with a frequency range with a large enough average
        #   power to On and the others to Off
        for i in range(0, NUM_LEDS):
            if(led_power[i] > max):
                leds.append(1)
            else:
                leds.append(0)
    #If the signal is not loud enough, set each LED to off
    else:
        for i in range(0, NUM_LEDS):
            leds.append(0)

    #Return the array with the LEDs states (On or Off)
    return leds

def main():
    #Initialize GPIO settings
    initializeGPIO()

    #Initialize ALSA audio input
    input = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, 'default')
    input.setperiodsize(SAMPLE)

    #Initialize frequency limits
    multiplier = (MAX_FREQUENCY/MIN_FREQUENCY)**(1.0/NUM_LEDS)
    frequency_limits = [MIN_FREQUENCY]
    for i in range(0, NUM_LEDS):
        frequency_limits.append(frequency_limits[i]*multiplier)

    #Until broken by keyboard interrupt or power loss, process incoming
    #   sound and adjust LEDs
    try:
        while True:
            #Get audio input
            l, raw = input.read()

            #Get array of LED states
            levels = get_levels(raw, frequency_limits)

            #Set LEDs to On or Off
            for i in range(0, NUM_LEDS):
                GPIO.output(PIN_ORDER[i], levels[i])
    except KeyboardInterrupt:
        pass

    #If broken by keyboard interrupt, turn of LEDs before ending program
    closeGPIO()

if __name__ == "__main__": main()
