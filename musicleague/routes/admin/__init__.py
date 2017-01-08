from flask import g

from musicleague import app
from musicleague.models import InvitedUser
from musicleague.models import League
from musicleague.models import Submission
from musicleague.models import SubmissionPeriod
from musicleague.models import User
from musicleague.models import Vote
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated


ADMIN_URL = '/admin/'
ADMIN_LEAGUES_URL = '/admin/leagues/'
ADMIN_TOOLS_URL = '/admin/tools/'
ADMIN_USERS_URL = '/admin/users/'


@app.route(ADMIN_URL)
@templated('admin/page.html')
@login_required
@admin_required
def admin():
    return {
        'user': g.user,
        'num_invited': InvitedUser.objects().count(),
        'num_leagues': League.objects().count(),
        'num_rounds': SubmissionPeriod.objects().count(),
        'num_submissions': Submission.objects().count(),
        'num_users': User.objects().count(),
        'num_votes': Vote.objects().count()
    }


@app.route(ADMIN_LEAGUES_URL)
@templated('admin/leagues.html')
@login_required
@admin_required
def admin_leagues():
    leagues = League.objects().all().order_by('preferences.name')
    return {
        'user': g.user,
        'leagues': leagues
    }


@app.route(ADMIN_TOOLS_URL)
@templated('admin/tools.html')
@login_required
@admin_required
def admin_tools():
    return {}


@app.route(ADMIN_USERS_URL)
@templated('admin/users.html')
@login_required
@admin_required
def admin_users():
    users = User.objects().all().order_by('name')
    return {
        'user': g.user,
        'users': users
    }
