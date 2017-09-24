"""Library code for reading Liquid Flow Meter input

Provides functionality for interfacing with the sensor input. Also provides
methods for measuring an individual pour (defined by min pour volume and
duration after last pulse) as well as total pour volume for this instance. All
volume is measured in liters.

Flow rate pulse characteristics: Frequency (Hz) = 7.5 * Flow rate (L/min)
Pulses per Liter: 450

https://www.adafruit.com/product/828

Example usage:

    # Import the flow sensor library
    from flow_sensor import FlowSensor

    # Define a callback function for handling pulses
    def pour_event(pin):
        current_time = int(time.time() * 1000)
        sensor.update(current_time)

    # Define a callback function for handling pour complete
    def pour_complete(pin):
        print sensor.display()

    # Create an instance of a flow meter and run it
    sensor = FlowSensor("Beer", 22, pour_event, pour_complete)
    sensor.start()

"""
import logging
import time
import threading

import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s')
# Constants
FINISHED_DELAY = 2 * 1000  # 2 seconds in miliseconds
MINUTE = 60  # seconds per minute
MIN_POUR = 0.1 #0.23  # Minimum pour volume check (~8oz)
FLOW_FREQ = 7.5  # Flow rate frequency

GPIO.setmode(GPIO.BCM)


class FlowSensor(threading.Thread):
    """An instance of the Flow Meter sensor input and output

    Args:
        name (str): The name of the FlowSensor.
        pin (int): The BCM pin number for this sensor.
        pour_event (function): The code to be executed with each pulse input.
        pour_complete (function): The code to be executed when pour complete.

    Attributes:
        last_time (int): A timestamp in miliseconds of the last click event.
        pour (float): The volume in liters of the current measured pour.
        pulses (int): The count of each input pulse received from the sensor.
        total_pour (float): The total volume in liters of all measured pours.
        name (str): The human readable string identifieir for this instance.
        pin (int): The GPIO pin number used with this sensor instance.

    """
    last_time = 0
    pour = 0.0
    pulses = 0
    total_pour = 0.0
    active = False

    def __init__(self, name, pin, pour_event, pour_complete):
        # initialize threading
        threading.Thread.__init__(self)
        self.daemon = True

        # set instance variabes
        self.name = name
        self.pin = pin
        self._pour_complete = pour_complete

        # configure GPIO for this sensor
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=pour_event,
                              bouncetime=20)

    # override threading.run
    def run(self):
        logging.debug('starting name: %s on pin: %s', self.name, self.pin)
        while True:
            current_time = int(time.time() * 1000)
            if self.done_pouring(current_time):
                self._pour_complete(self.pin)
                self.reset()

            time.sleep(0.2)
        logging.debug('exiting name: %s on pin: %s', self.name, self.pin)


    def display(self):
        """Return current pour and total pour stats"""
        msg = "{name}\nThis pour: {pour}\nTotal pour: {total_pour}\n".format(
            name=self.name, pour=self.pour, total_pour=self.total_pour)
        logging.info(msg)
        return msg

    def reset(self):
        """Resets instance variables used to measure current pour"""
        self.pulses = 0
        self.pour = 0.0
        self.active = False

    def done_pouring(self, current_time):
        """Determine if all conditions have satisfied a completed pour event"""
        min_pour_duration = self.pour > MIN_POUR
        min_pour_volume = (current_time - self.last_time) > FINISHED_DELAY
        if min_pour_duration and min_pour_volume:
            self.total_pour += self.pour
            return True
        return False

    def _update_status(self):
        if not self.active:
            self.active = True
            return True
        else:
            return False

    def update(self, current_time):
        """Handle a pulse click event and update current pour volume

        Returns: (bool) If this is the begining of a pour event
        """
        # measure flow meter pulses
        self.pulses += 1

        # if a plastic sensor use the following calculation
        # Sensor Frequency (Hz) = 7.5 * Q (Liters/min)
        # Liters = Q * time elapsed (seconds) / 60 (seconds/minute)
        # Liters = (Frequency (Pulses/second) / 7.5) * time elapsed (seconds) / 60
        # Liters = Pulses / (7.5 * 60)
        self.pour = self.pulses / (FLOW_FREQ * MINUTE)

        logging.debug("pour: %s  pulses: %s", self.pour, self.pulses)

        # set last_time for next iteration
        self.last_time = current_time

        return self._update_status()
