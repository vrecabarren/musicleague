from datetime import datetime
from datetime import timedelta
import logging

from feedback import default_scheduler
from feedback.models import SubmissionPeriod
from feedback.notify import user_submit_reminder_notification


def create_submission_period(league):
    name = '%s - SP %s' % (league.name, len(league.submission_periods) + 1)
    submission_due_date = datetime.utcnow() + timedelta(days=5)
    vote_due_date = submission_due_date + timedelta(days=2)
    new_submission_period = SubmissionPeriod(
        name=name, league=league, submission_due_date=submission_due_date,
        vote_due_date=vote_due_date)
    new_submission_period.save()

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


def update_submission_period(submission_period_id, name, submission_due_date):
    try:
        submission_period = get_submission_period(submission_period_id)
        submission_period.name = name

        # Reschedule notification reminders if needed
        # TODO Remove any previously queued reminders for this period
        if submission_due_date != submission_period.submission_due_date:
            submission_period.submission_due_date = submission_due_date
            notify = submission_period.submission_due_date - timedelta(hours=2)
            logging.warning('Inserting task to notify at %s. Currently: %s',
                            notify, datetime.utcnow())
            default_scheduler.enqueue_at(
                notify,
                send_submission_reminders,
                submission_period_id)

        submission_period.save()
        return submission_period

    except SubmissionPeriod.DoesNotExist:
        return None


def send_submission_reminders(submission_period_id):
    try:
        submission_period = get_submission_period(submission_period_id)
        league = submission_period.league
        users_submitted = set([s.user for s in submission_period.submissions])
        to_notify = set(league.users) - users_submitted
        for user in to_notify:
            logging.warning('%s has not submitted! Notifying.', user.name)
            user_submit_reminder_notification(user, league)

    except:
        logging.exception('Error occurred while sending submission reminders!')
