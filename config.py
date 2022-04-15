import os

WHOOSH_ENABLED = os.environ.get('HEROKU') is None
