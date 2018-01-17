from musicleague import app
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.statements import DELETE_INVITED_USER
from musicleague.persistence.statements import DELETE_LEAGUE
from musicleague.persistence.statements import DELETE_LEAGUE_PREFERENCES
from musicleague.persistence.statements import DELETE_MEMBERSHIP
from musicleague.persistence.statements import DELETE_MEMBERSHIPS
from musicleague.persistence.statements import DELETE_ROUND
from musicleague.persistence.statements import DELETE_ROUNDS
from musicleague.persistence.statements import DELETE_SUBMISSIONS_FOR_ROUND
from musicleague.persistence.statements import DELETE_VOTES_FOR_ROUND
from musicleague.persistence.statements import SELECT_ROUNDS_IN_LEAGUE


def delete_league(league):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUNDS_IN_LEAGUE, (league.id,))
                for round_id_tup in cur.fetchall():
                    round_id = round_id_tup[0]
                    cur.execute(DELETE_VOTES_FOR_ROUND, (round_id,))
                    cur.execute(DELETE_SUBMISSIONS_FOR_ROUND, (round_id,))

                cur.execute(DELETE_MEMBERSHIPS, (league.id,))
                cur.execute(DELETE_ROUNDS, (league.id,))
                cur.execute(DELETE_LEAGUE_PREFERENCES, (league.id,))
                cur.execute(DELETE_LEAGUE, (league.id,))
    except Exception as e:
        app.logger.error('Failed DELETE_LEAGUE', exc_info=e,
                         extra={'league': league.id})


def delete_round(round):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_ROUND, (round.id,))
    except Exception as e:
        app.logger.error('Failed DELETE_ROUND', exc_info=e,
                         extra={'round': round.id})


def delete_membership(league, user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_MEMBERSHIP, (league.id, user.id))
    except Exception as e:
        app.logger.error('Failed DELETE_MEMBERSHIP', exc_info=e,
                         extra={'user': user.id, 'league': league.id})


def delete_invited_user(invite_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_INVITED_USER, (invite_id,))
    except Exception as e:
        app.logger.error('Failed DELETE_INVITED_USER', exc_info=e,
                         extra={'invitation': invite_id})
