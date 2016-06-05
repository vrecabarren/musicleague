from flask import escape
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback import app
from feedback.models import Submission
from feedback.routes.decorators import login_required
from feedback.routes import urls
from feedback.league import get_league
from feedback.submit import create_or_update_submission
from feedback.submit import create_submission_period


CONFIRM_SUBMIT_URL = '/l/<league_name>/submit/<submission_id>/confirm/'
VIEW_SUBMIT_URL = '/l/<league_name>/submit/'


@app.route(urls.CONFIRM_SUBMIT_URL, methods=['GET'])
@login_required
def view_confirm_submit(league_name, submission_id):
    league = get_league(league_name)
    tracks = Submission.objects(id=submission_id).get().tracks
    spotify_tracks = [g.spotify.track(t_url) for t_url in tracks]
    kwargs = {
        'user': g.user,
        'league': league,
        'tracks': spotify_tracks
    }

    return render_template("confirm.html", **kwargs)


@app.route(urls.CONFIRM_SUBMIT_URL, methods=['POST'])
@login_required
def post_confirm_submit(league_name, submission_id):
    submission = Submission.objects(id=submission_id).get()
    submission.confirmed = True
    submission.save()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(urls.VIEW_SUBMIT_URL, methods=['GET'])
@login_required
def view_submit(league_name):
    league = get_league(league_name)
    kwargs = {
        'user': g.user,
        'league': league
    }
    return render_template("submit.html", **kwargs)


@app.route(urls.VIEW_SUBMIT_URL, methods=['POST'])
@login_required
def post_submit(league_name):
    league = get_league(league_name)
    tracks = [
        escape(request.form.get('track1')),
        escape(request.form.get('track2'))
    ]

    submission_period = league.current_submission_period
    if not submission_period:
        submission_period = create_submission_period(league)

    submission = create_or_update_submission(tracks, submission_period, g.user)

    return redirect(
        url_for('view_confirm_submit', league_name=league_name,
                submission_id=submission.id))
