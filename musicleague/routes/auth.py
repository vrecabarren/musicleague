from time import time

from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from spotipy import Spotify

from musicleague import app
from musicleague.environment import get_setting
from musicleague.environment.variables import SPOTIFY_BOT_USERNAME
from musicleague.routes.decorators import login_required
from musicleague.spotify import get_spotify_oauth
from musicleague.user import create_user
from musicleague.user import get_user


LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'


@app.before_request
def before_request():
    current_user = session['current_user'] if 'current_user' in session else ''
    g.user = None
    if current_user:
        g.user = get_user(current_user)

    access_token = session['access_token'] if 'access_token' in session else ''
    g.spotify = None
    if access_token:
        expiration = session['expires_at']

        # If auth token has expired, refresh it
        if int(expiration) < int(time()):
            refresh_token = session['refresh_token']
            oauth = get_spotify_oauth()
            token_info = oauth._refresh_access_token(refresh_token)
            access_token = token_info['access_token']
            session['access_token'] = access_token
            session['expires_at'] = token_info['expires_at']
            session['refresh_token'] = token_info['refresh_token']

        g.spotify = Spotify(access_token)


@app.route(LOGIN_URL)
def login():
    # If no current login, send user through Spotify OAuth process.
    # If current login, send user to his/her profile.
    if 'current_user' not in session:
        url = request.url
        oauth = get_spotify_oauth()
        code = oauth.parse_response_code(url)
        if code:
            token_info = oauth.get_access_token(code)
            access_token = token_info['access_token']
            session['access_token'] = access_token
            session['expires_at'] = token_info['expires_at']
            session['refresh_token'] = token_info['refresh_token']

            spotify = Spotify(access_token)
            spotify_user = spotify.current_user()
            user_id = spotify_user.get('id')

            if user_id == get_setting(SPOTIFY_BOT_USERNAME):
                import logging
                logging.warning(
                    'Logging in as BOT. access_token: %s, refresh_token: %s, '
                    'expires_at: %s', token_info['access_token'],
                    token_info['refresh_token'], token_info['expires_at'])

            user = get_user(user_id)

            # If user logging in w/ Spotify does not yet exist, create it
            if not user:
                user_email = spotify_user.get('email')
                user_display_name = spotify_user.get('display_name')
                user_images = spotify_user.get('images')
                user_image_url = ''
                if user_images:
                    user_image_url = user_images[0].get('url', user_image_url)

                user = create_user(id=user_id, email=user_email,
                                   name=(user_display_name or user_id),
                                   image_url=user_image_url)

            session['current_user'] = user.id

            # If user was going to a particular destination before logging in,
            # send them there after login.
            if 'next_url' in session:
                next_url = session['next_url'].decode('base64', 'strict')
                session.pop('next_url')
                return redirect(next_url)

    return redirect(url_for('profile'))


@app.route(LOGOUT_URL)
@login_required
def logout():
    session.pop('current_user')
    session.pop('access_token')
    session.pop('expires_at')
    session.pop('refresh_token')
    return redirect(url_for("hello", action='logout'))
