import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BCM)


class LED(object):

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def blink(self, duration):
        on()
        time.sleep(duration)
        off()
  
    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
  
    def off(self):
        GPIO.output(self.pin, GPIO.LOW)


def alternate(LEDS, count, duration):
    for _ in range(count):
        for led in LEDS:
            led.blink(duration)
