from flask import Flask
from flask import render_template
from flask import request

from feedback.api import create_session
from feedback.api import create_submission
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
    return render_template("view_session.html", session=session)


@app.route(VIEW_SESSION_URL, methods=['GET'])
def view_session(session_code):
    session = get_session(session_code)
    return render_template("view_session.html", session=session)


@app.route(VIEW_SUBMIT_URL, methods=['GET'])
def view_submit(session_code):
    return render_template("view_submit.html", session_code=session_code)


@app.route(VIEW_SUBMIT_URL, methods=['POST'])
def post_submit(session_code):
    return render_template("post_submit.html", session_code=session_code)


if __name__ == "__main__":
    app.run(debug=DEBUG)
