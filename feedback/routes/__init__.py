# flake8: noqa
from flask import g
from flask import render_template

from feedback import app
from feedback.models import League
from feedback.models import Submission
from feedback.models import User
from feedback.routes import urls
from feedback.routes.auth import before_request
from feedback.routes.auth import login
from feedback.routes.auth import logout
from feedback.routes.league import add_user_for_league
from feedback.routes.league import post_create_league
from feedback.routes.league import post_create_submission_period
from feedback.routes.league import remove_league
from feedback.routes.league import remove_submission_period
from feedback.routes.league import rename_submission_period
from feedback.routes.league import view_submission_period
from feedback.routes.league import view_league
from feedback.routes.spotify import create_spotify_playlist
from feedback.routes.spotify import view_playlist
from feedback.routes.submit import post_confirm_submit
from feedback.routes.submit import post_submit
from feedback.routes.submit import view_confirm_submit
from feedback.routes.submit import view_submit
from feedback.routes.user import profile
from feedback.routes.user import view_user
from feedback.spotify import get_spotify_oauth


@app.route(urls.HELLO_URL)
def hello():
    kwargs = {
        'user': g.user,
        'oauth_url': get_spotify_oauth().get_authorize_url(),
        'leagues': League.objects().count(),
        'submissions': Submission.objects().count(),
        'users': User.objects().count()
    }
    return render_template("hello.html", **kwargs)
