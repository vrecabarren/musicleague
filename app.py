from os import environ

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback.api import create_session
from feedback.api import get_session

from feedback.urls import CREATE_SESSION_URL
from feedback.urls import HELLO_URL
from feedback.urls import VIEW_SESSION_URL
from feedback.urls import VIEW_SUBMIT_URL

from mongoengine import connect

from settings import DEBUG
from settings import MONGO_DB_NAME


app = Flask(__name__)
connect(MONGO_DB_NAME)


@app.route(HELLO_URL)
def hello():
    return render_template("hello.html")


@app.route(CREATE_SESSION_URL, methods=['GET'])
def view_create_session():
    return render_template("create_session.html")


@app.route(CREATE_SESSION_URL, methods=['POST'])
def post_create_session():
    session_name = request.form.get('session_name')
    session = create_session(session_name)
    return redirect(url_for(view_session.__name__, session_name=session.name))


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
    port = int(environ.get('PORT', 33507))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
