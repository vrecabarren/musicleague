import logging

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.routes.decorators import league_required
from feedback.routes.decorators import login_required
from feedback.routes.decorators import templated
from feedback.league import add_user
from feedback.league import create_league
from feedback.league import remove_user
from feedback.submission import get_submission


ADD_USER_FOR_LEAGUE_URL = '/l/<league_id>/users/add/'
CREATE_LEAGUE_URL = '/l/create/'
JOIN_LEAGUE_URL = '/l/<league_id>/join/'
REMOVE_LEAGUE_URL = '/l/<league_id>/remove/'
REMOVE_SUBMISSION_URL = '/l/<league_id>/<submission_period_id>/<submission_id>/remove/'  # noqa
REMOVE_USER_FOR_LEAGUE_URL = '/l/<league_id>/users/remove/<user_id>/'
SETTINGS_URL = '/l/<league_id>/settings/'
VIEW_LEAGUE_URL = '/l/<league_id>/'


@app.route(ADD_USER_FOR_LEAGUE_URL, methods=['POST'])
@login_required
@league_required
def add_user_for_league(league_id, **kwargs):
    league = kwargs.get('league')
    user_email = request.form.get('email')
    if league.has_owner(g.user):
        add_user(league, user_email)
    return redirect(url_for('view_league', league_id=league_id))


@app.route(REMOVE_USER_FOR_LEAGUE_URL, methods=['GET'])
@login_required
@league_required
def remove_user_for_league(league_id, user_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        remove_user(league, user_id)
    return redirect(url_for('view_league', league_id=league_id))


@app.route(CREATE_LEAGUE_URL, methods=['POST'])
@login_required
def post_create_league():
    try:
        league = create_league(g.user)
        return redirect(
            url_for(view_league.__name__, league_id=league.id))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(JOIN_LEAGUE_URL, methods=['GET'])
@login_required
@league_required
def join_league(league_id, **kwargs):
    league = kwargs.get('league')
    add_user(league, g.user.email)

    if 'invite_id' in request.args:
        invited_user = next((iu for iu in league.invited_users
                             if iu.id == request.args.get('invite_id')), None)
        if invited_user:
            invited_user.delete()

    return redirect(url_for('view_league', league_id=league_id))


@app.route(REMOVE_LEAGUE_URL)
@login_required
@league_required
def remove_league(league_id, **kwargs):
    league = kwargs.get('league')
    if league and league.has_owner(g.user):
        league.delete()
    return redirect(url_for('profile'))


@app.route(REMOVE_SUBMISSION_URL)
@login_required
def remove_submission(league_id, submission_period_id, submission_id,
                      **kwargs):
    league = kwargs.get('league')
    if league and league.has_owner(g.user):
        submission = get_submission(submission_id)
        submission.delete()
    return redirect(url_for('view_submission_period', league_id=league_id,
                            submission_period_id=submission_period_id))


@app.route(SETTINGS_URL, methods=['POST'])
@login_required
@league_required
def save_league_settings(league_id, **kwargs):
    league = kwargs.get('league')

    league.preferences.name = request.form.get('name')
    league.preferences.submission_reminder_time = request.form.get(
        'submission_reminder_time')
    league.preferences.track_count = request.form.get('track_count')
    league.preferences.point_bank_size = request.form.get('point_bank_size')
    league.preferences.locked = request.form.get('locked') == 'on'
    league.preferences.late_submissions = (
        request.form.get('late_submissions') == 'on')

    league.save()
    return redirect(request.referrer)


@app.route(VIEW_LEAGUE_URL, methods=['GET'])
@templated('league.html')
@login_required
@league_required
def view_league(league_id, **kwargs):
    league = kwargs.get('league')

    tracks_by_uri = {}
    my_submission = None
    my_vote = None

    if league.current_submission_period:
        tracks = league.current_submission_period.all_tracks
        if tracks:
            tracks = g.spotify.tracks(tracks).get('tracks')

        tracks_by_uri = {track.get('uri'): track for track in tracks if track}

        my_submission = next(
            (sub for sub in league.current_submission_period.submissions
             if sub.user == g.user), None)

        my_vote = next(
            (vote for vote in league.current_submission_period.votes
             if vote.user == g.user), None)

    return {
        'user': g.user,
        'league': kwargs.get('league'),
        'edit': request.args.get('edit'),
        'action': request.args.get('action'),
        'tracks_by_uri': tracks_by_uri,
        'my_submission': my_submission,
        'my_vote': my_vote
    }
