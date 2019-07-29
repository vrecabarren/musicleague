from datetime import datetime
from pytz import utc

from flask import redirect
from flask import request

from musicleague import app
from musicleague.league import remove_league
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.select import select_league
from musicleague.persistence.update import update_round_status
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required


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
        if r.accepting_submissions and not r.have_not_submitted:
            update_round_status(r, RoundStatus.ACCEPTING_VOTES)
        elif (r.accepting_submissions and
              (r.submission_due_date < utc.localize(datetime.utcnow()))):
            update_round_status(r, RoundStatus.ACCEPTING_VOTES)
        elif r.accepting_votes and not r.have_not_voted:
            update_round_status(r, RoundStatus.COMPLETE)
        elif (r.accepting_votes and
              (r.vote_due_date < utc.localize(datetime.utcnow()))):
            update_round_status(r, RoundStatus.COMPLETE)

    return redirect(request.referrer)
