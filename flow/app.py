#!/usr/bin/env python

import atexit
import time

import RPi.GPIO as GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from flow_sensor import FlowSensor

# Flow sensor pin number
FLOW_SENSOR1 = 22
FLOW_SENSOR2 = 23

# Flask app config
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')


# Define a callback function for handling pulses
def do_click(pin):
    sensor = SENSORS[pin]
    current_time = int(time.time() * 1000)
    begin = sensor.update(current_time)

    if begin:
        msg = "Begin Pour of {}".format(sensor.name)
        print msg
        socketio.emit('my_response', {"data": msg, "count": 0}, namespace="/test")


# Define your pin:flow_sensor map
SENSORS = {
    FLOW_SENSOR1: FlowSensor("Beer", FLOW_SENSOR1, do_click),
    FLOW_SENSOR2: FlowSensor("Cider", FLOW_SENSOR2, do_click)
}

[s.start() for s in SENSORS.values()]



# Webapp Routes and Handlers
@app.route("/")
def hello():
    return render_template("index.html")


@socketio.on("my_event", namespace="/test")
def test_message(message):
    emit("my_response", {"data": message["data"], "count": 0})


@socketio.on("connect", namespace="/test")
def test_connect():
    emit("my_response", {"data": "Connected", "count": 0})


@socketio.on("disconnect", namespace="/test")
def test_disconnect():
    emit("my_response", {"data": "Disconnected", "count": 0})


# Clean up
@atexit.register
def cleanup():
    print "Sensor cleanup..."
    GPIO.cleanup()


# Main app
if __name__ == '__main__':
    socketio.run(app, threaded=True, debug=False)
