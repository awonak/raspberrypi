"""App for running this RPi project"""
import sys
import time

import RPi.GPIO as GPIO

from led import LED
from flow_sensor import FlowSensor

# Use this pin for input
FLOW_SENSOR = 22  # Beer
FLOW_SENSOR2 = 23  # Cider

# Use this pin for LED output
RED = 18  # Red LED


def time_in_miliseconds():
    """Get an int timestamp in miliseconds"""
    return int(time.time() * 1000)


def do_click(pin):
    """Sensor event callback"""
    RED_LED.on()
    current_time = time_in_miliseconds()
    SENSORS[pin].update(current_time)

   
def run():
    """The main execution loop for this app"""
    while True:
        # check if pour is complete
        current_time = time_in_miliseconds()
        for sensor in SENSORS.values():
            if sensor.done_pouring(current_time):
                sensor.display()
                sensor.reset()

        # done checking
        time.sleep(0.2)
        RED_LED.off()


# Define led output
RED_LED = LED(RED)

# Define your pin:flow_sensor map
SENSORS = {
    FLOW_SENSOR: FlowSensor("Beer", FLOW_SENSOR, do_click),
    FLOW_SENSOR2: FlowSensor("Cider", FLOW_SENSOR2, do_click)
}


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print "Exiting program..."
    finally:
        GPIO.cleanup()
        sys.exit()
