import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

 # Set pin number
inPin = 40

# Set pin 40 as input
GPIO.setup(inPin, GPIO.IN)

# Run until ctrl + C
try:
    while True:

        # Read input from pin 40
        readVal=GPIO.input(inPin)
        print(readVal)
        sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print()