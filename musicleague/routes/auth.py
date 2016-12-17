import logging
from time import time

from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from spotipy import Spotify

from musicleague import app
from musicleague.bot import create_or_update_bot
from musicleague.bot import is_bot
from musicleague.routes.decorators import login_required
from musicleague.spotify import get_spotify_oauth
from musicleague.user import create_user_from_spotify_user
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
            refresh_token = token_info['refresh_token']
            expires_at = int(token_info['expires_at'])

            spotify = Spotify(access_token)
            spotify_user = spotify.current_user()
            user_id = spotify_user.get('id')

            if is_bot(user_id):
                logging.warn('Create/update bot %s: %s, %s, %s', user_id,
                             access_token, refresh_token, expires_at)
                create_or_update_bot(user_id, access_token, refresh_token,
                                     expires_at)

            user = get_user(user_id)

            # If user logging in w/ Spotify does not yet exist, create it
            if not user:
                user = create_user_from_spotify_user(spotify_user)

            _update_session(user_id, access_token, refresh_token, expires_at)

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
    _clear_session()
    return redirect(url_for("hello", action='logout'))


def _update_session(user_id, access_token, refresh_token, expires_at):
    session['current_user'] = user_id
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    session['expires_at'] = expires_at


def _clear_session():
    session.pop('current_user')
    session.pop('access_token')
    session.pop('expires_at')
    session.pop('refresh_token')
