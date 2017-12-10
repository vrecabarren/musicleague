from musicleague import app
from musicleague.persistence.statements import UPDATE_MEMBERSHIP_RANK
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
        app.logger.warning('Failed INSERT_USER: %s', str(e))


def update_membership_rank(league, user, rank):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_MEMBERSHIP_RANK, (rank, str(league.id), str(user.id)))
    except Exception as e:
        app.logger.warning('Failed UPDATE_MEMBERSHIP_RANK: %s', str(e))


def update_submission_rank(round, spotify_uri, rank):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_SUBMISSION_RANK, (rank, str(round.id), spotify_uri))
    except Exception as e:
        app.logger.warning('Failed UPDATE_SUBMISSION_RANK: %s', str(e))
