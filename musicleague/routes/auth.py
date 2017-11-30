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
from musicleague.notify.flash import flash_info
from musicleague.persistence.select import select_user
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.spotify import get_spotify_oauth
from musicleague.user import create_user_from_spotify_user
from musicleague.user import get_user
from musicleague.user import update_user_from_spotify_user


LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
ADD_BOT_URL = '/add_bot/'
USER_ID_URL = '/id/'


@app.before_request
def before_request():
    current_user = session['current_user'] if 'current_user' in session else ''
    g.user = None
    if current_user:
        if request.args.get('pg') == '1':
            g.user = select_user(current_user)
        else:
            g.user = get_user(current_user)

    access_token = session['access_token'] if 'access_token' in session else ''
    g.spotify = None
    if access_token:
        expiration = session['expires_at']

        # If auth token has expired, refresh it
        if int(expiration) < int(time()):
            refresh_token = session['refresh_token']
            oauth = get_spotify_oauth()
            token_info = oauth.refresh_access_token(refresh_token)
            access_token = token_info['access_token']
            _update_session(
                current_user, access_token, token_info['refresh_token'],
                int(token_info['expires_at']))

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

            user = get_user(user_id)

            # If user logging in w/ Spotify does not yet exist, create it
            if not user:
                user = create_user_from_spotify_user(spotify_user)

            # If user's image is from Facebook, token may have expired.
            # TODO: This needs to be smarter
            elif 'fbcdn.net' in user.image_url:
                user = update_user_from_spotify_user(user, spotify_user)

            _update_session(user_id, access_token, refresh_token, expires_at)
            session.permanent = True

            # If user was going to a particular destination before logging in,
            # send them there after login.
            if 'next_url' in session:
                next_url = session['next_url'].decode('base64', 'strict')
                session.pop('next_url')
                return redirect(next_url)

    return redirect(url_for('profile'))


@app.route(USER_ID_URL, methods=['GET'])
@login_required
@templated('id.html')
def user_id():
    return {
        'user': g.user,
    }


@app.route(ADD_BOT_URL)
def add_bot():
    _clear_session()
    oauth = get_spotify_oauth(bot=True)
    code = oauth.parse_response_code(request.url)
    if code:
        token_info = oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        expires_at = int(token_info['expires_at'])

        spotify = Spotify(access_token)
        spotify_user = spotify.current_user()
        bot_id = spotify_user['id']

        # Check that we're adding a bot listed in env var list
        if not is_bot(bot_id):
            return 'Invalid bot: %s. If valid, add to environment.' % (bot_id)

        app.logger.warn('Create/update bot %s: %s, %s, %s', bot_id,
                        access_token, refresh_token, expires_at)

        create_or_update_bot(bot_id, access_token, refresh_token, expires_at)

        return 'Successfully added bot: %s' % (bot_id)

    return redirect(oauth.get_authorize_url())


@app.route(LOGOUT_URL)
@login_required
def logout():
    _clear_session()
    flash_info("You have been logged out of Music League.")
    return redirect(url_for("hello"))


def _update_session(user_id, access_token, refresh_token, expires_at):
    session['current_user'] = user_id
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    session['expires_at'] = expires_at


def _clear_session():
    if 'current_user' in session:
        session.pop('current_user')
    if 'access_token' in session:
        session.pop('access_token')
    if 'expires_at' in session:
        session.pop('expires_at')
    if 'refresh_token' in session:
        session.pop('refresh_token')
