import logging
import sys

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback.api import create_session
from feedback.api import get_session

from feedback.environment import get_port
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import parse_mongolab_uri

from feedback.urls import CREATE_SESSION_URL
from feedback.urls import HELLO_URL
from feedback.urls import REGISTER_URL
from feedback.urls import VIEW_SESSION_URL
from feedback.urls import VIEW_SUBMIT_URL

from mongoengine import connect

from settings import MONGO_DB_NAME


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))

if is_deployed():
    host, port, username, password, db = parse_mongolab_uri()
    connect(db, host=host, port=port, username=username, password=password)
    app.logger.setLevel(logging.ERROR)
else:
    connect(MONGO_DB_NAME)
    app.logger.setLevel(logging.DEBUG)


@app.route(HELLO_URL)
def hello():
    return render_template("hello.html")


@app.route(REGISTER_URL, methods=['GET'])
def view_register():
    return render_template("register.html")


@app.route(REGISTER_URL, methods=['POST'])
def post_register():
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


@app.route(VIEW_SUBMIT_URL, methods=['POST'])
def post_submit(session_name):
    return render_template("post_submit.html", session_name=session_name)


if __name__ == "__main__":
    debug = is_debug()
    port = get_port()
    app.run(host='0.0.0.0', port=port, debug=debug)
