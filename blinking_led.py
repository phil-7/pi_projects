import RPi.GPIO as GPIO
import time

# Set up board numbering syste
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

cycles = int(input("How many times do you want the LED to blink?: "))

for _ in range(cycles):
    GPIO.output(11, True)
    time.sleep(1)
    GPIO.output(11, False)
    time.sleep(.5)

GPIO.cleanup()