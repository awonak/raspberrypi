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

GPIO.setmode(GPIO.BCM)

LED_PIN = 4
SOUND_SENSOR_PIN = 21

ALERTS = []

logging.basicConfig(level=LOG_LEVEL,
                    format='(%(threadName)-10s) %(message)s')


def add_alert(_):
    """Add the current timestamp to the list of alerts."""
    ALERTS.append(datetime.datetime.now())


def get_alerts():
    """Return the list of alerts."""
    return ALERTS


@atexit.register
def cleanup():
    """Reset the active gpio signals."""
    GPIO.cleanup()
    logging.info('Sensor cleanup...')


def start():
    """Initialize sensors and start app."""
    sound = SoundSensor(SOUND_SENSOR_PIN)
    sound.detect = add_alert
    green = LED(LED_PIN)

    logging.info('Begin..')
    green.on()


if __name__ == '__main__':
    start()
    signal.pause()
