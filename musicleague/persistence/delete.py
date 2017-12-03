from musicleague import app
from musicleague.persistence.statements import DELETE_LEAGUE
from musicleague.persistence.statements import DELETE_MEMBERSHIPS
from musicleague.persistence.statements import DELETE_ROUND


def delete_league(league):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_MEMBERSHIPS, (str(league.id),))
                cur.execute(DELETE_LEAGUE, (str(league.id),))
    except Exception as e:
        app.logger.warning('Failed DELETE_LEAGUE: %s', str(e))


def delete_round(round):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_ROUND, (str(round.id),))
    except Exception as e:
        app.logger.warning('Failed DELETE_ROUND: %s', str(e))