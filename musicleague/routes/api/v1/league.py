import json

from musicleague import app
from musicleague.persistence.select import select_league

LEAGUE_URL = "/api/v1/league/<league_id>/"


@app.route(LEAGUE_URL, methods=['GET'])
def league_get(league_id):
    try:
        league = select_league(league_id)
        if not league:
            return json.dumps(None)

    except Exception:
        return json.dumps(None)

    return json.dumps({
        'name': league.name,
        'active': league.is_active,
        'complete': league.is_complete,
        'public': league.is_public,
        'users': [{
            'id': user.id,
            'name': user.name,
        } for user in league.users],
    })
