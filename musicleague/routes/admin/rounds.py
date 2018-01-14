from flask import redirect
from flask import request

from musicleague import app
from musicleague.persistence.select import select_league
from musicleague.persistence.select import select_league_id_for_round
from musicleague.persistence.select import select_round
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required
from musicleague.spotify import create_or_update_playlist
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period.tasks.schedulers import schedule_playlist_creation  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_round_completion  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_submission_reminders  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_vote_reminders  # noqa


GENERATE_PLAYLIST = '/admin/rounds/<submission_period_id>/playlist/'
REMOVE_ROUND_URL = '/admin/rounds/<submission_period_id>/remove/'
RESCHEDULE_TASKS_URL = '/admin/rounds/<submission_period_id>/reschedule/'


@app.route(GENERATE_PLAYLIST)
@login_required
@admin_required
def admin_generate_playlist(submission_period_id):
    if not submission_period_id:
        return

    league_id = select_league_id_for_round(submission_period_id)
    league = select_league(league_id, exclude_properties=['votes', 'scoreboard', 'invited_users'])
    submission_period = next((r for r in league.submission_periods
                              if r.id == submission_period_id), None)

    if not submission_period:
        return

    create_or_update_playlist(submission_period)

    return redirect(request.referrer)


@app.route(REMOVE_ROUND_URL)
@login_required
@admin_required
def admin_remove_round(submission_period_id):
    if not submission_period_id:
        return

    remove_submission_period(submission_period_id)

    return redirect(request.referrer)


@app.route(RESCHEDULE_TASKS_URL)
@login_required
@admin_required
def admin_reschedule_tasks(submission_period_id):
    if not submission_period_id:
        return

    submission_period = select_round(submission_period_id)
    if not submission_period:
        return

    schedule_playlist_creation(submission_period)
    schedule_round_completion(submission_period)
    schedule_submission_reminders(submission_period)
    schedule_vote_reminders(submission_period)

    return redirect(request.referrer)
