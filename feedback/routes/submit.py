from flask import escape
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.routes.decorators import login_required
from feedback.routes.decorators import league_required
from feedback.submission import create_or_update_submission


SUBMIT_URL = '/l/<league_name>/submit/'


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
@league_required
def submit(league_name, **kwargs):
    league = kwargs.get('league')
    tracks = [
        escape(request.form.get('track' + str(i)))
        for i in range(1, league.preferences.track_count + 1)]

    submission_period = league.current_submission_period
    if submission_period and submission_period.is_current:
        create_or_update_submission(tracks, submission_period, league, g.user)

    return redirect(url_for('view_league', league_name=league_name))
