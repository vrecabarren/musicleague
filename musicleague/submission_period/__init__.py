from datetime import datetime
from datetime import timedelta

from musicleague import app
from musicleague.models import SubmissionPeriod
from musicleague.submission_period.tasks.cancelers import cancel_pending_task
from musicleague.submission_period.tasks.schedulers import schedule_playlist_creation  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_submission_reminders  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_vote_reminders  # noqa


def create_submission_period(
        league, name=None, description=None, submission_due_date=None,
        vote_due_date=None):
    if name is None:
        name = 'Round %s' % (len(league.submission_periods) + 1)

    if description is None:
        description = ''

    if submission_due_date is None:
        submission_due_date = datetime.utcnow() + timedelta(days=5)

    if vote_due_date is None:
        vote_due_date = datetime.utcnow() + timedelta(days=7)

    new_submission_period = SubmissionPeriod(
        name=name,
        description=description,
        created=datetime.utcnow(),
        league=league,
        submission_due_date=submission_due_date,
        vote_due_date=vote_due_date)

    # Save to get id for notification tasks
    new_submission_period.save()

    schedule_playlist_creation(new_submission_period)
    schedule_submission_reminders(new_submission_period)
    schedule_vote_reminders(new_submission_period)

    new_submission_period.save()

    app.logger.info('Submission period created: %s', new_submission_period.id)

    league.submission_periods.append(new_submission_period)
    league.save()

    return new_submission_period


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects().get(id=submission_period_id)

    except SubmissionPeriod.DoesNotExist:
        return None


def remove_submission_period(submission_period_id, submission_period=None):
    if submission_period is None:
        submission_period = get_submission_period(submission_period_id)

    if (not submission_period or
            str(submission_period.id) != str(submission_period_id)):
        return

    league = submission_period.league

    # Cancel all scheduled tasks
    for pending_task_id in submission_period.pending_tasks.values():
        cancel_pending_task(pending_task_id)

    submission_period.delete()

    league.reload('submission_periods')
    app.logger.info('Submission period removed: %s', submission_period_id)

    return submission_period


def update_submission_period(submission_period_id, name, description,
                             submission_due_date, vote_due_date):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period:
        return

    submission_period.name = name
    submission_period.description = description
    submission_period.submission_due_date = submission_due_date
    submission_period.vote_due_date = vote_due_date

    # Reschedule playlist creation and submission/vote reminders if needed
    schedule_playlist_creation(submission_period)
    schedule_submission_reminders(submission_period)
    schedule_vote_reminders(submission_period)

    submission_period.save()
    return submission_period
