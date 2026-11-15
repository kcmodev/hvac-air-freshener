"""Production server settings. gunicorn reads this file when started from this folder."""

import logging

# Only nginx, on the same Pi, talks to the API. The port must match deploy/nginx/hvac.conf.
bind = "127.0.0.1:8000"

# One process keeps memory use low. Its threads let status checks run while a manual
# spray holds its request open.
workers = 1
threads = 4

# A manual spray takes about 15 seconds, well past gunicorn's usual limit for a request.
timeout = 60

# Send the app's own log messages, not just gunicorn's, to the journal.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
