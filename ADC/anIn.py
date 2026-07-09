import RPi.GPIO as GPIO
import ADC0834
from time import sleep

# Set GPIO board
GPIO.setmode(GPIO.BCM)

# Initiate library for ADC0834
ADC0834.setup()

delay = 0.2

try:
    while True:
        analogVal = ADC0834.getResult(0) # Get from Channel 0
        print(analogVal)
        sleep(delay)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print()