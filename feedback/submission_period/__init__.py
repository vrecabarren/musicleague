from datetime import datetime
from datetime import timedelta
import logging

from feedback.models import SubmissionPeriod
from feedback.submission_period.tasks import TYPES
from feedback.submission_period.tasks.schedulers import _cancel_pending_task
from feedback.submission_period.tasks.schedulers import schedule_complete_submission_period  # noqa
from feedback.submission_period.tasks.schedulers import schedule_playlist_creation  # noqa
from feedback.submission_period.tasks.schedulers import schedule_submission_reminders  # noqa


def create_submission_period(league):
    new_submission_period = SubmissionPeriod(
        name='Submission Period %s' % (len(league.submission_periods) + 1),
        league=league,
        submission_due_date=datetime.utcnow() + timedelta(days=5),
        vote_due_date=datetime.utcnow() + timedelta(days=7))
    schedule_playlist_creation(new_submission_period)
    schedule_submission_reminders(new_submission_period)
    new_submission_period.save()

    logging.info('Submission period created: %s', new_submission_period.id)

    # Mark all other previous submission periods as not current
    for submission_period in league.submission_periods:
        if submission_period.is_current:
            submission_period.is_current = False
            submission_period.save()

    league.submission_periods.append(new_submission_period)
    league.save()

    return new_submission_period


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects(id=submission_period_id).get()

    except SubmissionPeriod.DoesNotExist:
        return None


def remove_submission_period(submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    removing_current = submission_period.is_current

    # Cancel scheduled submission reminder job if one exists
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_SUBMISSION_REMINDERS))

    submission_period.delete()

    league.reload('submission_periods')

    if removing_current and league.submission_periods:
        new_current = league.submission_periods[-1]
        new_current.is_current = True
        new_current.save()

    logging.info('Submission period removed: %s', submission_period_id)


def update_submission_period(submission_period_id, name, submission_due_date,
                             vote_due_date):
    try:
        submission_period = get_submission_period(submission_period_id)
        submission_period.name = name
        submission_period.submission_due_date = submission_due_date
        submission_period.vote_due_date = vote_due_date

        # Reschedule playlist creation and submission reminders if needed
        schedule_playlist_creation(submission_period)
        schedule_submission_reminders(submission_period)

        submission_period.save()
        return submission_period

    except SubmissionPeriod.DoesNotExist:
        return None
