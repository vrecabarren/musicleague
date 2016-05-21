import logging

from flask import redirect
from flask import render_template
from flask import request
from flask import session as session
from flask import url_for

from spotipy import Spotify

from feedback import app
from feedback.api import create_season
from feedback.api import get_season
from feedback.spotify import get_spotify_oauth
from feedback.user import create_or_update_user
from feedback.views import urls
from feedback.views.decorators import login_required


@app.route(urls.HELLO_URL)
def hello(**kwargs):
    oauth = get_spotify_oauth()
    kwargs['oauth_url'] = oauth.get_authorize_url()
    return render_template("hello.html", **kwargs)


@app.route('/profile/')
@login_required
def profile(**kwargs):
    return render_template("profile.html", **kwargs)


@app.route(urls.LOGOUT_URL)
@login_required
def logout(**kwargs):
    session.pop('current_user')
    return redirect(url_for("hello"))


@app.route(urls.LOGIN_URL)
def login(**kwargs):
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
                spotify.current_user().get('id'),
                spotify.current_user().get('email'),
                spotify.current_user().get('display_name'))

            session['current_user'] = user.id

    return redirect(url_for('profile'))


@app.route(urls.CREATE_SEASON_URL, methods=['GET'])
@login_required
def view_create_season(**kwargs):
    return render_template("create_season.html", **kwargs)


@app.route(urls.CREATE_SEASON_URL, methods=['POST'])
@login_required
def post_create_season(**kwargs):
    try:
        season_name = request.form.get('season_name')
        season = create_season(season_name)
        return redirect(
            url_for(view_season.__name__, season_name=season.name))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(urls.VIEW_SEASON_URL, methods=['GET'])
@login_required
def view_season(season_name, **kwargs):
    season = get_season(season_name)
    return render_template("view_season.html", season=season, **kwargs)


@app.route(urls.VIEW_SUBMIT_URL, methods=['GET'])
@login_required
def view_submit(season_name, **kwargs):
    return render_template("view_submit.html", season=season_name, **kwargs)
