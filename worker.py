from rq import Connection
from rq import Worker

from feedback import default_queue
from feedback import redis_conn
from feedback.notify import notification_queue


if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker([default_queue, notification_queue])
        worker.work()
