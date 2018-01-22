"""Library code for controlling an LED.
"""
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class LED(object):
    """Class for LED functionality.

    Args:
        pin (int): The gpio pin number

    """
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        """Turn the LED on."""
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        """Turn the LED off."""
        GPIO.output(self.pin, GPIO.LOW)
