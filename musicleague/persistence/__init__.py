from psycopg2 import connect

from musicleague.environment import get_environment_setting
from musicleague.environment.variables import DATABASE_URL
from musicleague.persistence.statements import CREATE_TABLE_LEAGUES
from musicleague.persistence.statements import CREATE_TABLE_ROUNDS
from musicleague.persistence.statements import CREATE_TABLE_USERS


def get_postgres_conn():
    """ Connect to the PostgreSQL db and init tables. """
    dsn = get_environment_setting(DATABASE_URL)
    postgres_conn = connect(dsn)

    with postgres_conn:
        _init_db(postgres_conn)

    return postgres_conn


def _init_db(postgres_conn):
    """ Create all tables if they don't exist. """
    with postgres_conn.cursor() as cur:
        cur.execute(CREATE_TABLE_USERS)
        cur.execute(CREATE_TABLE_LEAGUES)
        cur.execute(CREATE_TABLE_ROUNDS)