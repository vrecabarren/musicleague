import json

from flask import g
from flask import redirect
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
@templated('user.html')
@login_required
def profile():
    page_user = g.user
    leagues = get_leagues_for_user(g.user)
    return {
        'user': g.user,
        'page_user': page_user,
        'user_image': g.spotify.user(str(page_user.id)).get('images')[0],
        'leagues': leagues,
        'owner_leagues': len(get_leagues_for_owner(page_user)),
        'contributor_leagues': len(get_leagues_for_user(page_user))
        }


@app.route(SETTINGS_URL, methods=['GET'])
@templated('settings.html')
@login_required
def view_settings():
    return {'user': g.user}


@app.route(SETTINGS_URL, methods=['POST'])
@login_required
def save_settings():
    user = g.user

    for field_name in user.preferences._fields:
        enabled = request.form.get(field_name) == 'on'
        user.preferences[field_name] = enabled

    user.save()
    return redirect(request.referrer)


@app.route(VIEW_USER_URL)
@templated('user.html')
@login_required
def view_user(user_id):
    page_user = get_user(user_id)
    leagues = get_leagues_for_user(g.user)
    return {
        'user': g.user,
        'page_user': page_user,
        'user_image': g.spotify.user(user_id).get('images')[0],
        'leagues': leagues,
        'owner_leagues': len(get_leagues_for_owner(page_user)),
        'contributor_leagues': len(get_leagues_for_user(page_user))
        }
