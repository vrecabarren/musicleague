from datetime import datetime
import logging

from flask import Flask
from flask import g
from flask import request
from flask_moment import Moment

from logentries import LogentriesHandler

from redis import Redis

from rq import Queue
from rq_scheduler import Scheduler

from musicleague.environment import get_redis_url
from musicleague.environment import get_secret_key
from musicleague.environment import get_server_name
from musicleague.environment import get_setting
from musicleague.environment import is_deployed
from musicleague.environment import parse_mongolab_uri
from musicleague.environment.variables import LOGENTRIES_TOKEN

from mongoengine import connect

from settings import MONGO_DB_NAME


# Initialize Flask app
app = Flask(__name__)
moment = Moment(app)
app.secret_key = get_secret_key()


class ContextualFilter(logging.Filter):

    def filter(self, log_record):
        log_record.utcnow = (datetime.utcnow()
                             .strftime('%Y-%m-%d %H:%M:%S,%f %Z'))
        log_record.url = request.path
        log_record.method = request.method
        log_record.user_id = g.user.id
        log_record.ip = request.environ.get('HTTP_X_REAL_IP',
                                            request.remote_addr)
        return True

log_format = ("%(utcnow)s\tl=%(levelname)s\tu=%(user_id)s\tip=%(ip)s"
              "\tm=%(method)s\turl=%(url)s\tmsg=%(message)s")
formatter = logging.Formatter(log_format)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(formatter)

leHandler = LogentriesHandler(get_setting(LOGENTRIES_TOKEN))
leHandler.setLevel(logging.INFO)
leHandler.setFormatter(formatter)

log = app.logger
log.setLevel(logging.DEBUG)
log.addFilter(ContextualFilter())
log.addHandler(streamHandler)
log.addHandler(leHandler)


if is_deployed():
    app.config['SERVER_NAME'] = get_server_name()

    host, port, username, password, db = parse_mongolab_uri()
    db = connect(db, host=host, port=port, username=username,
                 password=password)
else:
    db = connect(MONGO_DB_NAME)

redis_conn = Redis.from_url(get_redis_url())
queue = Queue(connection=redis_conn)
scheduler = Scheduler(connection=redis_conn)

from musicleague import routes  # noqa
