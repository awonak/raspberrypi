"""Fake testing sensors app for detecting sound events.
"""
import datetime
import logging
import time

LOG_LEVEL = logging.INFO

ALERTS = []

logging.basicConfig(level=LOG_LEVEL,
                    format='(%(threadName)-10s) %(message)s')


def add_alert(_):
    """Add the current timestamp to the list of alerts."""
    ALERTS.append(datetime.datetime.now())


def get_alerts():
    """Return the list of alerts."""
    return ALERTS


def start():
    """Initialize sensors and start app."""
    logging.info('Begin..')
    for _ in range(3):
        add_alert(None)
        time.sleep(2)
