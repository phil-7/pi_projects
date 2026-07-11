#!/usr/bin/env python3
#-----------------------------------------------------
#
#  This is a program for all ADC chip. It
# convert analog singnal to digital signal.
#
#  This program is most analog signal modules'
# dependency. Use it like this:
#  `import ADC0834`
#  `sig = ADC0834.getResult (chn)`
#
# *'chn' should be 0,1,2,3 represent for ch0, ch1, ch2, ch3
# on ADC0834

import RPi.GPIO as GPIO
import time

ADC_CS  = 17
ADC_CLK = 18
ADC_DIO = 27

# using default pins for backwards compatibility
def setup(cs=17, clk=18, dio=27):
    global ADC_CS, ADC_CLK, ADC_DIO
    ADC_CS = cs
    ADC_CLK = clk
    ADC_DIO = dio
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ADC_CS, GPIO.OUT)
    GPIO.setup(ADC_CLK, GPIO.OUT)

def destroy():
    GPIO.cleanup()

# using channel = 0 as default for backwards compatibility
def getResult(channel=0):
    sel = (channel >> 1) & 1
    odd = channel & 1

    GPIO.setup(ADC_DIO, GPIO.OUT)
    GPIO.output(ADC_CS, 0)

    # Start bit
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, 1)
    time.sleep(0.000002)
    GPIO.output(ADC_CLK, 1)
    time.sleep(0.000002)

    # Single-ended mode
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, 1)
    time.sleep(0.000002)
    GPIO.output(ADC_CLK, 1)
    time.sleep(0.000002)

    # ODD
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, odd)
    time.sleep(0.000002)
    GPIO.output(ADC_CLK, 1)
    time.sleep(0.000002)

    # Select
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, sel)
    time.sleep(0.000002)
    GPIO.output(ADC_CLK, 1)
    time.sleep(0.000002)

    GPIO.setup(ADC_DIO, GPIO.IN)

    # Mux settle clock
    GPIO.output(ADC_CLK, 0)
    time.sleep(0.000002)
    GPIO.output(ADC_CLK, 1)
    time.sleep(0.000002)

    dat1 = 0
    for i in range(8):
        GPIO.output(ADC_CLK, 0)
        time.sleep(0.000002)
        GPIO.output(ADC_CLK, 1)
        time.sleep(0.000002)
        dat1 = dat1 << 1 | GPIO.input(ADC_DIO)

    # bit0 is already sitting on the line — no clock needed to get it
    dat2 = dat1 & 1
    for i in range(1, 8):
        GPIO.output(ADC_CLK, 0)
        time.sleep(0.000002)
        GPIO.output(ADC_CLK, 1)
        time.sleep(0.000002)
        dat2 = dat2 | (GPIO.input(ADC_DIO) << i)

    GPIO.output(ADC_CS, 1)

    # print(f"dat1={dat1:08b} ({dat1})  dat2={dat2:08b} ({dat2})  match={dat1==dat2}")
    return dat1 if dat1 == dat2 else 0