import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

delay = 0.1

 # Set pin numbers
inPin = 40
ledPin = 11

# Set pin 40 as input, pin 11 as output
GPIO.setup(inPin, GPIO.IN)
GPIO.setup(ledPin, GPIO.OUT)

# Run until ctrl + C
try:
    while True:

        # Read input from pin 40
        readVal=GPIO.input(inPin)
        print(readVal)

        # if button pushed down, LED will turn on
        if readVal == 0:
            GPIO.output(ledPin, True)
        else:
            GPIO.output(ledPin, False)
        sleepd(delay)
except KeyboardInterrupt:
    GPIO.cleanup()
    print()