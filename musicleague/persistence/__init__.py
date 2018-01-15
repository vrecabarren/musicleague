from psycopg2 import connect
from psycopg2 import extensions

from musicleague.environment import get_environment_setting
from musicleague.environment.variables import DATABASE_URL
from musicleague.persistence.statements import CREATE_TABLE_BOTS
from musicleague.persistence.statements import CREATE_TABLE_INVITED_USERS
from musicleague.persistence.statements import CREATE_TABLE_LEAGUE_PREFERENCES
from musicleague.persistence.statements import CREATE_TABLE_LEAGUES
from musicleague.persistence.statements import CREATE_TABLE_MEMBERSHIPS
from musicleague.persistence.statements import CREATE_TABLE_ROUNDS
from musicleague.persistence.statements import CREATE_TABLE_SUBMISSIONS
from musicleague.persistence.statements import CREATE_TABLE_USER_PREFERENCES
from musicleague.persistence.statements import CREATE_TABLE_USERS
from musicleague.persistence.statements import CREATE_TABLE_VOTES


def get_postgres_conn():
    """ Connect to the PostgreSQL db and init tables. """
    dsn = get_environment_setting(DATABASE_URL)
    postgres_conn = connect(dsn)
    postgres_conn.set_client_encoding('UNICODE')
    extensions.register_type(extensions.UNICODE, postgres_conn)
    extensions.register_type(extensions.UNICODEARRAY, postgres_conn)

    with postgres_conn:
        _init_db(postgres_conn)

    return postgres_conn


def _init_db(postgres_conn):
    """ Create all tables if they don't exist. """
    with postgres_conn.cursor() as cur:
        cur.execute(CREATE_TABLE_USERS)
        cur.execute(CREATE_TABLE_USER_PREFERENCES)
        cur.execute(CREATE_TABLE_LEAGUES)
        cur.execute(CREATE_TABLE_LEAGUE_PREFERENCES)
        cur.execute(CREATE_TABLE_MEMBERSHIPS)
        cur.execute(CREATE_TABLE_INVITED_USERS)
        cur.execute(CREATE_TABLE_ROUNDS)
        cur.execute(CREATE_TABLE_SUBMISSIONS)
        cur.execute(CREATE_TABLE_VOTES)
        cur.execute(CREATE_TABLE_BOTS)
