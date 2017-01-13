import logging
import sys

from flask import Flask
from flask_moment import Moment

from redis import Redis

from rq import Queue
from rq_scheduler import Scheduler

from musicleague.environment import get_redis_url
from musicleague.environment import get_secret_key
from musicleague.environment import get_server_name
from musicleague.environment import is_debug
from musicleague.environment import is_deployed
from musicleague.environment import parse_mongolab_uri

from mongoengine import connect

from settings import MONGO_DB_NAME


# Initialize Flask app
app = Flask(__name__)
moment = Moment(app)
app.secret_key = get_secret_key()

if is_deployed():
    app.config['SERVER_NAME'] = get_server_name()

    host, port, username, password, db = parse_mongolab_uri()
    db = connect(db, host=host, port=port, username=username,
                 password=password)
    logging.basicConfig(level=logging.DEBUG if is_debug() else logging.WARNING)
else:
    db = connect(MONGO_DB_NAME)
    logging.basicConfig(level=logging.DEBUG)

app.logger.addHandler(logging.StreamHandler(sys.stdout))

redis_conn = Redis.from_url(get_redis_url())
queue = Queue(connection=redis_conn)
scheduler = Scheduler(connection=redis_conn)

from musicleague import routes  # noqa
