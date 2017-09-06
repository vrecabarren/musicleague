import json

from musicleague import app
from musicleague.league import get_leagues_for_user
from musicleague.user import get_user


USER_URL = "/api/v1/user/<user_id>/"


@app.route(USER_URL, methods=['GET'])
def get_user(user_id):
    try:
        user = get_user(user_id)
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
    } for league in get_leagues_for_user(user)]

    return json.dumps({
        'id': user.id,
        'name': user.name,
        'leagues': leagues,
    })
