# flake8: noqa
from flask import g
from flask import redirect
from flask import url_for

from musicleague import app

from musicleague.routes.admin import admin
from musicleague.routes.admin import admin_leagues
from musicleague.routes.admin import admin_tools
from musicleague.routes.admin import admin_users
from musicleague.routes.admin.jobs import cancel_job
from musicleague.routes.admin.leagues import admin_remove_league
from musicleague.routes.admin.rounds import admin_generate_playlist
from musicleague.routes.admin.rounds import admin_remove_round
from musicleague.routes.admin.rounds import admin_reschedule_tasks
from musicleague.routes.admin.users import admin_make_user_admin
from musicleague.routes.auth import before_request
from musicleague.routes.auth import login
from musicleague.routes.auth import logout
from musicleague.routes.decorators import templated
from musicleague.routes.league import get_create_league
from musicleague.routes.league import view_league
from musicleague.routes.messenger import verify
from musicleague.routes.messenger import webhook
from musicleague.routes.spotify import create_spotify_playlist
from musicleague.routes.spotify import view_playlist
from musicleague.routes.submission_period import post_create_submission_period
from musicleague.routes.submission_period import save_submission_period_settings
from musicleague.routes.submission_period import view_submission_period
from musicleague.routes.submit import submit
from musicleague.routes.user import profile
from musicleague.routes.user import request_info
from musicleague.routes.user import view_user
from musicleague.routes.vote import vote

from musicleague.routes.api.v1.user import get_user

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
        }
