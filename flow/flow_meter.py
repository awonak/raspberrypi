"""Library code for reading Liquid Flow Meter input

Provides functionality for interfacing with the sensor input. Also provides
methods for measuring an individual flow event (defined by min flow volume and
duration after last pulse) as well as total flow volume for this instance. All
volume is measured in liters.

Flow rate pulse characteristics: Frequency (Hz) = 7.5 * Flow rate (L/min)
Pulses per Liter: 450

https://www.adafruit.com/product/828

Example usage:

import time
import signal

from flow_sensor import FlowMeter

# Define a callback function for handling pulses
def flow_start(pin):
    current_time = int(time.time() * 1000)
    print "Flow started at %s" % current_time

# Define a callback function for handling flow stop
def flow_stop(pin):
    current_time = int(time.time() * 1000)
    print "Flow stopped at %s" % current_time
    print sensor.display()

# Create an instance of a flow meter and run it
sensor = FlowMeter("Beer", 22)
sensor.flow_start = flow_start
sensor.flow_stop = flow_stop

# sleep until a signal is received
signal.pause()

"""
import logging
import time

import RPi.GPIO as GPIO
from gpiozero.threads import GPIOThread

DEBUG = False
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(level=LOG_LEVEL,
                    format='(%(threadName)-10s) %(message)s')

# Constants
MINUTE = 60  # seconds per minute
FLOW_FREQ = 7.5  # Flow rate frequency

GPIO.setmode(GPIO.BCM)


class FlowMeter(GPIOThread):
    """An instance of the Flow Meter sensor input and output.

    FlowMeter callback methods
    flow_start: The code to be executed when flow starts.
    flow_stop: The code to be executed when flow stops.
    flow_pulse: The code to be executed with each pulse input.

    Args:
        name (str): The name of the FlowMeter.
        pin (int): The BCM pin number for this sensor.
        
    Attributes:
        last_time (int): A timestamp in miliseconds of the last click event.
        amount (float): The volume in liters since flow_start event.
        pulses (int): The count of each input pulse received from the sensor.
        total_flow (float): The total volume in liters of all measured flow.
        name (str): The human readable string identifieir for this instance.
        pin (int): The GPIO pin number used with this sensor instance.

    """

    FINISHED_DELAY = 2 * 1000  # 2 seconds in miliseconds
    MIN_AMOUNT = 0.1 #0.23  # Minimum flow volume check (~8oz)

    active = False
    amount = 0.0
    last_time = 0
    pulses = 0
    total_amount = 0.0

    def __init__(self, name, pin):
        # initialize threading
        super(FlowMeter, self).__init__()

        # set instance variabes
        self.name = name
        self.pin = pin

        # Default callback methods
        self.flow_start = lambda pin: None
        self.flow_stop = lambda pin: None
        self.flow_pulse = lambda pin: None

        # configure GPIO for this sensor
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.update,
                              bouncetime=20)

        # Start thread
        self.start()

    def _check_for_start(self):
        """Determine if the sensor was not previously active"""
        return not self.active

    def _check_for_stop(self):
        """Determine if all conditions have satisfied a stop flow event"""
        current_time = self.time_in_ms()
        min_duration_met = self.amount > self.MIN_AMOUNT
        min_volume_met = (current_time - self.last_time) > self.FINISHED_DELAY
        return min_duration_met and min_volume_met

    @staticmethod
    def time_in_ms():
        """Returns current timestamp in miliseconds"""
        return int(time.time() * 1000)

    # override threading.run
    def run(self):
        """The flow meter logic while listening for input"""
        logging.debug('starting name: %s on pin: %s', self.name, self.pin)
        while True:
            if self._check_for_stop():
                logging.info('Flow stopped...')
                self.total_amount += self.amount
                self.flow_stop(self.pin)
                self.reset()
            time.sleep(0.1)

    def display(self):
        """Return current amount and total amount stats"""
        msg = "{name}\nCurrent flow: {amount}\nTotal flow: {total_amount}\n".format(
            name=self.name, amount=self.amount, total_amount=self.total_amount)
        logging.info(msg)
        return msg

    def reset(self):
        """Resets instance variables used to measure current flow amount"""
        self.pulses = 0
        self.amount = 0.0
        self.active = False

    def update(self, _):
        """Handle a pulse event and update current volume amount"""
        if self._check_for_start():
            logging.info('Flow started...')
            self.active = True
            self.flow_start(self.pin)

        # count flow meter pulses
        self.pulses += 1

        # if a plastic sensor use the following calculation
        # Sensor Frequency (Hz) = 7.5 * Q (Liters/min)
        # Liters = Q * time elapsed (seconds) / 60 (seconds/minute)
        # Liters = (Frequency (Pulses/second) / 7.5) * time elapsed (seconds) / 60
        # Liters = Pulses / (7.5 * 60)
        self.amount = self.pulses / (FLOW_FREQ * MINUTE)

        # set last_time for next iteration
        self.last_time = self.time_in_ms()

        # call pulse event callback
        self.flow_pulse(self.pin)
        logging.debug("Flow pulse amount: %s  pulses: %s", self.amount, self.pulses)
