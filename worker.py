
from rq import Connection
from rq import Queue
from rq import Worker

from musicleague import redis_conn


listen = ['default']

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
