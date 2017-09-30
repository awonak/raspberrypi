#!/usr/bin/env python

import atexit
import logging
import time

import RPi.GPIO as GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from flow_meter import FlowMeter

# Constants
DEBUG = False
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
NAMESPACE = "/test"

# Flow sensor pin number
FLOW_SENSOR1 = 22
FLOW_SENSOR2 = 23

# Flask app config
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Configure logging
logging.basicConfig(level=LOG_LEVEL,
                    format='(%(threadName)-10s) %(message)s')


def pour_start(pin):
    sensor = SENSORS[pin]
    socketio.emit('my_response', {"data": "pour start", "count": 0},
                  namespace=NAMESPACE)

def pour_stop(pin):
    """Callback function for pour complete event"""
    sensor = SENSORS[pin]
    socketio.emit('my_response', {"data": sensor.display(), "count": 0},
                  namespace=NAMESPACE)

def pour_event(pin):
    """Callback function for sensor pulse event"""
    sensor = SENSORS[pin]
    socketio.emit('pouring', {"data": sensor.amount}, namespace=NAMESPACE)


# Define your pin:flow_sensor map
SENSORS = {
    FLOW_SENSOR1: FlowMeter("Beer", FLOW_SENSOR1),
    FLOW_SENSOR2: FlowMeter("Cider", FLOW_SENSOR2),
}

# Start each sensor thread
for _sensor in SENSORS.values():
    _sensor.flow_start=pour_start
    _sensor.flow_stop=pour_stop
    _sensor.flow_pulse=pour_event


# Webapp Routes and Handlers
@app.route("/")
def index():
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

    while SENSORS.values():
        for t in SENSORS.values():
            t.stop()

    GPIO.cleanup()


# Main app
if __name__ == '__main__':
    # Start the webserver thread
    socketio.run(app, threaded=True, debug=DEBUG)
