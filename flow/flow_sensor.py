import RPi.GPIO as GPIO

# Constants
MINUTE = 60.0  # seconds in a minute
SENSOR_FREQ_VOLUME = 7.5
FINISHED_DELAY = 2 * MINUTE
MIN_POUR = 0.23  # Minimum pour volume check
DEBUG = False

GPIO.setmode(GPIO.BCM)


class FlowSensor(object):
    clicks = 0
    last_click = 0
    hertz = 0.0
    flow = 0.0
    pour = 0.0
    total_pour = 0.0

    def __init__(self, name, pin, callback):
        # set instance variabes
        self.name = name
        self.pin = pin

        # configure GPIO for this sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=20)

    def __str__(self):
        return "%s\nThis pour: %s\nTotal pour: %s\n" % (
            self.name, self.pour, self.total_pour)

    def display(self):
        print self

    def reset(self):
        self.pour = 0.0
        self.clicks = 0
 
    def done_pouring(self, current_time):
        done = self.pour > MIN_POUR and ((current_time - self.last_time) > FINISHED_DELAY)
        if done:
            self.total_pour += self.pour
        return done
    
    def update(self, current_time):
        # measure flow meter clicks
        self.clicks += 1

        # if a plastic sensor use the following calculation
        # Sensor Frequency (Hz) = 7.5 * Q (Liters/min)
        # Liters = Q * time elapsed (seconds) / 60 (seconds/minute)
        # Liters = (Frequency (Pulses/second) / 7.5) * time elapsed (seconds) / 60
        # Liters = Pulses / (7.5 * 60)
        self.pour = self.clicks / (SENSOR_FREQ_VOLUME * MINUTE)

        if DEBUG:
            print "%s = %s / %s * %s" % (self.pour, self.clicks, SENSOR_FREQ_VOLUME, MINUTE)

        # set last_time for next iteration
        self.last_time = current_time
