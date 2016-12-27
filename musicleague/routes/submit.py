import httplib

from flask import escape
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.notify import owner_all_users_submitted_notification
from musicleague.notify import owner_user_submitted_notification
from musicleague.notify import user_last_to_submit_notification
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.spotify import create_or_update_playlist
from musicleague.spotify import to_uri
from musicleague.submission import create_or_update_submission
from musicleague.submission_period import get_submission_period


SUBMIT_URL = '/l/<league_id>/<submission_period_id>/submit/'


@app.route(SUBMIT_URL, methods=['GET'])
@templated('submit/submit.html')
@login_required
def view_submit(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    my_submission = next(
        (s for s in submission_period.submissions if s.user == g.user), None)

    return {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'my_submission': my_submission,
    }


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
def submit(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        return "Not a member of this league", httplib.UNAUTHORIZED

    if submission_period and (submission_period.accepting_submissions or
                              submission_period.accepting_late_submissions):
        league = submission_period.league

        tracks = [
            to_uri(escape(request.form.get('track' + str(i))))
            for i in range(1, league.preferences.track_count + 1)]

        # Filter out any invalid URL or URI that we received
        tracks = filter(None, tracks)

        submission = create_or_update_submission(
            tracks, submission_period, league, g.user)

        if g.user.id != league.owner.id:
            owner_user_submitted_notification(submission)

        submitted_users = set([s.user for s in submission_period.submissions])
        remaining = set(league.users) - submitted_users

        if not remaining:
            owner_all_users_submitted_notification(submission_period)
            create_or_update_playlist(submission_period)

        elif len(remaining) == 1:
            last_user = list(remaining)[0]
            user_last_to_submit_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))
