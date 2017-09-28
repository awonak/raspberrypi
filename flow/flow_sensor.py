"""Library code for reading Liquid Flow Meter input

Provides functionality for interfacing with the sensor input. Also provides
methods for measuring an individual flow event (defined by min flow volume and
duration after last pulse) as well as total flow volume for this instance. All
volume is measured in liters.

Flow rate pulse characteristics: Frequency (Hz) = 7.5 * Flow rate (L/min)
Pulses per Liter: 450

https://www.adafruit.com/product/828

Example usage:

    # Import the flow sensor library
    from flow_sensor import FlowMeter
    import time

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
    sensor = FlowMeter("Beer", 22, flow_start, flow_stop)
    sensor.start()

"""
import logging
import time
import threading

import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s')
# Constants
MINUTE = 60  # seconds per minute
FLOW_FREQ = 7.5  # Flow rate frequency

GPIO.setmode(GPIO.BCM)


class FlowMeter(threading.Thread):
    """An instance of the Flow Meter sensor input and output

    Args:
        name (str): The name of the FlowMeter.
        pin (int): The BCM pin number for this sensor.
        flow_start (function): The code to be executed when flow starts.
        flow_stop (function): The code to be executed when flow stops.
        flow_pulse (function): The code to be executed with each pulse input.

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

    def __init__(self, name, pin, flow_start=None, flow_stop=None,
                 flow_pulse=None):
        # initialize threading
        threading.Thread.__init__(self)
        self.daemon = True

        # set instance variabes
        self.name = name
        self.pin = pin
        self._start = flow_start or lambda pin: None
        self._stop = flow_stop or lambda pin: None
        self._pulse = flow_pulse or lambda pin: None

        # configure GPIO for this sensor
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.update,
                              bouncetime=20)

    def _check_for_start(self):
        if not self.active:
            logging.info('Flow started...')
            self.active = True
            self._start(self.pin)

    def _check_for_stop(self):
        """Determine if all conditions have satisfied a stop flow event"""
        current_time = self.time_in_ms()
        min_duration_met = self.amount > self.MIN_AMOUNT
        min_volume_met = (current_time - self.last_time) > self.FINISHED_DELAY
        return min_duration_met and min_volume_met

    @staticmethod
    def time_in_ms():
        return int(time.time() * 1000)

    # override threading.run
    def run(self):
        """The flow meter logic while listening for input"""
        logging.debug('starting name: %s on pin: %s', self.name, self.pin)
        while True:
            if self._check_for_stop():
                logging.info('Flow stopped...')
                self.total_amount += self.amount
                self._stop(self.pin)
                self.reset()
            time.sleep(0.1)
        logging.debug('exiting name: %s on pin: %s', self.name, self.pin)

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
        self._check_for_start()

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
        self._pulse(self.pin)
        logging.debug("Flow pulse amount: %s  pulses: %s", self.amount, self.pulses)
