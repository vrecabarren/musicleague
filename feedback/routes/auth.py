from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from spotipy import Spotify

from feedback import app
from feedback.routes import urls
from feedback.routes.decorators import login_required
from feedback.spotify import get_spotify_oauth
from feedback.user import create_or_update_user
from feedback.user import get_user


@app.before_request
def before_request():
    current_user = session['current_user'] if 'current_user' in session else ''
    g.user = get_user(current_user) if current_user else None

    access_token = session['access_token'] if 'access_token' in session else ''
    g.spotify = Spotify(access_token) if access_token else None


@app.route(urls.LOGIN_URL)
def login():
    if 'current_user' not in session:
        url = request.url
        oauth = get_spotify_oauth()
        code = oauth.parse_response_code(url)
        if code:
            token_info = oauth.get_access_token(code)
            access_token = token_info['access_token']
            session['access_token'] = access_token

            spotify = Spotify(access_token)
            user = create_or_update_user(
                id=spotify.current_user().get('id'),
                email=spotify.current_user().get('email'),
                name=spotify.current_user().get('display_name'))

            session['current_user'] = user.id

    return redirect(url_for('profile'))


@app.route(urls.LOGOUT_URL)
@login_required
def logout():
    session.pop('current_user')
    return redirect(url_for("hello"))
