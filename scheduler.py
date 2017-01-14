
from rq import Connection

from musicleague import redis_conn
from musicleague import scheduler


listen = ['default']

if __name__ == '__main__':
    scheduler.run(burst=False)
