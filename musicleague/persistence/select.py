from musicleague import app
from musicleague.models import User
from musicleague.persistence.statements import SELECT_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUES_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_COUNT
from musicleague.persistence.statements import SELECT_ROUNDS_COUNT
from musicleague.persistence.statements import SELECT_ROUNDS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_SUBMISSIONS_COUNT
from musicleague.persistence.statements import SELECT_VOTES_COUNT
from musicleague.persistence.statements import SELECT_USER
from musicleague.persistence.statements import SELECT_USERS_COUNT
from musicleague.persistence.statements import SELECT_USERS_IN_LEAGUE


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


def select_league(league_id):
    try:
        from musicleague import postgres_conn
        from musicleague.persistence.models import League as NewLeague
        from musicleague.persistence.models import Round
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUE, (str(league_id),))
                league_tup = cur.fetchone()
                l = NewLeague(
                    id=str(league_id),
                    created=league_tup[0],
                    name=league_tup[1],
                    owner_id=league_tup[2]
                )

                cur.execute(SELECT_USERS_IN_LEAGUE, (str(league_id),))
                for user_tup in cur.fetchall():
                    user_id = user_tup[0]
                    u = select_user(user_id)
                    l.users.append(u)
                    if user_id == l.owner_id:
                        l.owner = u

                cur.execute(SELECT_ROUNDS_IN_LEAGUE, (str(league_id),))
                for round_tup in cur.fetchall():
                    r = Round(
                        id=round_tup[0],
                        created=round_tup[1],
                        description=round_tup[2],
                        name=round_tup[3],
                        playlist_url=round_tup[4],
                        submissions_due=round_tup[5],
                        votes_due=round_tup[6],
                    )
                    l.submission_periods.append(r)

                return l
    except Exception as e:
        app.logger.warning('Failed SELECT_LEAGUE: %s', str(e))


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
