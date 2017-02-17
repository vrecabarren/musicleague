import httplib

from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.environment import is_production
from musicleague.notify import owner_all_users_voted_notification
from musicleague.notify import owner_user_voted_notification
from musicleague.notify import user_last_to_vote_notification
from musicleague.notify.flash import flash_error
from musicleague.notify.flash import flash_success
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission_period import get_submission_period
from musicleague.submission_period.tasks.cancelers import cancel_vote_reminders
from musicleague.vote import create_or_update_vote


VOTE_URL = '/l/<league_id>/<submission_period_id>/vote/'


@app.route(VOTE_URL, methods=['GET'])
@templated('vote/page.html')
@login_required
def view_vote(league_id, submission_period_id):
    if not is_production():
        return redirect(
            url_for('new_view_vote', league_id=league_id,
                    submission_period_id=submission_period_id))

    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        flash_error("You must be a member of the league to vote")
        return redirect(url_for('view_league', league_id=league.id))

    if not submission_period.accepting_votes:
        flash_error('Votes are not currently being accepted')
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = next(
        (s for s in submission_period.submissions if s.user == g.user), None)
    my_vote = next(
        (v for v in submission_period.votes if v.user == g.user), None)

    tracks = []
    if submission_period.all_tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')
    tracks_by_uri = {track.get('uri'): track for track in tracks if track}

    if my_submission:
        for uri in my_submission.tracks:
            tracks_by_uri.pop(uri, None)

    return {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'tracks_by_uri': tracks_by_uri,
        'my_vote': my_vote
    }


@app.route(VOTE_URL + 'new/', methods=['GET'])
@templated('vote/new/page.html')
@login_required
def new_view_vote(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        flash_error("You must be a member of the league to vote")
        return redirect(url_for('view_league', league_id=league.id))

    if not submission_period.accepting_votes:
        flash_error('Votes are not currently being accepted')
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = next(
        (s for s in submission_period.submissions if s.user == g.user), None)
    my_vote = next(
        (v for v in submission_period.votes if v.user == g.user), None)

    tracks = []
    if submission_period.all_tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')
    tracks_by_uri = {track.get('uri'): track for track in tracks if track}

    if my_submission:
        for uri in my_submission.tracks:
            tracks_by_uri.pop(uri, None)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'tracks_by_uri': tracks_by_uri,
        'my_vote': my_vote
    }


@app.route(VOTE_URL, methods=['POST'])
@login_required
def vote(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        return "Not a member of this league", httplib.UNAUTHORIZED

    votes = {uri: int(votes or 0) for uri, votes in request.form.iteritems()}

    if not submission_period.accepting_votes:
        flash_error("Votes are no longer being accepted.")
        return redirect(request.referrer)

    # Process votes
    league = submission_period.league
    vote = create_or_update_vote(votes, submission_period, league, g.user)

    flash_success("Your votes have been recorded.")

    # If someone besides owner is submitting, notify the owner
    if g.user.id != league.owner.id:
        owner_user_voted_notification(vote)

    voted_users = set([v.user for v in submission_period.votes])
    remaining = set(league.users) - voted_users

    if not remaining:
        owner_all_users_voted_notification(submission_period)
        cancel_vote_reminders(submission_period)
        submission_period.save()

    elif len(remaining) == 1:
        last_user = remaining = list(remaining)[0]
        user_last_to_vote_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))
