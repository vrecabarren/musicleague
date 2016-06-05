from flask import escape
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.models import Submission
from feedback.models import SubmissionPeriod
from feedback.routes.decorators import login_required
from feedback.routes.decorators import league_required
from feedback.routes.decorators import templated
from feedback.submit import create_or_update_submission


CONFIRM_SUBMIT_URL = '/l/<league_name>/<submission_id>/confirm/'
VIEW_SUBMIT_URL = '/l/<league_name>/<submission_period_id>/submit/'


@app.route(CONFIRM_SUBMIT_URL, methods=['GET'])
@templated('confirm.html')
@login_required
@league_required
def view_confirm_submit(league_name, submission_id, **kwargs):
    tracks = Submission.objects(id=submission_id).get().tracks
    spotify_tracks = [g.spotify.track(t_url) for t_url in tracks]
    return {'user': g.user,
            'league': kwargs.get('league'),
            'tracks': spotify_tracks}


@app.route(CONFIRM_SUBMIT_URL, methods=['POST'])
@login_required
def post_confirm_submit(league_name, submission_id):
    submission = Submission.objects(id=submission_id).get()
    submission.confirmed = True
    submission.save()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(VIEW_SUBMIT_URL, methods=['GET'])
@templated('submit.html')
@login_required
@league_required
def view_submit(league_name, submission_period_id, **kwargs):
    return {'user': g.user, 'league': kwargs.get('league')}


@app.route(VIEW_SUBMIT_URL, methods=['POST'])
@login_required
def post_submit(league_name, submission_period_id, **kwargs):
    tracks = [
        escape(request.form.get('track1')),
        escape(request.form.get('track2'))
    ]

    submission_period = SubmissionPeriod.objects(id=submission_period_id).get()
    if submission_period and submission_period.is_current:
        submission = create_or_update_submission(
            tracks, submission_period, g.user)
        return redirect(
            url_for('view_confirm_submit',
                    league_name=league_name, submission_id=submission.id))
    return redirect(url_for('view_league', league_name=league_name))
