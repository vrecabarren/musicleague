import json
from os import getenv

from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from musicleague import app
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.update import update_user
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.persistence.select import select_memberships_count
from musicleague.persistence.update import upsert_user_preferences
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
    results = []
    term = request.form.get('query')
    stmt = 'SELECT name, id FROM users WHERE name ILIKE %s OR name ILIKE %s ORDER BY 1 LIMIT 10'
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt, ('%' + term, '%' + term + '%'))
            for user_tup in cur.fetchall():
                name, id = user_tup
                if id != g.user.id:
                    results.append({'label': name, 'id': id})
    return json.dumps(results)


@app.route(PROFILE_URL)
@templated('profile/page.html')
@login_required
def profile():
    page_user = g.user

    from musicleague.persistence.select import select_leagues_for_user
    from musicleague.persistence.select import select_memberships_placed
    leagues = select_leagues_for_user(page_user.id, exclude_properties=['rounds', 'invited_users', 'scoreboard'])
    placed_leagues = select_memberships_placed(page_user.id)

    return {
        'user': g.user,
        'page_user': page_user,
        'leagues': leagues,
        'contributor_leagues': len(leagues),
        'placed_leagues': placed_leagues,
        'access_token': session['access_token'],
        'api_domain': getenv('API_DOMAIN'),
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
    g.user.name = request.form.get('name')
    g.user.email = request.form.get('email')
    g.user.image_url = request.form.get('image_url')
    update_user(g.user)
    return redirect(request.referrer)


@app.route(SYNC_PROFILE_SETTINGS_URL, methods=['GET'])
@login_required
def sync_profile_settings():
    spotify_user = g.spotify.current_user()
    g.user.email = spotify_user.get('email')

    # Display name will be None if not linked to social media
    display_name = spotify_user.get('display_name')
    if display_name is None:
        display_name = spotify_user.get('id')
    g.user.name = display_name

    # There will be no images if not linked to social media
    user_images = spotify_user.get('images')
    user_image_url = ''
    if user_images:
        g.user.image_url = user_images[0].get('url', user_image_url)

    update_user(g.user)

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

    for k in user.preferences.settings_keys():
        enabled = request.form.get(k) == 'on'
        user.preferences.__dict__[k] = enabled

    upsert_user_preferences(user)

    return redirect(request.referrer)


@app.route(VIEW_USER_URL)
@templated('profile/page.html')
@login_required
def view_user(user_id):
    if user_id == str(g.user.id):
        return redirect(url_for('profile'))

    page_user = get_user(user_id)

    from musicleague.persistence.select import select_leagues_for_user
    from musicleague.persistence.select import select_memberships_placed
    leagues = select_leagues_for_user(page_user.id, exclude_properties=['rounds', 'invited_users', 'scoreboard'])
    placed_leagues = select_memberships_placed(page_user.id)

    return {
        'user': g.user,
        'page_user': page_user,
        'leagues': leagues,
        'contributor_leagues': select_memberships_count(page_user.id),
        'placed_leagues': placed_leagues
    }
