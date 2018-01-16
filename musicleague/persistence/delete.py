from musicleague import app
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.statements import DELETE_INVITED_USER
from musicleague.persistence.statements import DELETE_LEAGUE
from musicleague.persistence.statements import DELETE_LEAGUE_PREFERENCES
from musicleague.persistence.statements import DELETE_MEMBERSHIP
from musicleague.persistence.statements import DELETE_MEMBERSHIPS
from musicleague.persistence.statements import DELETE_ROUND
from musicleague.persistence.statements import DELETE_ROUNDS


def delete_league(league):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_MEMBERSHIPS, (str(league.id),))
                cur.execute(DELETE_ROUNDS, (str(league.id),))
                cur.execute(DELETE_LEAGUE_PREFERENCES, (str(league.id),))
                cur.execute(DELETE_LEAGUE, (str(league.id),))
    except Exception as e:
        app.logger.error('Failed DELETE_LEAGUE', exc_info=e,
                         extra={'league': str(league.id)})


def delete_round(round):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_ROUND, (str(round.id),))
    except Exception as e:
        app.logger.error('Failed DELETE_ROUND', exc_info=e,
                         extra={'round': str(round.id)})


def delete_membership(league, user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_MEMBERSHIP, (str(league.id), str(user.id)))
    except Exception as e:
        app.logger.error('Failed DELETE_MEMBERSHIP', exc_info=e,
                         extra={'user': str(user.id), 'league': str(league.id)})


def delete_invited_user(invite_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_INVITED_USER, (invite_id,))
    except Exception as e:
        app.logger.error('Failed DELETE_INVITED_USER', exc_info=e,
                         extra={'invitation': invite_id})
