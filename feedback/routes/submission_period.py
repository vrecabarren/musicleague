from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback import app
from feedback.league import get_league
from feedback.routes.decorators import login_required
from feedback.submit import create_submission_period
from feedback.submit import get_submission_period


CREATE_SUBMISSION_PERIOD_URL = '/l/<league_name>/submission_period/create/'
REMOVE_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/remove/'  # noqa
RENAME_SUBMISSION_PERIOD_URL = '/l/<league_name>/<submission_period_id>/rename/'  # noqa
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


@app.route(RENAME_SUBMISSION_PERIOD_URL, methods=['POST'])
@login_required
def rename_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    if league and league.owner == g.user:
        new_name = request.form.get('new_name')
        if not submission_period_id or not new_name:
            return redirect(request.referrer)

        submission_period = get_submission_period(submission_period_id)
        submission_period.name = new_name
        submission_period.save()

    return redirect(url_for('view_league', league_name=league_name))


@app.route(VIEW_SUBMISSION_PERIOD_URL)
@login_required
def view_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    submission_period = get_submission_period(submission_period_id)

    all_tracks = []
    for submission in submission_period.submissions:
        all_tracks.extend(submission.tracks)

    tracks = g.spotify.tracks(all_tracks).get('tracks') if all_tracks else []

    kwargs = {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'tracks': tracks
    }

    return render_template("submission_period.html", **kwargs)
