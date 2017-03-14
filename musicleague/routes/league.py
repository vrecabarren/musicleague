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
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import league_required
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.scoring.league import calculate_league_scoreboard
from musicleague.submission_period import create_submission_period
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period import update_submission_period
from musicleague.user import get_user


CREATE_LEAGUE_URL = '/l/create/'
JOIN_LEAGUE_URL = '/l/<league_id>/join/'
LEADERBOARD_URL = '/l/<league_id>/leaderboard/'
MANAGE_LEAGUE_URL = '/l/<league_id>/manage/'
REMOVE_LEAGUE_URL = '/l/<league_id>/remove/'
VIEW_LEAGUE_URL = '/l/<league_id>/'


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
    upvote_size = request.form.get('point-bank-size')
    downvote_size = request.form.get('downvote-bank-size')

    user_ids = json.loads(request.form.get('added-members', []))
    members = [get_user(uid) for uid in user_ids]

    emails = json.loads(request.form.get('invited-members', []))

    rounds = json.loads(request.form.get('added-rounds', []))

    league = create_league(g.user, name=name, users=members)
    league.preferences.track_count = int(num_tracks)
    league.preferences.point_bank_size = int(upvote_size)
    league.preferences.downvote_bank_size = int(downvote_size)

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

    return {'user': g.user,
            'league': league}


@app.route(MANAGE_LEAGUE_URL, methods=['POST'])
@login_required
def post_manage_league(league_id):
    name = request.form.get('league-name')
    num_tracks = request.form.get('tracks-submitted')
    upvote_size = request.form.get('point-bank-size')
    downvote_size = request.form.get('downvote-bank-size')

    user_ids = json.loads(request.form.get('added-members', []))
    added_members = [get_user(uid) for uid in user_ids]
    emails = json.loads(request.form.get('invited-members', []))
    deleted_members = json.loads(request.form.get('deleted-members', []))

    added_rounds = json.loads(request.form.get('added-rounds', []))
    edited_rounds = json.loads(request.form.get('edited-rounds', []))
    deleted_rounds = json.loads(request.form.get('deleted-rounds', []))

    league = get_league(league_id)
    league.preferences.name = name
    league.preferences.track_count = int(num_tracks)
    league.preferences.point_bank_size = int(upvote_size)
    league.preferences.downvote_bank_size = int(downvote_size)
    league.users.extend(added_members)

    for email in emails:
        add_user(league, email, notify=True)

    for deleted_member in deleted_members:
        remove_user(league, deleted_member)

    for added_round in added_rounds:
        submission_due_date_str = added_round['submission-due-date-utc']
        submission_due_date = utc.localize(
            datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

        vote_due_date_str = added_round['voting-due-date-utc']
        vote_due_date = utc.localize(
            datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

        create_submission_period(
            league, added_round['name'], added_round['description'],
            submission_due_date, vote_due_date)

    for edited_round in edited_rounds:
        submission_due_date_str = edited_round['submission-due-date-utc']
        submission_due_date = utc.localize(
            datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

        vote_due_date_str = edited_round['voting-due-date-utc']
        vote_due_date = utc.localize(
            datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

        update_submission_period(
            edited_round['id'], edited_round['name'],
            edited_round['description'], submission_due_date, vote_due_date)

    for deleted_round in deleted_rounds:
        try:
            remove_submission_period(deleted_round)
        except Exception as e:
            app.logger.warning('Error while attempting to delete round %s: %s',
                               deleted_round, str(e))

    league.reload('submission_periods')
    if league.scoreboard:
        league = calculate_league_scoreboard(league)

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


@app.route(VIEW_LEAGUE_URL + 'score/')
@login_required
@admin_required
@league_required
def score_league(league_id, **kwargs):
    league = kwargs.get('league')
    league = calculate_league_scoreboard(league)
    ret = {rank: [entry.user.id for entry in entries]
           for rank, entries in league.scoreboard.rankings.iteritems()}
    return json.dumps(ret), 200


@app.route(LEADERBOARD_URL)
@templated('leaderboard/page.html')
@login_required
@league_required
def view_leaderboard(league_id, **kwargs):
    league = kwargs.get('league')
    return {'user': g.user, 'league': league}
