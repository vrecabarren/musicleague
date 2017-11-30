from musicleague import app
from musicleague.models import User
from musicleague.persistence.statements import SELECT_USER


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
