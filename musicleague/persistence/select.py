from musicleague import app
from musicleague.models import User
from musicleague.persistence.statements import SELECT_LEAGUES_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_COUNT
from musicleague.persistence.statements import SELECT_ROUNDS_COUNT
from musicleague.persistence.statements import SELECT_SUBMISSIONS_COUNT
from musicleague.persistence.statements import SELECT_VOTES_COUNT
from musicleague.persistence.statements import SELECT_USER
from musicleague.persistence.statements import SELECT_USERS_COUNT


def select_user(user_id):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USER, (str(user_id),))
                u = User()
                u.id = user_id
                u.email, u.image_url, u.joined, u.name, u.profile_background = cur.fetchone()
                return u
    except Exception as e:
        app.logger.warning('Failed SELECT_USER: %s', str(e))


def select_users_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USERS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_USERS_COUNT: %s', str(e))


def select_leagues_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUES_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_LEAGUES_COUNT: %s', str(e))


def select_memberships_count(user_id):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_COUNT, (str(user_id),))
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_MEMBERSHIPS_COUNT: %s', str(e))


def select_rounds_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUNDS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_ROUNDS_COUNT: %s', str(e))


def select_submissions_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_SUBMISSIONS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_SUBMISSIONS_COUNT: %s', str(e))


def select_votes_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_VOTES_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_VOTES_COUNT: %s', str(e))
