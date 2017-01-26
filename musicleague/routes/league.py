from datetime import datetime
from datetime import timedelta
import json
from pytz import utc

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.league import add_user
from musicleague.league import create_league
from musicleague.league import get_league
from musicleague.league import remove_league
from musicleague.league import remove_user
from musicleague.notify.flash import flash_error
from musicleague.routes.decorators import league_required
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission import get_submission
from musicleague.submission_period import create_submission_period
from musicleague.user import get_user


ADD_USER_FOR_LEAGUE_URL = '/l/<league_id>/users/add/'
CREATE_LEAGUE_URL = '/l/create/'
JOIN_LEAGUE_URL = '/l/<league_id>/join/'
MANAGE_LEAGUE_URL = '/l/<league_id>/manage/'
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
    return redirect(
        url_for('view_league', league_id=league_id, action='members'))


@app.route(REMOVE_USER_FOR_LEAGUE_URL, methods=['GET'])
@login_required
@league_required
def remove_user_for_league(league_id, user_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        remove_user(league, user_id)
    return redirect(url_for('view_league', league_id=league_id))


@app.route(CREATE_LEAGUE_URL, methods=['GET'])
@templated('league/create/page.html')
@login_required
def get_create_league():
    return {'user': g.user}


@app.route(CREATE_LEAGUE_URL, methods=['POST'])
@login_required
def post_create_league():
    name = request.form.get('league-name')
    num_tracks = request.form.get('tracks-submitted')
    bank_size = request.form.get('point-bank-size')

    user_ids = json.loads(request.form.get('added-members', []))
    members = [get_user(uid) for uid in user_ids]

    emails = json.loads(request.form.get('invited-members', []))

    rounds = json.loads(request.form.get('added-rounds', []))

    league = create_league(g.user, name=name, users=members)
    league.preferences.track_count = int(num_tracks)
    league.preferences.point_bank_size = int(bank_size)

    for email in emails:
        add_user(league, email, notify=True)

    for new_round in rounds:
        submission_due_date_str = new_round['submission-due-date-utc']
        submission_due_date = utc.localize(
            datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

        vote_due_date_str = new_round['voting-due-date-utc']
        vote_due_date = utc.localize(
            datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

        create_submission_period(
            league, new_round['name'], new_round['description'],
            submission_due_date, vote_due_date)

    league.save()

    app.logger.info('Creating league: %s', league.id)

    return redirect(url_for('view_league', league_id=league.id))


@app.route(MANAGE_LEAGUE_URL, methods=['GET'])
@templated('league/manage/page.html')
@login_required
def get_manage_league(league_id):
    league = get_league(league_id)
    if not league or not league.has_owner(g.user):
        app.logger.warning('Unauthorized user attempted access')
        flash_error('You must be owner of the league to access that page')
        return redirect(url_for('view_league', league_id=league_id))

    if league.submission_periods:
        lsp = league.submission_periods[-1]
        next_submission_due_date = lsp.submission_due_date + timedelta(weeks=1)
        next_vote_due_date = lsp.vote_due_date + timedelta(weeks=1)
    else:
        next_submission_due_date = datetime.utcnow() + timedelta(days=5)
        next_vote_due_date = datetime.utcnow() + timedelta(days=7)

    return {'user': g.user,
            'league': league,
            'next_submission_due_date': next_submission_due_date,
            'next_vote_due_date': next_vote_due_date}


@app.route(MANAGE_LEAGUE_URL, methods=['POST'])
@login_required
def post_manage_league(league_id):
    name = request.form.get('league-name')
    num_tracks = request.form.get('tracks-submitted')
    bank_size = request.form.get('point-bank-size')

    user_ids = json.loads(request.form.get('added-members', []))
    members = [get_user(uid) for uid in user_ids]

    emails = json.loads(request.form.get('invited-members', []))

    rounds = json.loads(request.form.get('added-rounds', []))

    league = get_league(league_id)
    league.preferences.name = name
    league.preferences.track_count = int(num_tracks)
    league.preferences.point_bank_size = int(bank_size)
    league.users.extend(members)

    for email in emails:
        add_user(league, email, notify=True)

    for new_round in rounds:
        submission_due_date_str = new_round['submission-due-date-utc']
        submission_due_date = utc.localize(
            datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

        vote_due_date_str = new_round['voting-due-date-utc']
        vote_due_date = utc.localize(
            datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

        create_submission_period(
            league, new_round['name'], new_round['description'],
            submission_due_date, vote_due_date)

    league.save()
    return redirect(url_for('view_league', league_id=league_id))


@app.route(JOIN_LEAGUE_URL, methods=['GET'])
@login_required
@league_required
def join_league(league_id, **kwargs):
    league = kwargs.get('league')
    add_user(league, g.user.email, notify=False)

    # If this URL is from an invitation email, delete the placeholder
    invite_id = request.args.get('invite_id')
    if invite_id:
        invited_user = next((iu for iu in league.invited_users
                             if str(iu.id) == invite_id), None)
        if invited_user:
            invited_user.delete()

    app.logger.info('User joined league: %s', league.id)

    return redirect(url_for('view_league', league_id=league_id))


@app.route(REMOVE_LEAGUE_URL)
@login_required
@league_required
def get_remove_league(league_id, **kwargs):
    league = kwargs.get('league')
    if league and league.has_owner(g.user):
        app.logger.info('Removing league: %s', league.id)
        league = remove_league(league_id, league=league)

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
    league.preferences.vote_reminder_time = request.form.get(
        'vote_reminder_time')
    league.preferences.track_count = request.form.get('track_count')
    league.preferences.point_bank_size = request.form.get('point_bank_size')
    league.preferences.locked = request.form.get('locked') == 'on'
    league.preferences.late_submissions = (
        request.form.get('late_submissions') == 'on')
    league.save()

    return redirect(request.referrer)


@app.route(VIEW_LEAGUE_URL, methods=['GET'])
@templated('league/view/page.html')
@login_required
@league_required
def view_league(league_id, **kwargs):
    league = kwargs.get('league')

    my_submission, my_vote = None, None
    if league.current_submission_period:
        submissions = league.current_submission_period.submissions
        my_submission = next(
            (s for s in submissions if s.user.id == g.user.id), None)

        votes = league.current_submission_period.votes
        my_vote = next(
            (v for v in votes if v.user.id == g.user.id), None)

    if league.submission_periods:
        lsp = league.submission_periods[-1]
        next_submission_due_date = lsp.submission_due_date + timedelta(weeks=1)
        next_vote_due_date = lsp.vote_due_date + timedelta(weeks=1)
    else:
        next_submission_due_date = datetime.utcnow() + timedelta(days=5)
        next_vote_due_date = datetime.utcnow() + timedelta(days=7)

    return {
        'user': g.user,
        'league': league,
        'my_submission': my_submission,
        'my_vote': my_vote,
        'next_submission_due_date': next_submission_due_date,
        'next_vote_due_date': next_vote_due_date
    }
