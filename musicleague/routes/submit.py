import httplib
import json

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from musicleague import app
from musicleague.notify import owner_all_users_submitted_notification
from musicleague.notify import owner_user_submitted_notification
from musicleague.notify import user_last_to_submit_notification
from musicleague.notify.flash import flash_error
from musicleague.notify.flash import flash_success
from musicleague.notify.flash import flash_warning
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.spotify import create_or_update_playlist
from musicleague.submission import create_or_update_submission
from musicleague.submission_period import get_submission_period
from musicleague.submission_period.tasks.cancelers import cancel_playlist_creation  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_submission_reminders  # noqa


SUBMIT_URL = '/l/<league_id>/<submission_period_id>/submit/'


@app.route(SUBMIT_URL, methods=['GET'])
@templated('submit/page.html')
@login_required
def view_submit(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        flash_error("You must be a member of the league to submit")
        return redirect(url_for('view_league', league_id=league.id))

    if not (submission_period.accepting_submissions or
            submission_period.accepting_late_submissions):
        flash_error('Submissions are not currently being accepted')
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = next(
        (s for s in submission_period.submissions if s.user == g.user), None)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'my_submission': my_submission,
    }


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
def submit(league_id, submission_period_id):
    # TODO: Way too much happens in this function
    submission_period = get_submission_period(submission_period_id)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        return "Not a member of this league", httplib.UNAUTHORIZED

    if (not submission_period.accepting_submissions and
            not submission_period.accepting_late_submissions):
        flash_error("Submissions are no longer being accepted.")
        return redirect(request.referrer)

    # Process submission
    league = submission_period.league

    tracks = json.loads(request.form.get('songs'))

    app.logger.warning(tracks)

    if None in tracks:
        flash_error("Invalid submission. Please submit only tracks.")
        return redirect(request.referrer)

    # Don't allow user to submit duplicate tracks
    if len(tracks) != len(set(tracks)):
        flash_warning("Duplicate submissions not allowed.")
        return redirect(request.referrer)

    # Don't include user's own previous submission when checking duplicates
    my_submission = next((s for s in submission_period.submissions
                          if s.user.id == g.user.id), None)
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

        # Don't allow user to submit already submitted track or artist
        duplicate_tracks = check_duplicate_tracks(my_tracks, their_tracks)
        duplicate_artists = check_duplicate_artists(my_tracks, their_tracks)
        if duplicate_tracks or duplicate_artists:
            return render_template(
                'submit/page.html',
                user=g.user, league=league, round=submission_period,
                previous_tracks=tracks, duplicate_songs=duplicate_tracks,
                duplicate_artists=duplicate_artists)

    submission = create_or_update_submission(tracks, submission_period, league,
                                             g.user)

    flash_success("Your submissions have been recorded.")

    # If someone besides owner is submitting, notify the owner
    if g.user.id != league.owner.id:
        owner_user_submitted_notification(submission)

    submitted_users = set([s.user for s in submission_period.submissions])
    remaining = set(league.users) - submitted_users

    if not remaining:
        owner_all_users_submitted_notification(submission_period)
        create_or_update_playlist(submission_period)
        cancel_playlist_creation(submission_period)
        cancel_submission_reminders(submission_period)
        submission_period.save()

    elif len(remaining) == 1:
        last_user = list(remaining)[0]
        user_last_to_submit_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))


def check_duplicate_tracks(my_tracks, their_tracks):
    duplicate_tracks = []
    their_ids = [track['id'] for track in their_tracks]
    for my_track in my_tracks:
        if my_track['id'] in their_ids:
            duplicate_tracks.append(my_track['uri'])
    return duplicate_tracks


def check_duplicate_artists(my_tracks, their_tracks):
    duplicate_tracks = []
    their_ids = [track['artists'][0]['id'] for track in their_tracks]
    for my_track in my_tracks:
        if my_track['artists'][0]['id'] in their_ids:
            duplicate_tracks.append(my_track['uri'])
    return duplicate_tracks
