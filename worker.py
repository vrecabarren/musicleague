
import redis

from rq import Connection
from rq import Queue
from rq import Worker

from musicleague import redis_conn
from musicleague.environment import get_redis_url


listen = ['default']

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
