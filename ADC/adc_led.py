import RPi.GPIO as GPIO
import ADC0834
from time import sleep

# Set GPIO board
GPIO.setmode(GPIO.BCM)

# Initiate library for ADC0834
ADC0834.setup()

# Set up variables
ledPin = 16
delay = 0.2
freq = 100

# Set up output
GPIO.setup(ledPin, GPIO.OUT)

# Set up PWM
myPWM = GPIO.PWM(ledPin, freq) # (pin, freq)
myPWM.start(0)


try:
    while True:
        analogVal = ADC0834.getResult(0) # Get from Channel 0
        analogVal_percent = (analogVal / 255) * 100
        print(f"Analog Value: {analogVal} and Brightness: {analogVal_percent:.2f}%")
        myPWM.ChangeDutyCycle(analogVal_percent)
        sleep(delay)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print()