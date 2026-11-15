"""HTTP API for triggering the sprayer and checking on the system."""

from __future__ import annotations

import logging
import os

from flask import Blueprint, Flask, jsonify

from pi_logic.config import ConfigError
from pi_logic.motor_logic import SprayerBusyError, cycle_sprayer_manually
from pi_logic.spray_log import last_spray
from pi_logic.thermostat_logic import ThermostatError, get_thermostat

logger = logging.getLogger(__name__)

# Every route sits under /api, so a web server can send these paths here and serve
# the frontend from the rest of the same address.
api = Blueprint("api", __name__, url_prefix="/api")


@api.errorhandler(SprayerBusyError)
def handle_sprayer_busy(error):
    return jsonify(error=str(error)), 409


@api.errorhandler(ThermostatError)
def handle_thermostat_error(error):
    # The cause can include device URLs, so it goes to the log rather than the client.
    logger.warning("Thermostat request failed: %s", error)
    return jsonify(error="Could not reach the thermostat"), 502


@api.errorhandler(ConfigError)
def handle_config_error(error):
    logger.error("%s. See .env.example.", error)
    return jsonify(error="Thermostat credentials are not configured"), 503


@api.post("/spray")
def spray():
    """Start the fan and run a spray cycle, returning its time once complete."""
    cycle_sprayer_manually()
    return jsonify(last_spray())


@api.get("/timestamp")
def timestamp():
    """Return the time of the most recent spray."""
    latest = last_spray()
    if latest is None:
        return jsonify(error="No sprays recorded"), 404
    return jsonify(latest)


@api.get("/status")
def status():
    """Return the current state of the HVAC system."""
    return jsonify(status=get_thermostat().get_hvac_status())


app = Flask(__name__)
app.register_blueprint(api)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # Flask's development server, for running locally. On the Pi, gunicorn runs the app instead.
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")))
