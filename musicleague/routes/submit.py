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
from musicleague.routes.decorators import league_required
from musicleague.spotify import create_or_update_playlist
from musicleague.spotify import to_uri
from musicleague.submission import create_or_update_submission


SUBMIT_URL = '/l/<league_id>/submit/'


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
@league_required
def submit(league_id, **kwargs):
    league = kwargs.get('league')

    submission_period = league.current_submission_period
    if submission_period and (submission_period.accepting_submissions or
                              submission_period.accepting_late_submissions):

        tracks = [
            to_uri(escape(request.form.get('track' + str(i))))
            for i in range(1, league.preferences.track_count + 1)]

        # Filter out any invalid URL or URI that we received
        tracks = filter(None, tracks)

        submission = create_or_update_submission(tracks, submission_period,
                                                 league, g.user)

        if g.user.id != league.owner.id:
            owner_user_submitted_notification(league.owner, submission)

        submitted_users = set([s.user for s in submission_period.submissions])
        remaining = set(league.users) - submitted_users

        if not remaining:
            owner_all_users_submitted_notification(
                league.owner, submission_period)
            create_or_update_playlist(submission_period)

        elif len(remaining) == 1:
            last_user = list(remaining)[0]
            user_last_to_submit_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))
