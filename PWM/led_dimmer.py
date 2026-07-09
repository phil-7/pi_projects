import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

# Set variables
decimation = (1/8) * 100
delay = 0.15
duty_cycle = 0

# Set pin numbers
ledPin = 37
upPin = 32
downPin = 36

# Setup inputs and outputs, include internal pull up resistor
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(upPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(downPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup PWM, if you want to change frequency in logic, use myPWM.ChangeFrequency(freq) 
myPWM = GPIO.PWM(ledPin, 100) # Pin 37, 100Hz freq
myPWM.start(duty_cycle) # starts with duty cycle of 0

# Logic for adjusting LED brightness
try:
    while True:
        upVal = GPIO.input(upPin)
        downVal = GPIO.input(downPin)

        if upVal == 0 and duty_cycle < 100:
            duty_cycle = duty_cycle + decimation
            myPWM.ChangeDutyCycle(duty_cycle)
            print(f"Brightness: {duty_cycle}%")

        elif downVal == 0 and duty_cycle > 0:
            duty_cycle = duty_cycle - decimation
            myPWM.ChangeDutyCycle(duty_cycle)
            print(f"Brightness: {duty_cycle}%")
        
        sleep(delay)

except KeyboardInterrupt:
    myPWM.stop()
    GPIO.cleanup()
    print()
