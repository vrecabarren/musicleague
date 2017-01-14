from flask import redirect
from flask import request

from musicleague import app
from musicleague import scheduler
from musicleague.notify.flash import flash_error
from musicleague.notify.flash import flash_success
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required
from musicleague.submission_period import get_submission_period
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period.tasks.schedulers import schedule_playlist_creation  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_submission_reminders  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_vote_reminders  # noqa


REMOVE_ROUND_URL = '/admin/rounds/<submission_period_id>/remove/'
RESCHEDULE_TASKS_URL = '/admin/rounds/<submission_period_id>/reschedule/'


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

    submission_period = get_submission_period(submission_period_id)
    if not submission_period:
        return

    schedule_playlist_creation(submission_period)
    schedule_submission_reminders(submission_period)
    schedule_vote_reminders(submission_period)
    submission_period.save()

    return redirect(request.referrer)
