from flask import g
from flask import request
from rq.decorators import job

from musicleague import app
from musicleague import redis_conn
from musicleague import scheduler
from musicleague.league import get_league
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
ADMIN_JOBS_URL = '/admin/jobs/'
ADMIN_LEAGUES_URL = '/admin/leagues/'
ADMIN_TOOLS_URL = '/admin/tools/'
ADMIN_USERS_URL = '/admin/users/'


@app.route(ADMIN_URL)
@templated('admin/page.html')
@login_required
@admin_required
def admin():
    if request.args.get('pg') == '1':
        from musicleague.persistence.select import select_leagues_count
        from musicleague.persistence.select import select_rounds_count
        from musicleague.persistence.select import select_submissions_count
        from musicleague.persistence.select import select_users_count
        from musicleague.persistence.select import select_votes_count
        return {
            'user': g.user,
            'num_invited': InvitedUser.objects().count(),
            'num_leagues': select_leagues_count(),
            'num_rounds': select_rounds_count(),
            'num_submissions': select_submissions_count(),
            'num_tasks': len(scheduler.get_jobs()),
            'num_users': select_users_count(),
            'num_votes': select_votes_count()
        }

    return {
        'user': g.user,
        'num_invited': InvitedUser.objects().count(),
        'num_leagues': League.objects().count(),
        'num_rounds': SubmissionPeriod.objects().count(),
        'num_submissions': Submission.objects().count(),
        'num_tasks': len(scheduler.get_jobs()),
        'num_users': User.objects().count(),
        'num_votes': Vote.objects().count()
    }


@app.route(ADMIN_JOBS_URL)
@templated('admin/jobs/page.html')
@login_required
@admin_required
def admin_jobs():
    jobs = scheduler.get_jobs(with_times=True)
    jobs = sorted(jobs, key=(lambda (j, _): j.func_name))
    return {
        'user': g.user,
        'jobs': jobs
    }


@app.route(ADMIN_LEAGUES_URL)
@templated('admin/leagues/page.html')
@login_required
@admin_required
def admin_leagues():
    leagues = League.objects().all().order_by('preferences.name')

    if request.args.get('pg_update') == '1':
        from musicleague.persistence.insert import insert_league
        for league in leagues:
            insert_league_async.delay(str(league.id))

    return {
        'user': g.user,
        'leagues': leagues
    }


@job('default', connection=redis_conn)
def insert_league_async(league_id):
    league = get_league(league_id)
    from musicleague.persistence.insert import insert_league
    insert_league(league)


@app.route(ADMIN_TOOLS_URL)
@templated('admin/tools/page.html')
@login_required
@admin_required
def admin_tools():
    return {'user': g.user}


@app.route(ADMIN_USERS_URL)
@templated('admin/users/page.html')
@login_required
@admin_required
def admin_users():
    users = User.objects().all().order_by('name')

    if request.args.get('pg_update') == '1':
        from musicleague.persistence.insert import insert_user
        for user in users:
            insert_user(user)

    return {
        'user': g.user,
        'users': users
    }
