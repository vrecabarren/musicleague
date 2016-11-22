import json

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.models import User
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.league import get_leagues_for_owner
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


@app.route(AUTOCOMPLETE)
@login_required
def autocomplete():
    term = request.args.get('term')
    results = User.objects(name__istartswith=term).all()
    results = [{'name': user.name,
                'id': user.id,
                'email': user.email,
                'image_url': user.image_url} for user in results]
    return json.dumps(results)


@app.route(PROFILE_URL)
@templated('user.html')
@login_required
def profile():
    page_user = g.user
    leagues = get_leagues_for_user(g.user)
    tracks = []
    for league in leagues:
        if league.current_submission_period:
            tracks.extend(league.current_submission_period.all_tracks[:3])

    tracks = g.spotify.tracks(tracks).get('tracks') if tracks else []
    tracks_by_uri = {track['uri']: track for track in tracks}

    images = g.spotify.user(str(page_user.id)).get('images')
    return {
        'user': g.user,
        'page_user': page_user,
        'user_image': images[0] if images else '',
        'leagues': leagues,
        'tracks_by_uri': tracks_by_uri,
        'owner_leagues': len(get_leagues_for_owner(page_user)),
        'contributor_leagues': len(get_leagues_for_user(page_user))
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
@templated('user.html')
@login_required
def view_user(user_id):
    if user_id == str(g.user.id):
        return redirect(url_for('profile'))
    page_user = get_user(user_id)
    leagues = get_leagues_for_user(page_user)
    tracks = []
    for league in leagues:
        if league.current_submission_period:
            tracks.extend(league.current_submission_period.all_tracks[:3])

    tracks = g.spotify.tracks(tracks).get('tracks') if tracks else []
    tracks_by_uri = {track['uri']: track for track in tracks}

    images = g.spotify.user(user_id).get('images')
    return {
        'user': g.user,
        'page_user': page_user,
        'user_image': images[0] if images else '',
        'leagues': leagues,
        'tracks_by_uri': tracks_by_uri,
        'owner_leagues': len(get_leagues_for_owner(page_user)),
        'contributor_leagues': len(get_leagues_for_user(page_user))
        }
