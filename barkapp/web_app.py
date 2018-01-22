"""Web server for BarkApp.

Detect and log the timestamp of each bark. Serve a webserver to display the
bark events.

"""
from flask import Flask

import rpi_app


app = Flask(__name__)
rpi_app.start()

@app.route('/')
def index():
    """List the alert timestamps."""
    output = 'Barks: <br/><ul>'
    for bark in rpi_app.ALERTS:
        output += '<li>' + bark.isoformat()
    return output
