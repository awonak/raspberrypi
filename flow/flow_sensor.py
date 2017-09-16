"""Library code for reading Liquid Flow Meter input

Provides functionality for interfacing with the sensor input. Also provides
methods for measuring an individual pour (defined by min pour volume and
duration after last pulse) as well as total pour volume for this instance. All
volume is measured in liters.

Flow rate pulse characteristics: Frequency (Hz) = 7.5 * Flow rate (L/min)
Pulses per Liter: 450

https://www.adafruit.com/product/828

"""
import RPi.GPIO as GPIO

# Constants
DEBUG = False
FINISHED_DELAY = 2 * 1000  # 2 seconds in miliseconds
MINUTE = 60  # seconds per minute
MIN_POUR = 0.23  # Minimum pour volume check (~8oz)
VOLUME_PER_PULSE = 7.5  # Volume per pulse

GPIO.setmode(GPIO.BCM)


class FlowSensor(object):
    """An instance of the Flow Meter sensor input and output

    Args:
        name (str): The name of the FlowSensor.
        pin (int): The BCM pin number for this sensor.
        callback (function): The code to be executed with each pulse input.

    Attributes:
        pulses (int): The count of each input pulse received from the sensor.
        last_time (int): A timestamp in miliseconds of the last click event.
        pour (float): The volume in liters of the current measured pour.
        total_pour (float): The total volume in liters of all measured pours.
        name (str): The human readable string identifieir for this instance.

    """
    last_time = 0
    pour = 0.0
    pulses = 0
    total_pour = 0.0

    def __init__(self, name, pin, callback):
        # set instance variabes
        self.name = name
        self.pin = pin

        # configure GPIO for this sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=20)

    def display(self):
        """Print current pour and total pour stats"""
        print "%s\nThis pour: %s\nTotal pour: %s\n" % (
            self.name, self.pour, self.total_pour)

    def reset(self):
        """Resets instance variables used to measure current pour"""
        self.pulses = 0
        self.pour = 0.0

    def done_pouring(self, current_time):
        """Determine if all conditions have satisfied a completed pour event"""
        pour_duration = self.pour > MIN_POUR
        pour_volume = (current_time - self.last_time) > FINISHED_DELAY
        if pour_duration and pour_volume:
            self.total_pour += self.pour
            return True
        return False

    def update(self, current_time):
        """Handle a pulse click event and update current pour volume"""
        # measure flow meter pulses
        self.pulses += 1

        # if a plastic sensor use the following calculation
        # Sensor Frequency (Hz) = 7.5 * Q (Liters/min)
        # Liters = Q * time elapsed (seconds) / 60 (seconds/minute)
        # Liters = (Frequency (Pulses/second) / 7.5) * time elapsed (seconds) / 60
        # Liters = Pulses / (7.5 * 60)
        self.pour = self.pulses / (VOLUME_PER_PULSE * MINUTE)

        if DEBUG:
            print "%s = %s / %s * %s" % (self.pour, self.pulses, VOLUME_PER_PULSE, MINUTE)

        # set last_time for next iteration
        self.last_time = current_time
