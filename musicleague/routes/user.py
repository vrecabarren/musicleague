import json

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.models import User
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.league import get_leagues_for_user
from musicleague.user import create_or_update_user
from musicleague.user import get_user


AUTOCOMPLETE = '/autocomplete/'
PROFILE_URL = '/profile/'
SETTINGS_URL = '/settings/'
NOTIFICATIONS_SETTINGS_URL = '/settings/notifications/'
PROFILE_SETTINGS_URL = '/settings/profile/'
SYNC_PROFILE_SETTINGS_URL = '/settings/profile/sync/'
VIEW_USER_URL = '/user/<user_id>/'


@app.route(AUTOCOMPLETE, methods=['POST'])
@login_required
def autocomplete():
    term = request.form.get('query')
    results = User.objects(name__icontains=term).all().limit(10)
    results = [{'label': user.name, 'id': user.id}
               for user in results if user.id != g.user.id]
    return json.dumps(sorted(results, key=lambda u: u['label']))


@app.route(PROFILE_URL)
@templated('profile/page.html')
@login_required
def profile():
    page_user = g.user

    leagues = get_leagues_for_user(g.user)

    if request.args.get('pg_update') == '1':
        from musicleague.persistence.insert import insert_league
        for league in leagues:
            insert_league(league)

    return {
        'user': g.user,
        'page_user': page_user,
        'leagues': leagues,
        'contributor_leagues': len(leagues)
        }


@app.route(SETTINGS_URL, methods=['GET'])
@login_required
def forward_settings():
    return redirect(PROFILE_SETTINGS_URL)


@app.route(PROFILE_SETTINGS_URL, methods=['GET'])
@templated('settings/profile.html')
@login_required
def view_profile_settings():
    return {'user': g.user}


@app.route(PROFILE_SETTINGS_URL, methods=['POST'])
@login_required
def save_profile_settings():
    name = request.form.get('name')
    email = request.form.get('email')
    image_url = request.form.get('image_url')
    create_or_update_user(g.user.id, name, email, image_url)
    return redirect(request.referrer)


@app.route(SYNC_PROFILE_SETTINGS_URL, methods=['GET'])
@login_required
def sync_profile_settings():
    spotify_user = g.spotify.current_user()
    user_email = spotify_user.get('email')
    user_display_name = spotify_user.get('display_name')
    user_images = spotify_user.get('images')
    user_image_url = ''
    if user_images:
        user_image_url = user_images[0].get('url', user_image_url)

    create_or_update_user(g.user.id, user_display_name, user_email,
                          user_image_url)

    return redirect(request.referrer)


@app.route(NOTIFICATIONS_SETTINGS_URL, methods=['GET'])
@templated('settings/notifications.html')
@login_required
def view_notification_settings():
    return {'user': g.user}


@app.route(NOTIFICATIONS_SETTINGS_URL, methods=['POST'])
@login_required
def save_notification_settings():
    user = g.user

    for field_name in user.preferences._fields:
        enabled = request.form.get(field_name) == 'on'
        user.preferences[field_name] = enabled

    user.save()
    return redirect(request.referrer)


@app.route(VIEW_USER_URL)
@templated('profile/page.html')
@login_required
def view_user(user_id):
    if user_id == str(g.user.id):
        return redirect(url_for('profile'))
    page_user = get_user(user_id)
    leagues = get_leagues_for_user(page_user)

    if request.args.get('pg_update') == '1':
        from musicleague.persistence.insert import insert_league
        for league in leagues:
            insert_league(league)

    if request.args.get('pg') == '1':
        from musicleague.persistence.select import select_memberships_count
        contributor_leagues = select_memberships_count(page_user.id)
    else:
        contributor_leagues = len(get_leagues_for_user(page_user))

    return {
        'user': g.user,
        'page_user': page_user,
        'leagues': leagues,
        'contributor_leagues': contributor_leagues
        }
