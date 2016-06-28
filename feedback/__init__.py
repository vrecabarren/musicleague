# flake8: noqa
import logging
import sys

from flask import Flask
from flask_moment import Moment

from feedback.environment import get_secret_key
from feedback.environment import get_server_name
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import parse_mongolab_uri
from feedback.environment import parse_rediscloud_url

from mongoengine import connect

from redis import Redis

from rq import Connection
from rq import Queue

from rq_scheduler import Scheduler

from settings import MONGO_DB_NAME


# Initialize Flask app
app = Flask(__name__)
moment = Moment(app)
app.secret_key = get_secret_key()
app.config['SERVER_NAME'] = get_server_name()

if is_deployed():
    host, port, username, password, db = parse_mongolab_uri()
    db = connect(db, host=host, port=port, username=username, password=password)
    logging.basicConfig(level=logging.DEBUG if is_debug() else logging.WARNING)
else:
    db = connect(MONGO_DB_NAME)
    logging.basicConfig(level=logging.DEBUG)

app.logger.addHandler(logging.StreamHandler(sys.stdout))

# Initialize Redis connection
host, port, password = parse_rediscloud_url()
redis_conn = Redis(host=host, port=port, db=0, password=password)

# Initialize Redis queues
with Connection(redis_conn):
    default_queue = Queue('default')
    notification_queue = Queue('notifications')
    queues = [default_queue, notification_queue]


# Initialize Redis queue scheduler
scheduler = Scheduler(default_queue.name, connection=redis_conn)


from feedback import routes
