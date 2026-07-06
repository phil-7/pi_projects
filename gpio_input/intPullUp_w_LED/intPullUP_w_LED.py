import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

delay = 0.1

 # Set pin numbers
inPin = 40
ledPin = 11

# Set pin 40 as input and set internal pull up resistor. pin 11 as output
GPIO.setup(inPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ledPin, GPIO.OUT)

# # Run until ctrl + C
# try:
#     while True:

#         # Read input from pin 40
#         readVal=GPIO.input(inPin)
#         print(readVal)

#         # if button pushed down, LED will turn on
#         if readVal == 0:
#             GPIO.output(ledPin, True)
#         else:
#             GPIO.output(ledPin, False)
#         sleep(delay)

# except KeyboardInterrupt:
#     GPIO.cleanup()
#     print()


# # This toggles light switch using a counter
# counter = 0
# try:
#     while True:

#         # Read input from pin 40
#         readVal=GPIO.input(inPin)
#         # print(readVal)

#         # if button pushed down, add 1 to counter
#         if readVal == 0:
#             counter += 1
        
#         if counter % 2 == 0:
#             GPIO.output(ledPin, False)
#         else:
#             GPIO.output(ledPin, True)
        
#         sleep(delay)

# except KeyboardInterrupt:
#     GPIO.cleanup()
#     print()

# OR Use states
LEDstate = 0
buttonState = 1
buttonStateOld = 1

try:
        while True:
            buttonState = GPIO.input(inPin)
            print(buttonState)

            if buttonState == 1 and buttonStateOld == 0:
                LEDstate = not LEDstate
                GPIO.output(ledPin, LEDstate)
            buttonStateOld = buttonState
            
            sleep(delay)

except KeyboardInterrupt:
    GPIO.cleanup()
    print()