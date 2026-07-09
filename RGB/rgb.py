import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

# Save pins to variables
rPin = 37
gPin = 35
bPin = 33

# Setup GPIO pins
GPIO.setup(rPin, GPIO.OUT)
GPIO.setup(gPin, GPIO.OUT)
GPIO.setup(bPin, GPIO.OUT)

# Output color
try:
    while True:
        GPIO.output(gPin, 1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print()