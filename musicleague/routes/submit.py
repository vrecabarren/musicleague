import httplib
import json
from timeit import default_timer as timer

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from musicleague import app
from musicleague.notify import owner_user_submitted_notification
from musicleague.notify import user_last_to_submit_notification
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission import create_or_update_submission
from musicleague.submission import get_my_submission
from musicleague.submission_period import get_submission_period
from musicleague.submission_period.tasks import complete_submission_process
from musicleague.validate import check_duplicate_albums
from musicleague.validate import check_duplicate_artists
from musicleague.validate import check_duplicate_tracks


SUBMIT_URL = '/l/<league_id>/<submission_period_id>/submit/'


@app.route(SUBMIT_URL, methods=['GET'])
@templated('submit/page.html')
@login_required
def view_submit(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        return redirect(url_for('view_league', league_id=league.id))

    if not (submission_period.accepting_submissions or
            submission_period.accepting_late_submissions):
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = get_my_submission(g.user, submission_period)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'my_submission': my_submission,
        'access_token': session['access_token'],
    }


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
def submit(league_id, submission_period_id):
    start = timer()
    submission_period = get_submission_period(submission_period_id)
    app.logger.info('Submission period loaded after %ss', timer() - start)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        app.logger.warning('No membership - redirecting after %ss', timer() - start)
        return "Not a member of this league", httplib.UNAUTHORIZED

    if (not submission_period.accepting_submissions and
            not submission_period.accepting_late_submissions):
        app.logger.warning('No longer accepting submissions - redirecting after %ss', timer() - start)
        return redirect(request.referrer)

    # Process submission
    league = submission_period.league

    try:
        tracks = json.loads(request.form.get('songs'))
    except Exception:
        app.logger.exception("Failed to load JSON from form with submit: %s",
                             request.form)
        return 'There was an error processing your submission', 500

    if None in tracks:
        return redirect(request.referrer)

    # Don't allow user to submit duplicate tracks
    if len(tracks) != len(set(tracks)):
        return redirect(request.referrer)

    # Don't include user's own previous submission when checking duplicates
    my_submission = get_my_submission(g.user, submission_period)
    their_tracks = []
    if submission_period.all_tracks:
        their_tracks = set(submission_period.all_tracks)
        if my_submission is not None:
            their_tracks.difference_update(set(my_submission.tracks))
        their_tracks = list(their_tracks)

    if their_tracks:
        s_tracks = tracks + their_tracks
        s_tracks = g.spotify.tracks(s_tracks).get('tracks')
        my_tracks = s_tracks[:len(tracks)]
        their_tracks = s_tracks[len(tracks):]

        # Don't allow user to submit already submitted track, album or artist
        duplicate_tracks = check_duplicate_tracks(my_tracks, their_tracks)
        duplicate_albums = check_duplicate_albums(my_tracks, their_tracks)
        duplicate_artists = check_duplicate_artists(my_tracks, their_tracks)
        if duplicate_tracks or duplicate_albums or duplicate_artists:
            return render_template(
                'submit/page.html',
                user=g.user, league=league, round=submission_period,
                previous_tracks=tracks,
                duplicate_songs=duplicate_tracks,
                duplicate_albums=duplicate_albums,
                duplicate_artists=duplicate_artists,
                access_token=session['access_token'])

    # Create a new submission on the round as current user
    app.logger.info('Creating/updating submission after %ss', timer() - start)
    submission = create_or_update_submission(
        tracks, submission_period, league, g.user)
    app.logger.info('Submission created/updated after %ss', timer() - start)

    # If someone besides owner is submitting, notify the owner
    if g.user.id != league.owner.id:
        app.logger.info('Notifying owner of user submission after %ss', timer() - start)
        owner_user_submitted_notification(submission)

    remaining = submission_period.have_not_submitted
    if not remaining:
        app.logger.info('Completing submission process after %ss', timer() - start)
        complete_submission_process.delay(submission_period.id)

    # Don't send submission reminder if this user is resubmitting. In this
    # case, the last user to submit will have already gotten a notification.
    elif submission.count < 2 and len(remaining) == 1:
        app.logger.info('Notifying final submitter after %ss', timer() - start)
        last_user = remaining[0]
        user_last_to_submit_notification(last_user, submission_period)

    app.logger.info('Submit request complete after %ss', timer() - start)
    return redirect(url_for('view_league', league_id=league_id))
