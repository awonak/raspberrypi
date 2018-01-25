"""Web server for BarkApp.

Detect and log the timestamp of each bark. Serve a webserver to display the
bark events.

"""
from flask import Flask
from flask import jsonify

try:
    import rpi_app
    rpi_app.start()
    alerts = rpi_app.ALERTS
except RuntimeError as e:
    import datetime
    import time
    alerts = [datetime.datetime.now()]
    time.sleep(1)
    alerts.append(datetime.datetime.now())

app = Flask(__name__)

@app.route('/')
def index():
    """List the alert timestamps."""
    output = 'Barks: <br/><ul>'
    for bark in alerts:
        output += '<li>' + bark.isoformat()
    return output

@app.route('/api/barks')
def barks():
    """List the alert timestamps."""
    return jsonify(alerts)
