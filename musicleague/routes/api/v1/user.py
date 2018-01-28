import json

from musicleague import app
from musicleague.persistence.select import select_leagues_for_user
from musicleague.persistence.select import select_user


USER_URL = "/api/v1/user/<user_id>/"


@app.route(USER_URL, methods=['GET'])
def get_user(user_id):
    try:
        user = select_user(user_id)
        if not user:
            return json.dumps(None)

    except Exception:
        return json.dumps(None)

    leagues = [{
        'name': league.name,
        'active': league.is_active,
        'complete': league.is_complete,
        'users': [{
            'id': user.id,
            'name': user.name,
        } for user in league.users]
    } for league in select_leagues_for_user(user)]

    return json.dumps({
        'id': user.id,
        'name': user.name,
        'leagues': leagues,
    })
