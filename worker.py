from redis import Redis

from rq import Connection
from rq import Queue
from rq import Worker

from feedback.environment import parse_rediscloud_url


host, port, password = parse_rediscloud_url()
redis_conn = Redis(host=host, port=port, db=0, password=password)
listen = ['default']

with Connection(redis_conn):
    q = Queue('default')

    if __name__ == '__main__':
        worker = Worker([q])
        worker.work()
