from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.routes.decorators import login_required
from feedback.routes.decorators import league_required
from feedback.vote import create_or_update_vote


VOTE_URL = '/l/<league_id>/vote/'


@app.route(VOTE_URL, methods=['POST'])
@login_required
@league_required
def vote(league_id, **kwargs):
    league = kwargs.get('league')

    votes = {uri: int(votes) for uri, votes in request.form.iteritems()}

    submission_period = league.current_submission_period
    if submission_period and submission_period.is_current:
        create_or_update_vote(votes, submission_period, league, g.user)

    return redirect(url_for('view_league', league_id=league_id))
