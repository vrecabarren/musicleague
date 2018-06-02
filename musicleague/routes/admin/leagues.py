from flask import redirect
from flask import request

from musicleague import app
from musicleague.league import remove_league
from musicleague.persistence.select import select_league
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required
from musicleague.submission_period import update_submission_period


REMOVE_LEAGUE_URL = '/admin/leagues/<league_id>/remove/'
STATE = '/admin/leagues/<league_id>/state/'


@app.route(REMOVE_LEAGUE_URL)
@login_required
@admin_required
def admin_remove_league(league_id):
    if not league_id:
        return

    remove_league(league_id)

    return redirect(request.referrer)


@app.route(STATE)
@login_required
@admin_required
def admin_league_state(league_id):
    if not league_id:
        return

    league = select_league(league_id)
    for r in league.submission_periods:
        update_submission_period(r.id, r.name, r.description, r.submission_due_date, r.vote_due_date, submission_period=r)

    return redirect(request.referrer)
