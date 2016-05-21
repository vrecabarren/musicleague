import logging

from flask import redirect
from flask import render_template
from flask import request
from flask import session as flask_session
from flask import url_for

from spotipy import Spotify

from feedback import app
from feedback.api import create_season
from feedback.api import get_season
from feedback.spotify import get_spotify_oauth
from feedback.user import get_user
from feedback.user import create_user
from feedback.views import urls
from feedback.views.decorators import login_required


@app.route(urls.HELLO_URL)
def hello():
    oauth = get_spotify_oauth()
    return render_template(
        "hello.html",
        user=(get_user(flask_session['current_user'])
              if 'current_user' in flask_session else None),
        oauth_url=oauth.get_authorize_url())


@app.route('/profile/')
@login_required
def profile():
    return 'logged in! here is your profile!'


@app.route(urls.LOGOUT_URL)
def logout():
    if 'current_user' in flask_session:
        flask_session.pop('current_user')
    return redirect(url_for(hello.__name__))


@app.route(urls.LOGIN_URL)
def login():
    if 'current_user' not in flask_session:
        url = request.url
        oauth = get_spotify_oauth()
        code = oauth.parse_response_code(url)
        if code:
            token_info = oauth.get_access_token(code)
            access_token = token_info['access_token']
            flask_session['access_token'] = access_token
            spotify = Spotify(access_token)
            user_id = spotify.current_user().get('id')
            user = get_user(user_id)
            user_email = spotify.current_user().get('email')
            user_name = spotify.current_user().get('display_name')

            if not user:
                user = create_user(user_id, user_name, user_email)

            else:
                user.id = user_id
                user.name = user_name
                user.email = user_email
                user.save()

            flask_session['current_user'] = user_id

    return redirect(url_for(hello.__name__))


@app.route(urls.CREATE_SEASON_URL, methods=['GET'])
def view_create_season():
    return render_template("create_season.html")


@app.route(urls.CREATE_SEASON_URL, methods=['POST'])
def post_create_season():
    try:
        season_name = request.form.get('season_name')
        season = create_season(season_name)
        return redirect(
            url_for(view_season.__name__, season_name=season.name))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(urls.VIEW_SEASON_URL, methods=['GET'])
def view_season(season_name):
    season = get_season(season_name)
    return render_template("view_season.html", season=season)


@app.route(urls.VIEW_SUBMIT_URL, methods=['GET'])
def view_submit(season_name):
    return render_template("view_submit.html", season=season_name)
