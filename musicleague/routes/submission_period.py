from collections import defaultdict
from datetime import datetime
from pytz import utc

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.league import get_league
from musicleague.notify.flash import flash_success
from musicleague.routes.decorators import league_required
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission_period import create_submission_period
from musicleague.submission_period import get_submission_period
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period import update_submission_period


CREATE_SUBMISSION_PERIOD_URL = '/l/<league_id>/submission_period/create/'
MODIFY_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/modify/'  # noqa
REMOVE_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/remove/'  # noqa
SETTINGS_URL = '/l/<league_id>/<submission_period_id>/settings/'
VIEW_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/'


@app.route(CREATE_SUBMISSION_PERIOD_URL, methods=['POST'])
@login_required
@league_required
def post_create_submission_period(league_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        name = request.form.get('name')
        description = request.form.get('description')
        submission_period = create_submission_period(league, name, description)
        flash_success("Submission period <strong>{}</strong> created."
                      .format(submission_period.name))
    return redirect(url_for('view_league', league_id=league_id))


@app.route(REMOVE_SUBMISSION_PERIOD_URL)
@login_required
@league_required
def r_remove_submission_period(league_id, submission_period_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        submission_period = remove_submission_period(submission_period_id)
        flash_success("Submission period <strong>{}</strong> removed."
                      .format(submission_period.name))
    return redirect(url_for('view_league', league_id=league_id))


@app.route(SETTINGS_URL, methods=['POST'])
@login_required
@league_required
def save_submission_period_settings(league_id, submission_period_id,
                                    **kwargs):
    name = request.form.get('name')

    submission_due_date_str = request.form.get('submission_due_date_utc')
    submission_due_date = utc.localize(
        datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

    vote_due_date_str = request.form.get('voting_due_date_utc')
    vote_due_date = utc.localize(
        datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

    update_submission_period(submission_period_id, name, submission_due_date,
                             vote_due_date)

    return redirect(url_for('view_submission_period',
                            league_id=league_id,
                            submission_period_id=submission_period_id))


@app.route(VIEW_SUBMISSION_PERIOD_URL)
@templated('submission_period/submission_period.html')
@login_required
def view_submission_period(league_id, submission_period_id):
    if submission_period_id is None:
        raise Exception(request.referrer)
        return redirect(request.referrer)
    league = get_league(league_id)
    submission_period = get_submission_period(submission_period_id)
    tracks = submission_period.all_tracks
    if tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')

    submissions_by_uri = {}
    for submission in submission_period.submissions:
        for uri in submission.tracks:
            submissions_by_uri[uri] = submission

    total_points = 0
    points_by_uri = defaultdict(int)
    voters_by_uri = defaultdict(int)
    votes_by_uri = defaultdict(list)
    for vote in submission_period.votes:
        total_points += sum(vote.votes.values())
        for uri, points in vote.votes.iteritems():
            points_by_uri[uri] += points
            if points:
                voters_by_uri[uri] += 1
                votes_by_uri[uri].append(vote)
    votes_by_uri

    tracks_by_uri = {track.get('uri'): track for track in tracks}

    results = [
        {
            'track': tracks_by_uri.get(uri),
            'submission': submission,
            'votes': sorted(votes_by_uri[uri] or [],
                            key=lambda v: v.votes[uri], reverse=True),
            'points': points_by_uri.get(uri) or 0,
            'voters': voters_by_uri.get(uri) or 0
        } for uri, submission in submissions_by_uri.iteritems()]

    # Sort results by number of points and then by number of voters.
    # TODO Allow owner to modify order of rules applied in this sorting.
    results = sorted(results,
                     key=(lambda r: (r['points'], r['voters'])),
                     reverse=True)

    return {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'results': results,
        'total_points': total_points
    }
