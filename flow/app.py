import atexit
import time

import RPi.GPIO as GPIO
from flask import Flask
app = Flask(__name__)

from flow_sensor import FlowSensor
FLOW_SENSOR1 = 22
FLOW_SENSOR2 = 23

# Define a callback function for handling pulses
def do_click(pin):
    sensor = SENSORS[pin]
    current_time = int(time.time() * 1000)
    begin = sensor.update(current_time)

    if begin:
        print "Begin Pour of {}".format(sensor.name)


# Define your pin:flow_sensor map
SENSORS = {
    FLOW_SENSOR1: FlowSensor("Beer", FLOW_SENSOR1, do_click),
    FLOW_SENSOR2: FlowSensor("Cider", FLOW_SENSOR2, do_click)
}

[s.start() for s in SENSORS.values()]



@app.route("/")
def hello():
    return "Hello world"

@atexit.register
def cleanup():
    print "Sensor cleanup..."
    GPIO.cleanup()
 
