import logging
import sys

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session as flask_session
from flask import url_for

from feedback.api import create_session
from feedback.api import get_session
from feedback.environment import get_secret_key
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import parse_mongolab_uri
from feedback.spotify import get_spotify_oauth
from feedback.urls import CREATE_SESSION_URL
from feedback.urls import HELLO_URL
from feedback.urls import LOGIN_URL
from feedback.urls import LOGOUT_URL
from feedback.urls import VIEW_SESSION_URL
from feedback.urls import VIEW_SUBMIT_URL
from feedback.user import get_user
from feedback.user import create_user

from mongoengine import connect

from settings import MONGO_DB_NAME

from spotipy import Spotify


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.secret_key = get_secret_key()

if is_deployed():
    host, port, username, password, db = parse_mongolab_uri()
    db = connect(db, host=host, port=port, username=username,
                 password=password)
    app.logger.setLevel(logging.DEBUG if is_debug() else logging.ERROR)
else:
    db = connect(MONGO_DB_NAME)
    app.logger.setLevel(logging.DEBUG)


@app.route(HELLO_URL)
def hello():
    oauth = get_spotify_oauth()
    return render_template(
        "hello.html",
        user=(get_user(flask_session['current_user'])
              if 'current_user' in flask_session else None),
        oauth_url=oauth.get_authorize_url())


@app.route(LOGOUT_URL)
def logout():
    if 'current_user' in flask_session:
        flask_session.pop('current_user')
    return redirect(url_for(hello.__name__))


@app.route(LOGIN_URL)
def spotify_oauth():
    url = request.url
    oauth = get_spotify_oauth()
    code = oauth.parse_response_code(url)
    if code:
        token_info = oauth.get_access_token(code)
        access_token = token_info['access_token']
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


@app.route(CREATE_SESSION_URL, methods=['GET'])
def view_create_session():
    return render_template("create_session.html")


@app.route(CREATE_SESSION_URL, methods=['POST'])
def post_create_session():
    try:
        session_name = request.form.get('session_name')
        session = create_session(session_name)
        return redirect(
            url_for(view_session.__name__, session_name=session.name))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(VIEW_SESSION_URL, methods=['GET'])
def view_session(session_name):
    session = get_session(session_name)
    return render_template("view_session.html", session=session)


@app.route(VIEW_SUBMIT_URL, methods=['GET'])
def view_submit(session_name):
    return render_template("view_submit.html", session_name=session_name)
