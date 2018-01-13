from musicleague import app
from musicleague.persistence.statements import DELETE_INVITED_USER
from musicleague.persistence.statements import DELETE_LEAGUE
from musicleague.persistence.statements import DELETE_MEMBERSHIP
from musicleague.persistence.statements import DELETE_MEMBERSHIPS
from musicleague.persistence.statements import DELETE_ROUND
from musicleague.persistence.statements import DELETE_ROUNDS


def delete_league(league):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_MEMBERSHIPS, (str(league.id),))
                cur.execute(DELETE_ROUNDS, (str(league.id),))
                cur.execute(DELETE_LEAGUE, (str(league.id),))
    except Exception as e:
        app.logger.warning('Failed DELETE_LEAGUE: %s', str(e), exc_info=e)


def delete_round(round):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_ROUND, (str(round.id),))
    except Exception as e:
        app.logger.warning('Failed DELETE_ROUND: %s', str(e), exc_info=e)


def delete_membership(league, user):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_MEMBERSHIP, (str(league.id), str(user.id)))
    except Exception as e:
        app.logger.warning('Failed DELETE_MEMBERSHIP: %s', str(e), exc_info=e)


def delete_invited_user(invite_id):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_INVITED_USER, (invite_id,))
    except Exception as e:
        app.logger.warning('Failed DELETE_INVITED_USER: %s', str(e), exc_info=e)
