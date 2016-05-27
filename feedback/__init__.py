import logging
import sys

from flask import Flask

from feedback.environment import get_secret_key
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import parse_mongolab_uri

from mongoengine import connect

from settings import MONGO_DB_NAME


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.secret_key = get_secret_key()

if is_deployed():
    host, port, username, password, db = parse_mongolab_uri()
    db = connect(db, host=host, port=port, username=username,
                 password=password)
    app.logger.setLevel(logging.DEBUG if is_debug() else logging.ERROR)
else:
    db = connect(MONGO_DB_NAME)
    app.logger.setLevel(logging.DEBUG)


from feedback import routes
