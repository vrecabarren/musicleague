import httplib
import json

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from musicleague import app
from musicleague.analytics import track_user_proceeded_duplicate_artist
from musicleague.analytics import track_user_proceeded_repeat_submission
from musicleague.analytics import track_user_submitted
from musicleague.analytics import track_user_submitted_duplicate_artist
from musicleague.analytics import track_user_submitted_duplicate_song
from musicleague.analytics import track_user_submitted_repeat_submission
from musicleague.notify import owner_user_submitted_notification
from musicleague.notify import user_last_to_submit_notification
from musicleague.persistence.select import select_league
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission import create_or_update_submission
from musicleague.submission import get_my_submission
from musicleague.submission_period.tasks import complete_submission_process
from musicleague.validate import check_duplicate_artists
from musicleague.validate import check_duplicate_tracks
from musicleague.validate import check_repeat_submissions


SUBMIT_URL = '/l/<league_id>/<submission_period_id>/submit/'
SUBMIT2_URL = SUBMIT_URL + '2/'

@app.route(SUBMIT2_URL, methods=['GET'])
@templated('submit/page2.html')
@login_required
def view_submit_2(league_id, submission_period_id):
    league = select_league(league_id)
    submission_period = next((sp for sp in league.submission_periods
                              if sp.id == submission_period_id), None)
    if not league.has_user(g.user):
        return redirect(url_for('view_league', league_id=league.id))

    if not submission_period.accepting_submissions:
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = get_my_submission(g.user, submission_period)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'my_submission': my_submission,
        'access_token': session['access_token'],
    }

@app.route(SUBMIT_URL, methods=['GET'])
@templated('submit/page.html')
@login_required
def view_submit(league_id, submission_period_id):
    league = select_league(league_id)
    submission_period = next((sp for sp in league.submission_periods
                              if sp.id == submission_period_id), None)
    if not league.has_user(g.user):
        return redirect(url_for('view_league', league_id=league.id))

    if not submission_period.accepting_submissions:
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
    try:
        league = select_league(league_id)
        submission_period = next((sp for sp in league.submission_periods
                                  if sp.id == submission_period_id), None)
        if not league or not submission_period:
            return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

        if not league.has_user(g.user):
            return "Not a member of this league", httplib.UNAUTHORIZED

        if not submission_period.accepting_submissions:
            return redirect(request.referrer)

        try:
            tracks = json.loads(request.form.get('songs'))
            warned_artists = json.loads(request.form.get('duplicate-artists') or '[]')
            warned_repeats = json.loads(request.form.get('repeat-submissions') or '[]')
        except Exception:
            app.logger.exception("Failed to load JSON from form with submit: %s",
                                 request.form)
            return 'There was an error processing your submission', 500

        if len(filter(None, tracks)) != len(tracks):
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

        s_tracks = tracks + their_tracks
        s_tracks = g.spotify.tracks(s_tracks).get('tracks')

        my_tracks, their_tracks = s_tracks, []
        if len(s_tracks) > len(tracks):
            my_tracks = s_tracks[:len(tracks)]
            their_tracks = s_tracks[len(tracks):]

        # Don't allow user to submit already submitted track, album or artist
        duplicate_tracks = check_duplicate_tracks(my_tracks, their_tracks)
        duplicate_artists = check_duplicate_artists(my_tracks, their_tracks)
        repeat_submissions = check_repeat_submissions(g.user.id, tracks, league_id)

        proceeding_dups = set(warned_artists).intersection(set(duplicate_artists))
        if proceeding_dups:
            duplicate_artists = list(set(duplicate_artists) - set(warned_artists))
            track_user_proceeded_duplicate_artist(g.user.id, submission_period, list(proceeding_dups))

        proceeding_repeats = set(warned_repeats).intersection(set(repeat_submissions))
        if proceeding_repeats:
            repeat_submissions = list(set(repeat_submissions) - set(warned_repeats))
            track_user_proceeded_repeat_submission(g.user.id, submission_period, list(proceeding_repeats))

        if duplicate_tracks or duplicate_artists or repeat_submissions:

            if duplicate_tracks:
                track_user_submitted_duplicate_song(g.user.id, submission_period, duplicate_tracks)
            # elif duplicate_albums:
            #     track_user_submitted_duplicate_album(g.user.id, submission_period, duplicate_albums)
            elif duplicate_artists:
                track_user_submitted_duplicate_artist(g.user.id, submission_period, duplicate_artists)
            elif repeat_submissions:
                track_user_submitted_repeat_submission(g.user.id, submission_period, repeat_submissions)

            return render_template(
                'submit/page.html',
                user=g.user, league=league, round=submission_period,
                previous_tracks=tracks,
                duplicate_songs=duplicate_tracks,
                duplicate_albums=[],
                duplicate_artists=duplicate_artists,
                repeat_submissions=repeat_submissions,
                access_token=session['access_token'])

        # Create a new submission on the round as current user
        submission = create_or_update_submission(
            tracks, submission_period, league, g.user)

        # If someone besides owner is submitting, notify the owner
        if not league.has_owner(g.user):
            owner_user_submitted_notification(submission)

        remaining = submission_period.have_not_submitted
        if not remaining:
            app.logger.warning('No remaining members to submit', extra={'round': submission_period_id})
            # If this is not the first round, roll forward
            if len(league.submission_periods) > 1:
                app.logger.warning('This is not the only round', extra={'round': submission_period_id})
                if league.submission_periods[0].id != submission_period_id:
                    # This makes the request a little heavy for the final submitter,
                    # but asyncing means the submitter gets a playlist button but no playlist.
                    app.logger.warning('This is not the first round, completing the submission process', extra={'round': submission_period_id})
                    complete_submission_process(submission_period.id)

        # Don't send submission reminder if this user is resubmitting. In this
        # case, the last user to submit will have already gotten a notification.
        elif submission.count < 2 and len(remaining) == 1:
            last_user = remaining[0]
            user_last_to_submit_notification(last_user, submission_period)

        track_user_submitted(g.user.id, submission_period)

        return redirect(url_for('view_league', league_id=league_id))

    except Exception:
        app.logger.exception(
            'Failed to process submissions',
            extra={'user': g.user.id, 'league': league_id, 'round': submission_period_id,
                   'form_values': request.form})

        return 'There was an error processing your submission', 500
