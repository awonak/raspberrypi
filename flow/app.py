#!/usr/bin/env python

import atexit
import logging
import time

import RPi.GPIO as GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from flow_sensor import FlowSensor

# Constants
DEBUG = False
NAMESPACE = "/test"

# Flow sensor pin number
FLOW_SENSOR1 = 22
FLOW_SENSOR2 = 23

# Flask app config
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s')

def pour_event(pin):
    """Callback function for sensor pulse event"""
    sensor = SENSORS[pin]
    current_time = int(time.time() * 1000)
    begin = sensor.update(current_time)
    socketio.emit("pour_event", {"data": sensor.pour}, namespace=NAMESPACE)

    if begin:
        msg = "Begin Pour of {}".format(sensor.name)
        socketio.emit('my_response', {"data": msg, "count": 0},
                      namespace=NAMESPACE)

def pour_complete(pin):
    """Callback function for pour complete event"""
    sensor = SENSORS[pin]
    socketio.emit('my_response', {"data": sensor.display(), "count": 0},
                  namespace=NAMESPACE)

# Define your pin:flow_sensor map
SENSORS = {
    FLOW_SENSOR1: FlowSensor("Beer", FLOW_SENSOR1, pour_event, pour_complete),
    FLOW_SENSOR2: FlowSensor("Cider", FLOW_SENSOR2, pour_event, pour_complete),
}
# Start each sensor thread
for _sensor in SENSORS.values():
    _sensor.start()


# Webapp Routes and Handlers
@app.route("/")
def hello():
    return render_template("index.html")


@socketio.on("my_event", namespace=NAMESPACE)
def test_message(message):
    emit("my_response", {"data": message["data"], "count": 0})


@socketio.on("connect", namespace=NAMESPACE)
def test_connect():
    emit("my_response", {"data": "Connected", "count": 0})


@socketio.on("disconnect", namespace=NAMESPACE)
def test_disconnect():
    emit("my_response", {"data": "Disconnected", "count": 0})


# Clean up
@atexit.register
def cleanup():
    logging.info("Sensor cleanup...")
    GPIO.cleanup()


# Main app
if __name__ == '__main__':
    # Start the webserver thread
    socketio.run(app, threaded=True, debug=DEBUG)
