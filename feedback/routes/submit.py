import re

from flask import escape
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.routes.decorators import login_required
from feedback.routes.decorators import league_required
from feedback.submission import create_or_update_submission


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
        create_or_update_submission(tracks, submission_period, league, g.user)

    return redirect(url_for('view_league', league_id=league_id))
