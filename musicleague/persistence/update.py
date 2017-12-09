from musicleague import app
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