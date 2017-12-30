from musicleague import app
from musicleague.persistence.statements import UPDATE_LEAGUE
from musicleague.persistence.statements import UPDATE_LEAGUE_STATUS
from musicleague.persistence.statements import UPDATE_MEMBERSHIP_RANK
from musicleague.persistence.statements import UPDATE_ROUND
from musicleague.persistence.statements import UPDATE_ROUND_STATUS
from musicleague.persistence.statements import UPDATE_SUBMISSION_RANK
from musicleague.persistence.statements import UPDATE_USER


def update_user(user):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPDATE_USER,
                    (user.email, user.image_url, user.name,
                     user.profile_background, str(user.id)))
    except Exception as e:
        app.logger.warning('Failed UPDATE_USER: %s', str(e), exc_info=e)


def update_league(league):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_LEAGUE, (league.name, league.status, str(league.id)))
    except Exception as e:
        app.logger.warning('Failed UPDATE_LEAGUE: %s', str(e), exc_info=e)


def update_league_status(league, status):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_LEAGUE_STATUS, (status, str(league.id)))
    except Exception as e:
        app.logger.warning('Failed UPDATE_LEAGUE_STATUS: %s', str(e), exc_info=e)


def update_membership_rank(league, user, rank):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_MEMBERSHIP_RANK, (rank, str(league.id), str(user.id)))
    except Exception as e:
        app.logger.warning('Failed UPDATE_MEMBERSHIP_RANK: %s', str(e), exc_info=e)


def update_round(round):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPDATE_ROUND,
                    (round.description, round.name, round.submission_due_date, round.vote_due_date, round.id))
    except Exception as e:
        app.logger.warning('Failed UPDATE_ROUND: %s', str(e), exc_info=e)


def update_round_status(round, status):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_ROUND_STATUS, (status, str(round.id)))
    except Exception as e:
        app.logger.warning('Failed UPDATE_ROUND_STATUS: %s', str(e), exc_info=e)


def update_submission_rank(round, spotify_uri, rank):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_SUBMISSION_RANK, (rank, str(round.id), spotify_uri))
    except Exception as e:
        app.logger.warning('Failed UPDATE_SUBMISSION_RANK: %s', str(e), exc_info=e)
