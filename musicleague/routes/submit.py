import re

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
from musicleague.submission import create_or_update_submission


SUBMIT_URL = '/l/<league_id>/submit/'


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
@league_required
def submit(league_id, **kwargs):
    league = kwargs.get('league')

    def to_uri(url_or_uri):
        uri_regex = 'spotify:track:[A-Za-z0-9]{22}'
        url_regex = ('(?:http|https):\/\/(?:open|play)\.spotify\.com\/track\/'
                     '(?P<id>[A-Za-z0-9]{22})')

        # If valid URI, no need to modify
        if re.match(uri_regex, url_or_uri):
            return url_or_uri

        # Has to be a valid track URL to mutate. If not, return None.
        if not re.match(url_regex, url_or_uri):
            return None

        return 'spotify:track:%s' % re.match(url_regex, url_or_uri).group('id')

    tracks = [
        to_uri(escape(request.form.get('track' + str(i))))
        for i in range(1, league.preferences.track_count + 1)]

    # Filter out any invalid URL or URI that we received
    tracks = filter(None, tracks)

    submission_period = league.current_submission_period
    if submission_period and submission_period.is_current:
        submission = create_or_update_submission(
            tracks, submission_period, league, g.user)

        owner_user_submitted_notification(league.owner, submission)

        submitted_users = set([s.user for s in submission_period.submissions])
        remaining = set(league.users) - submitted_users
        if not remaining or remaining == set([league.owner]):
            owner_all_users_submitted_notification(
                league.owner, submission_period)

        if len(remaining) == 1:
            last_user = list(remaining)[0]
            user_last_to_submit_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))
