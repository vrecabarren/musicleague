from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.models import League
from feedback.models import User
from feedback.routes.decorators import login_required
from feedback.routes.decorators import templated


ADMIN_URL = '/admin/'
ADMIN_LEAGUES_URL = '/admin/leagues/'
ADMIN_TOOLS_URL = '/admin/tools/'
ADMIN_USERS_URL = '/admin/users/'


@app.route(ADMIN_URL)
def admin():
    return redirect(url_for('admin_users'))


@app.route(ADMIN_LEAGUES_URL)
@templated('admin/leagues.html')
@login_required
def admin_leagues():
    if g.user.email == 'nathandanielcoleman@gmail.com':
        leagues = League.objects().all()
        return {
            'user': g.user,
            'leagues': leagues
        }
    return redirect(request.referrer)


@app.route(ADMIN_TOOLS_URL)
@templated('admin/tools.html')
@login_required
def admin_tools():
    if g.user.email == 'nathandanielcoleman@gmail.com':
        return {}
    return redirect(request.referrer)


@app.route(ADMIN_USERS_URL)
@templated('admin/users.html')
@login_required
def admin_users():
    if g.user.email == 'nathandanielcoleman@gmail.com':
        users = User.objects().all()
        return {
            'user': g.user,
            'users': users
        }
    return redirect(request.referrer)
