import logging
import sys

from flask import current_app
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.security import login_required
from flask.ext.security import login_user
from flask.ext.security import MongoEngineUserDatastore
from flask.ext.security import Security
from flask.ext.social import login_failed
from flask.ext.social import Social
from flask.ext.social.datastore import MongoEngineConnectionDatastore
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.social.views import connect_handler

from feedback.api import create_session
from feedback.api import get_session
from feedback.environment import get_facebook_config
from feedback.environment import get_secret_key
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import parse_mongolab_uri
from feedback.models import Connection
from feedback.models import Role
from feedback.models import User
from feedback.urls import CREATE_SESSION_URL
from feedback.urls import HELLO_URL
from feedback.urls import VIEW_SESSION_URL
from feedback.urls import VIEW_SUBMIT_URL

from mongoengine import connect

from settings import MONGO_DB_NAME


app = Flask(__name__)
app.config['SOCIAL_FACEBOOK'] = get_facebook_config()
app.config['SECURITY_POST_LOGIN'] = '/profile'
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


app.security = Security(app, MongoEngineUserDatastore(db, User, Role))
app.social = Social(app, MongoEngineConnectionDatastore(db, Connection))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', content='Profile Page',
                           facebook_conn=app.social.facebook.get_connection())


@app.route(HELLO_URL)
def hello():
    return render_template("hello.html")


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


@login_failed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
    logging.debug('Social Login Failed via %s; &oauth_response=%s',
                  provider.name, oauth_response)

    connection_values = get_connection_values_from_oauth_response(
        provider, oauth_response)

    name = connection_values.get('full_name')
    connection_values['name'] = name
    del connection_values['full_name']
    email = connection_values.get('email')

    ds = current_app.security.datastore
    user = ds.create_user(name=name, email=email)
    ds.commit()
    connection_values['user_id'] = user.id
    connect_handler(connection_values, provider)
    login_user(user)
    db.commit()
    return render_template('success.html')

    logging.warning('full_name: %s, email: %s', name, email)
