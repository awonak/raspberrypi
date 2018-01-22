"""Library code for sound sensor module.

Detect a sound above a threshold set on the device and trigger a callback
function.

http://a.co/9BRmagD

Example usage:

    import signal
    from sound_sensor import SoundSensor

    # Define a callback function
    def add_alert(pin):
        print "Sount detected!"

    # Create and configure an instance of the sound sensor
    sound = SoundSensor(4)
    sound.detect = add_alert

    # Sleep until a signal is received
    signal.pause()

"""
import logging
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(message)s')

GPIO.setmode(GPIO.BCM)


class SoundSensor(object):
    """Sound sensor module collection of common functionality.

    Detect a sound above a threshold set on the device and trigger a callback
    function.

    Args:
        pin (int): The gpio pin number
        debounce (int): delay between readings in ms

    """
    def __init__(self, pin, debounce=1000):
        self.debounce = debounce
        self.pin = pin

        # Callback method to override
        self.detect = lambda pin: None

        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, self._detect,
                              bouncetime=self.debounce)

    def _detect(self, pin):
        logging.info("Event detected!")
        self.detect(pin)
