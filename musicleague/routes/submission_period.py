from datetime import datetime
from pytz import utc

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.league import get_league
from musicleague.notify.flash import flash_error
from musicleague.notify.flash import flash_success
from musicleague.notify.flash import flash_warning
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import league_required
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.scoring.league import calculate_league_scoreboard
from musicleague.scoring.round import calculate_round_scoreboard
from musicleague.submission_period import create_submission_period
from musicleague.submission_period import get_submission_period
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period import update_submission_period


CREATE_SUBMISSION_PERIOD_URL = '/l/<league_id>/submission_period/create/'
MODIFY_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/modify/'
REMOVE_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/remove/'
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
        if not description or not description.strip():
            description = None

        submission_due_date_str = request.form.get('submission_due_date_utc')
        submission_due_date = utc.localize(
            datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

        vote_due_date_str = request.form.get('voting_due_date_utc')
        vote_due_date = utc.localize(
            datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

        submission_period = create_submission_period(
            league, name, description, submission_due_date, vote_due_date)

        flash_success("<strong>{}</strong> created."
                      .format(submission_period.name))

    return redirect(url_for('view_league', league_id=league_id))


@app.route(REMOVE_SUBMISSION_PERIOD_URL)
@login_required
@league_required
def r_remove_submission_period(league_id, submission_period_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        submission_period = remove_submission_period(submission_period_id)
        flash_success("<strong>{}</strong> removed."
                      .format(submission_period.name))
    return redirect(url_for('view_league', league_id=league_id))


@app.route(SETTINGS_URL, methods=['POST'])
@login_required
@league_required
def save_submission_period_settings(league_id, submission_period_id,
                                    **kwargs):
    name = request.form.get('name')

    description = request.form.get('description')
    description = description.strip()

    submission_due_date_str = request.form.get('submission_due_date_utc')
    submission_due_date = utc.localize(
        datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

    vote_due_date_str = request.form.get('voting_due_date_utc')
    vote_due_date = utc.localize(
        datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

    update_submission_period(submission_period_id, name, description,
                             submission_due_date, vote_due_date)

    return redirect(url_for('view_submission_period',
                            league_id=league_id,
                            submission_period_id=submission_period_id))


@app.route(VIEW_SUBMISSION_PERIOD_URL)
@templated('results/page.html')
@login_required
def view_submission_period(league_id, submission_period_id):
    league = get_league(league_id)
    submission_period = get_submission_period(submission_period_id)
    if not submission_period:
        flash_error('Round not found')
        return redirect(url_for('view_league', league_id=league.id))

    is_owner = league.has_owner(g.user)
    is_admin = g.user.is_admin
    can_view = submission_period.is_complete or is_owner or is_admin
    if not can_view:
        flash_warning('You do not have access to this page right now')
        return redirect(url_for('view_league', league_id=league.id))

    # Get Spotify track objects
    tracks = submission_period.all_tracks
    if tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')
    tracks_by_uri = {track['uri']: track for track in tracks if track}

    # Make sure this round has an up-to-date scoreboard
    if not submission_period.scoreboard or not submission_period.is_complete:
        submission_period = calculate_round_scoreboard(submission_period)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'tracks_by_uri': tracks_by_uri
    }


@app.route(VIEW_SUBMISSION_PERIOD_URL + 'score/')
@login_required
@admin_required
def score_round(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    submission_period = calculate_round_scoreboard(submission_period)
    calculate_league_scoreboard(submission_period.league)
    return str(len(submission_period.scoreboard)), 200
