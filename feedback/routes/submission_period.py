from datetime import datetime

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.league import get_league
from feedback.routes.decorators import login_required
from feedback.routes.decorators import templated
from feedback.submission_period import create_submission_period
from feedback.submission_period import get_submission_period


CREATE_SUBMISSION_PERIOD_URL = '/l/<league_name>/submission_period/create/'
MODIFY_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/modify/'  # noqa
REMOVE_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/remove/'  # noqa
VIEW_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/'


@app.route(CREATE_SUBMISSION_PERIOD_URL)
@login_required
def post_create_submission_period(league_name):
    league = get_league(league_name)
    if league.owner == g.user:
        create_submission_period(league)
    return redirect(url_for('view_league', league_name=league_name))


@app.route(REMOVE_SUBMISSION_PERIOD_URL)
@login_required
def remove_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    if league and league.owner == g.user:
        submission_period = get_submission_period(submission_period_id)
        submission_period.delete()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(MODIFY_SUBMISSION_PERIOD_URL, methods=['POST'])
@login_required
def modify_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    if league and league.owner == g.user:
        new_name = request.form.get('new_name')
        new_due_date = request.form.get('new_due_date')
        if not submission_period_id or not new_name:
            return redirect(request.referrer)

        submission_period = get_submission_period(submission_period_id)
        submission_period.name = new_name
        submission_period.submission_due_date = datetime.strptime(
            new_due_date, '%m/%d/%y %I%p')
        submission_period.save()

    return redirect(url_for('view_league', league_name=league_name))


@app.route(VIEW_SUBMISSION_PERIOD_URL)
@templated('submission_period.html')
@login_required
def view_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    submission_period = get_submission_period(submission_period_id)

    all_tracks = []
    for submission in submission_period.submissions:
        all_tracks.extend(submission.tracks)

    tracks = g.spotify.tracks(all_tracks).get('tracks') if all_tracks else []

    return {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'tracks': tracks
        }
