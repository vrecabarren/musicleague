import httplib

from flask import escape
from flask import flash
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from musicleague import app
from musicleague.notify import owner_all_users_submitted_notification
from musicleague.notify import owner_user_submitted_notification
from musicleague.notify import user_last_to_submit_notification
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.spotify import create_or_update_playlist
from musicleague.spotify import to_uri
from musicleague.submission import create_or_update_submission
from musicleague.submission_period import get_submission_period


SUBMIT_URL = '/l/<league_id>/<submission_period_id>/submit/'


@app.route(SUBMIT_URL, methods=['GET'])
@templated('submit/submit.html')
@login_required
def view_submit(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        flash("You must be a member to submit.", "danger")
        return redirect(request.referrer)

    my_submission = next(
        (s for s in submission_period.submissions if s.user == g.user), None)

    return {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'my_submission': my_submission,
    }


@app.route(SUBMIT_URL, methods=['POST'])
@login_required
def submit(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        return "Not a member of this league", httplib.UNAUTHORIZED

    if (not submission_period.accepting_submissions and
            not submission_period.accepting_late_submissions):
        flash("Submissions are no longer being accepted.", "danger")
        return redirect(request.referrer)

    # Process submission
    league = submission_period.league

    tracks = [to_uri(escape(request.form.get('track' + str(i))))
              for i in range(1, league.preferences.track_count + 1)]

    if None in tracks:
        flash("Invalid submission. Please submit only tracks.", "danger")
        return redirect(request.referrer)
    tracks = filter(None, tracks)

    # Don't allow user to submit duplicate tracks
    if len(tracks) != len(set(tracks)):
        flash("Duplicate submissions not allowed.", "warning")
        return redirect(request.referrer)

    if tracks + submission_period.all_tracks:
        s_tracks = tracks + submission_period.all_tracks
        s_tracks = g.spotify.tracks(s_tracks).get('tracks')
        my_tracks = s_tracks[:len(tracks)]
        their_tracks = s_tracks[len(tracks):]

        # Don't allow user to submit already submitted track
        duplicate_track = check_duplicate_track(my_tracks, their_tracks)
        if duplicate_track is not None:
            track_name = duplicate_track['name']
            flash("{} has already been submitted. Please choose another "
                  "track to submit.".format(track_name), "danger")
            return redirect(request.referrer)

        # Warn user if submitting already submitted artist
        duplicate_track = check_duplicate_artist(my_tracks, their_tracks)
        if duplicate_track is not None:
            artist_name = duplicate_track['artists'][0]['name']
            flash("Your submission was accepted, but we thought you'd like to "
                  "know that another track by {} has already been submitted."
                  .format(artist_name), "warning")

    submission = create_or_update_submission(tracks, submission_period, league,
                                             g.user)

    flash("Your submissions have been recorded.", "success")

    # If someone besides owner is submitting, notify the owner
    if g.user.id != league.owner.id:
        owner_user_submitted_notification(submission)

    submitted_users = set([s.user for s in submission_period.submissions])
    remaining = set(league.users) - submitted_users

    if not remaining:
        owner_all_users_submitted_notification(submission_period)
        create_or_update_playlist(submission_period)

    elif len(remaining) == 1:
        last_user = list(remaining)[0]
        user_last_to_submit_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))


def check_duplicate_track(my_tracks, their_tracks):
    duplicate_track = None
    their_ids = [track['id'] for track in their_tracks]
    for my_track in my_tracks:
        if my_track['id'] in their_ids:
            duplicate_track = my_track
    return duplicate_track


def check_duplicate_artist(my_tracks, their_tracks):
    duplicate_track = None
    their_ids = [track['artists'][0]['id'] for track in their_tracks]
    for my_track in my_tracks:
        if my_track['artists'][0]['id'] in their_ids:
            duplicate_track = my_track
    return duplicate_track
