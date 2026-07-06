import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(37. GPIO.OUT)
GPIO.output(37, True)

myPWM = GPIO.PWM(37, 100) # Pin 37, 100Hz freq

myPWM.start(100) # starts with duty cycle of 50
myPWM.stop()

myPWM.ChangeDutyCycle(75) # change duty cycle
myPWM.ChangeFrequency (200) # change freq