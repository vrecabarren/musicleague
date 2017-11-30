from musicleague import app
from musicleague.persistence.statements import DELETE_LEAGUE


def delete_league(league):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_LEAGUE, (str(league.id),))
    except Exception as e:
        app.logger.warning('Failed INSERT_USER: %s', str(e))