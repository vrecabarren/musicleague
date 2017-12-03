from musicleague import app
from musicleague.persistence.statements import DELETE_LEAGUE
from musicleague.persistence.statements import DELETE_MEMBERSHIPS


def delete_league(league):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_LEAGUE, (str(league.id),))
                cur.execute(DELETE_MEMBERSHIPS, (str(league.id),))
    except Exception as e:
        app.logger.warning('Failed INSERT_USER: %s', str(e))