"""Web server for BarkApp.

Detect and log the timestamp of each bark. Serve a webserver to display the
bark events.

"""
from flask import Flask

import sensors


app = Flask(__name__)
sensors.start()

@app.route('/')
def index():
    """List the alert timestamps."""
    output = 'Barks: <br/><ul>'
    for alert in sensors.get_alerts():
        output += '<li>' + alert.isoformat()
    return output
