import httplib
import json
from timeit import default_timer as timer

from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from musicleague import app
from musicleague.notify import owner_user_voted_notification
from musicleague.notify import user_last_to_vote_notification
from musicleague.persistence.select import select_round
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission import get_my_submission
from musicleague.submission_period.tasks import complete_submission_period
from musicleague.vote import create_or_update_vote
from musicleague.vote import get_my_vote

VOTE_URL = '/l/<league_id>/<submission_period_id>/vote/'


@app.route(VOTE_URL, methods=['GET'])
@templated('vote/page.html')
@login_required
def view_vote(league_id, submission_period_id):
    submission_period = select_round(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        return redirect(url_for('view_league', league_id=league.id))

    if not submission_period.accepting_votes:
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = get_my_submission(g.user, submission_period)

    # If this user didn't submit for this round, don't allow them to vote
    if not my_submission:
        return redirect(url_for('view_league', league_id=league.id))

    my_vote = get_my_vote(g.user, submission_period)

    tracks = []
    if submission_period.all_tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')
    tracks_by_uri = {track.get('uri'): track for track in tracks if track}

    # Remove user's own submitted songs from tracks shown on page
    if my_submission:
        for uri in my_submission.tracks:
            tracks_by_uri.pop(uri, None)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'tracks_by_uri': tracks_by_uri,
        'my_vote': my_vote,
        'access_token': session['access_token'],
    }


@app.route(VOTE_URL, methods=['POST'])
@login_required
def vote(league_id, submission_period_id):
    start = timer()
    submission_period = select_round(submission_period_id)
    app.logger.info('Submission period loaded after %s s', timer() - start)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        app.logger.warning('No membership - redirecting after %s s', timer() - start)
        return "Not a member of this league", httplib.UNAUTHORIZED

    # If this user didn't submit for this round, don't allow them to vote
    if g.user not in submission_period.have_submitted:
        app.logger.warning('No submission - redirecting after %s s', timer() - start)
        return redirect(url_for('view_league', league_id=submission_period.league.id))

    # If this round is no longer accepting votes, redirect
    if not submission_period.accepting_votes:
        app.logger.warning('No longer accepting votes - redirecting after %s s', timer() - start)
        return redirect(request.referrer)

    try:
        app.logger.info('Loading votes from form submission after %s s', timer() - start)
        votes = json.loads(request.form.get('votes'))
        app.logger.info('Votes loaded after %s s', timer() - start)
    except Exception:
        app.logger.exception("Failed to load JSON from form with votes: %s",
                             request.form)
        return 'There was an error processing your votes', 500

    # Remove all unnecessary zero-values
    app.logger.info('Removing zero values after %s s', timer() - start)
    votes = {k: v for k, v in votes.iteritems() if v}
    app.logger.info('Removed zero values after %s s', timer() - start)

    # Process votes
    league = submission_period.league
    app.logger.info('Creating/updating vote after %s s', timer() - start)
    vote = create_or_update_vote(votes, submission_period, league, g.user)
    app.logger.info('Vote created/updated after %s s', timer() - start)

    # If someone besides owner is voting, notify the owner
    if g.user.id != league.owner.id:
        app.logger.info('Notifying owner of user vote after %s s', timer() - start)
        owner_user_voted_notification(vote)

    app.logger.info('Checking remaining voters after %s s', timer() - start)
    remaining = submission_period.have_not_voted
    if not remaining:
        app.logger.info('Completing submission period after %s s', timer() - start)
        complete_submission_period.delay(submission_period.id)

    elif vote.count < 2 and len(remaining) == 1:
        app.logger.info('Notifying final voter after %s s', timer() - start)
        last_user = remaining[0]
        user_last_to_vote_notification(last_user, submission_period)

    app.logger.info('Vote request complete after %s s', timer() - start)
    return redirect(url_for('view_league', league_id=league_id))
