from flask import redirect
from flask import request

from musicleague import app
from musicleague.league import remove_league
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required


REMOVE_LEAGUE_URL = '/admin/leagues/<league_id>/remove/'


@app.route(REMOVE_LEAGUE_URL)
@login_required
@admin_required
def admin_remove_league(league_id):
    if not league_id:
        return

    remove_league(league_id)

    return redirect(request.referrer)
