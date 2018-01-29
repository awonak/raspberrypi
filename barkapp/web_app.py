"""Web server for BarkApp.

Detect and log the timestamp of each bark. Serve a webserver to display the
bark events.

"""
from flask import Flask
from flask import jsonify
from flask import send_file


try:
    import sensors
except RuntimeError:
    import fake_sensors as sensors


app = Flask(__name__, static_url_path='', static_folder='./ionic/www')
sensors.start()


@app.route("/")
def index():
    """Serve index.html file."""
    return send_file("./ionic/www/index.html")


@app.route("/api/barks")
def barks():
    """List the alert timestamps."""
    alerts = []
    for alert in sensors.get_alerts():
        alerts.append(alert.isoformat())
    return jsonify(alerts)

@app.route("/api/barks/last")
def last_bark():
    """Get the timestamp of the last bark."""
    return jsonify(max(sensors.get_alerts()))
