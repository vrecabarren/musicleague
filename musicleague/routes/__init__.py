# flake8: noqa
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.messenger import verify
from musicleague.messenger import webhook
from musicleague.models import League
from musicleague.models import Submission
from musicleague.models import User
from musicleague.routes.admin import admin
from musicleague.routes.admin import admin_leagues
from musicleague.routes.admin import admin_tools
from musicleague.routes.admin import admin_users
from musicleague.routes.admin.tools import clean_submission_periods
from musicleague.routes.admin.tools import clean_submissions
from musicleague.routes.auth import before_request
from musicleague.routes.auth import login
from musicleague.routes.auth import logout
from musicleague.routes.decorators import templated
from musicleague.routes.league import add_user_for_league
from musicleague.routes.league import get_create_league
from musicleague.routes.league import remove_league
from musicleague.routes.league import view_league
from musicleague.routes.spotify import create_spotify_playlist
from musicleague.routes.spotify import view_playlist
from musicleague.routes.submission_period import post_create_submission_period
from musicleague.routes.submission_period import remove_submission_period
from musicleague.routes.submission_period import save_submission_period_settings
from musicleague.routes.submission_period import view_submission_period
from musicleague.routes.submit import submit
from musicleague.routes.user import profile
from musicleague.routes.user import view_user
from musicleague.routes.vote import vote
from musicleague.spotify import get_spotify_oauth


HELLO_URL = '/'


@app.route(HELLO_URL)
@templated('hello.html')
def hello():
    # If user is logged in, always send to profile
    if g.user:
        return redirect(url_for('profile'))

    return {
        'user': g.user,
        'oauth_url': get_spotify_oauth().get_authorize_url(),
        'leagues': League.objects().count(),
        'submissions': Submission.objects().count(),
        'users': User.objects().count(),
        'action': request.args.get('action')
        }
