from datetime import datetime
from datetime import timedelta
import logging

from musicleague.models import SubmissionPeriod
from musicleague.submission_period.tasks import TYPES
from musicleague.submission_period.tasks.schedulers import _cancel_pending_task
from musicleague.submission_period.tasks.schedulers import schedule_playlist_creation  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_submission_reminders  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_vote_reminders  # noqa


def create_submission_period(league):
    new_submission_period = SubmissionPeriod(
        name='Submission Period %s' % (len(league.submission_periods) + 1),
        created=datetime.utcnow(),
        league=league,
        submission_due_date=datetime.utcnow() + timedelta(days=5),
        vote_due_date=datetime.utcnow() + timedelta(days=7))

    # Save to get id for notification tasks
    new_submission_period.save()

    schedule_playlist_creation(new_submission_period)
    schedule_submission_reminders(new_submission_period)
    schedule_vote_reminders(new_submission_period)

    new_submission_period.save()

    logging.info('Submission period created: %s', new_submission_period.id)

    league.submission_periods.append(new_submission_period)
    league.save()

    return new_submission_period


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects().get(id=submission_period_id)

    except SubmissionPeriod.DoesNotExist:
        return None


def remove_submission_period(submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period:
        return

    league = submission_period.league

    # Cancel scheduled submission and vote reminder jobs if they exist
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_SUBMISSION_REMINDERS))
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_VOTE_REMINDERS))

    submission_period.delete()

    league.reload('submission_periods')

    logging.info('Submission period removed: %s', submission_period_id)


def update_submission_period(submission_period_id, name, submission_due_date,
                             vote_due_date):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period:
        return

    submission_period.name = name
    submission_period.submission_due_date = submission_due_date
    submission_period.vote_due_date = vote_due_date

    # Reschedule playlist creation and submission/vote reminders if needed
    schedule_playlist_creation(submission_period)
    schedule_submission_reminders(submission_period)
    schedule_vote_reminders(submission_period)

    submission_period.save()
    return submission_period
