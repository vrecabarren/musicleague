from rq import Connection
from rq import Worker

from feedback import q
from feedback import redis_conn


if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker([q])
        worker.work()
