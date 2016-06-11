from datetime import datetime
from datetime import timedelta
import logging

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback import app
from feedback import default_scheduler
from feedback.league import get_league
from feedback.routes.decorators import league_required
from feedback.routes.decorators import login_required
from feedback.submission_period import create_submission_period
from feedback.submission_period import get_submission_period
from feedback.submission_period import send_submission_reminders
from feedback.submission_period import update_submission_period


CREATE_SUBMISSION_PERIOD_URL = '/l/<league_name>/submission_period/create/'
MODIFY_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/modify/'  # noqa
REMOVE_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/remove/'  # noqa
VIEW_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/'


@app.route(CREATE_SUBMISSION_PERIOD_URL)
@login_required
@league_required
def post_create_submission_period(league_name, **kwargs):
    league = kwargs.get('league')
    if league.owner == g.user:
        submission_period = create_submission_period(league)
        notify_at = submission_period.submission_due_date - timedelta(hours=2)
        logging.warning('Inserting task to notify at %s. Currently: %s',
                        notify_at, datetime.utcnow())
        default_scheduler.enqueue_at(
            notify_at,
            send_submission_reminders,
            submission_period.id)
    return redirect(url_for('view_league', league_name=league_name))


@app.route(REMOVE_SUBMISSION_PERIOD_URL)
@login_required
@league_required
def remove_submission_period(league_name, submission_period_id, **kwargs):
    league = kwargs.get('league')
    if league.owner == g.user:
        submission_period = get_submission_period(submission_period_id)
        submission_period.delete()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(MODIFY_SUBMISSION_PERIOD_URL, methods=['POST'])
@login_required
@league_required
def modify_submission_period(league_name, submission_period_id, **kwargs):
    league = kwargs.get('league')
    if league.owner == g.user:
        new_name = request.form.get('new_name')
        new_due_date_str = request.form.get('new_due_date')
        new_due_date = datetime.strptime(new_due_date_str, '%m/%d/%y %I%p')
        update_submission_period(submission_period_id, new_name, new_due_date)

    return redirect(url_for('view_league', league_name=league_name))


@app.route(VIEW_SUBMISSION_PERIOD_URL)
@login_required
def view_submission_period(league_name, submission_period_id):
    if submission_period_id is None:
        raise Exception(request.referrer)
        return redirect(request.referrer)
    league = get_league(league_name)
    submission_period = get_submission_period(submission_period_id)
    tracks = submission_period.all_tracks
    if tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')

    return render_template(
        'submission_period.html',
        user=g.user, league=league, submission_period=submission_period,
        tracks=tracks)
