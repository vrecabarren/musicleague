from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.notify import owner_all_users_voted_notification
from musicleague.notify import owner_user_voted_notification
from musicleague.notify import user_last_to_vote_notification
from musicleague.routes.decorators import login_required
from musicleague.submission_period import get_submission_period
from musicleague.vote import create_or_update_vote


VOTE_URL = '/l/<league_id>/<submission_period_id>/vote/'


@app.route(VOTE_URL, methods=['POST'])
@login_required
def vote(league_id, submission_period_id):

    votes = {uri: int(votes or 0) for uri, votes in request.form.iteritems()}

    submission_period = get_submission_period(submission_period_id)
    if submission_period and submission_period.accepting_votes:
        league = submission_period.league
        vote = create_or_update_vote(votes, submission_period, league, g.user)
        owner_user_voted_notification(league.owner, vote)

        voted_users = set([v.user for v in submission_period.votes])
        remaining = set(league.users) - voted_users

        if not remaining:
            owner_all_users_voted_notification(league.owner, submission_period)

        elif len(remaining) == 1:
            last_user = remaining = list(remaining)[0]
            user_last_to_vote_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))
