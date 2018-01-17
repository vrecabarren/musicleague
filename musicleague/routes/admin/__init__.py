from flask import g
from flask import request

from musicleague import app
from musicleague import scheduler
from musicleague.league import get_league
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.insert import insert_league
from musicleague.persistence.models import League
from musicleague.persistence.models import User
from musicleague.persistence.select import select_invited_users_count
from musicleague.persistence.select import select_league
from musicleague.persistence.select import select_leagues_count
from musicleague.persistence.select import select_rounds_count
from musicleague.persistence.select import select_submissions_count
from musicleague.persistence.select import select_users_count
from musicleague.persistence.select import select_votes_count
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated


ADMIN_URL = '/admin/'
ADMIN_JOBS_URL = '/admin/jobs/'
ADMIN_LEAGUE_URL = '/admin/leagues/<league_id>/'
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
        'num_invited': select_invited_users_count(),
        'num_leagues': select_leagues_count(),
        'num_rounds': select_rounds_count(),
        'num_submissions': select_submissions_count(),
        'num_tasks': len(scheduler.get_jobs()),
        'num_users': select_users_count(),
        'num_votes': select_votes_count()
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
    if request.args.get('mdb'):
        from musicleague.models import League as MLeague
        leagues = MLeague.objects().all()
    else:
        stmt = 'SELECT id, created, name, owner_id, status FROM leagues ORDER BY name;'
        leagues = []
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(stmt)
                for league_tup in cur.fetchall():
                    leagues.append(
                        League(id=league_tup[0],
                               created=league_tup[1],
                               name=league_tup[2],
                               owner_id=league_tup[3],
                               status=league_tup[4]))

    return {
        'user': g.user,
        'leagues': leagues
    }


@app.route(ADMIN_LEAGUE_URL)
@templated('admin/leagues/league.html')
@login_required
@admin_required
def admin_league(league_id):
    league = select_league(league_id)

    return {
        'user': g.user,
        'league': league
    }


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
    stmt = "SELECT id, email, image_url, is_admin, joined, name, profile_bg FROM users ORDER BY name;"
    postgres_conn = get_postgres_conn()
    with postgres_conn:
        with postgres_conn.cursor() as cur:
            users = []
            cur.execute(stmt)
            for user_tup in cur.fetchall():
                user_id, email, image_url, is_admin, joined, name, profile_bg = user_tup
                users.append(
                    User(user_id, email, image_url, is_admin, joined, name, profile_bg))

    return {
        'user': g.user,
        'users': users
    }
