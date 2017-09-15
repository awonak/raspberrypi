import RPi.GPIO as GPIO
import sys
import time

from led import LED
from flow_sensor import FlowSensor


# Constants
SECOND = 1000.0  # in ms

# Use this pin for input
FLOW_SENSOR = 22  # Beer
FLOW_SENSOR2 = 23  # Cider

# Use this pin for LED output
RED = 18


def do_click(pin):
    led.on()
    current_time = int(time.time() * SECOND)
    sensors[pin].update(current_time)

    
def run():
    while True:
        # check if pour is complete
        current_time = int(time.time() * SECOND)
        for fs in sensors.values():
            if (fs.done_pouring(current_time)):
                fs.display()
                fs.reset()

        # done
        led.off()
        time.sleep(0.2)
        

# Define led output
led = LED(RED)

# Define your pin:flow_sensor map
sensors = {
    FLOW_SENSOR: FlowSensor("Beer", FLOW_SENSOR, do_click),
    FLOW_SENSOR2: FlowSensor("Cider", FLOW_SENSOR2, do_click)
}
    
if __name__ == '__main__':
    
    try:
        run()
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.stdout.flush()
        sys.exit()
