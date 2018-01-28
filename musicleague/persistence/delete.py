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
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_ROUNDS_IN_LEAGUE, (league.id,))
            for round_id_tup in cur.fetchall():
                round_id = round_id_tup[0]
                cur.execute(DELETE_VOTES_FOR_ROUND, (round_id,))
                cur.execute(DELETE_SUBMISSIONS_FOR_ROUND, (round_id,))

            cur.execute(DELETE_MEMBERSHIPS, (league.id,))
            cur.execute(DELETE_ROUNDS, (league.id,))
            cur.execute(DELETE_LEAGUE_PREFERENCES, (league.id,))
            cur.execute(DELETE_LEAGUE, (league.id,))


def delete_round(round):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_VOTES_FOR_ROUND, (round.id,))
            cur.execute(DELETE_SUBMISSIONS_FOR_ROUND, (round.id,))
            cur.execute(DELETE_ROUND, (round.id,))


def delete_membership(league, user):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_MEMBERSHIP, (league.id, user.id))


def delete_invited_user(invite_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_INVITED_USER, (invite_id,))
