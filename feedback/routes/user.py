import json

from flask import g
from flask import request

from feedback import app
from feedback.models import User
from feedback.routes.decorators import login_required
from feedback.routes.decorators import templated
from feedback.league import get_leagues_for_owner
from feedback.league import get_leagues_for_user
from feedback.user import get_user


AUTOCOMPLETE = '/autocomplete/'
PROFILE_URL = '/profile/'
SETTINGS_URL = '/settings/'
VIEW_USER_URL = '/user/<user_id>/'


@app.route(AUTOCOMPLETE)
@login_required
def autocomplete():
    term = request.args.get('term')
    results = User.objects(name__istartswith=term).all()
    results = [{'label': user.name, 'value': user.email} for user in results]
    return json.dumps(results)


@app.route(PROFILE_URL)
@templated('profile.html')
@login_required
def profile():
    leagues = get_leagues_for_user(g.user)
    return {'user': g.user, 'leagues': leagues}


@app.route(SETTINGS_URL)
@templated('settings.html')
@login_required
def settings():
    return {'user': g.user}


@app.route(VIEW_USER_URL)
@templated('user.html')
@login_required
def view_user(user_id):
    page_user = get_user(user_id)
    return {
        'user': g.user,
        'page_user': page_user,
        'user_image': g.spotify.user(user_id).get('images')[0],
        'owner_leagues': len(get_leagues_for_owner(page_user)),
        'contributor_leagues': len(get_leagues_for_user(page_user))
        }
