"""Raspberry Pi sensors app for detecting sound events.
"""
import atexit
import datetime
import logging
import signal

import RPi.GPIO as GPIO

from led import LED
from sound_sensor import SoundSensor

LOG_LEVEL = logging.INFO

ALERTS = []

GPIO.setmode(GPIO.BCM)

logging.basicConfig(level=LOG_LEVEL,
                    format='(%(threadName)-10s) %(message)s')


def add_alert(_):
    """Add the current timestamp to the list of alerts."""
    ALERTS.append(datetime.datetime.now())


@atexit.register
def cleanup():
    """Reset the active gpio signals."""
    GPIO.cleanup()
    logging.info('Sensor cleanup...')


def start():
    """Initialize sensors and start app."""
    sound = SoundSensor(4)
    sound.detect = add_alert
    green = LED(21)

    logging.info('Begin..')
    green.on()


if __name__ == '__main__':
    start()
    signal.pause()
