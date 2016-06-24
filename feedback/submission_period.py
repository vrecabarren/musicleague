from datetime import datetime
from datetime import timedelta
import logging

from feedback import default_scheduler
from feedback.models import SubmissionPeriod
from feedback.notify import user_submit_reminder_notification


def create_submission_period(league):
    new_submission_period = SubmissionPeriod(
        name='Submission Period %s' % (len(league.submission_periods) + 1),
        league=league,
        submission_due_date=datetime.utcnow() + timedelta(days=5),
        vote_due_date=datetime.utcnow() + timedelta(days=7))
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

    # Cancel scheduled submission reminder job if one exists
    reminder_task_id = submission_period.pending_tasks.get(
        SubmissionPeriod.TASK_SEND_SUBMISSION_REMINDERS)
    if reminder_task_id:
        default_scheduler.cancel(reminder_task_id)

    submission_period.delete()

    logging.info('Submission period removed: %s', submission_period_id)


def update_submission_period(submission_period_id, name, submission_due_date,
                             vote_due_date):
    try:
        submission_period = get_submission_period(submission_period_id)
        submission_period.name = name
        submission_period.submission_due_date = submission_due_date
        submission_period.vote_due_date = vote_due_date

        # Reschedule submission reminders if needed
        schedule_submission_reminders(submission_period)

        submission_period.save()
        return submission_period

    except SubmissionPeriod.DoesNotExist:
        return None


def schedule_submission_reminders(submission_period):
    notify_time = submission_period.submission_due_date - timedelta(hours=2)

    # Cancel scheduled notification job if one exists
    reminder_task_id = submission_period.pending_tasks.get(
        SubmissionPeriod.TASK_SEND_SUBMISSION_REMINDERS)
    if reminder_task_id:
        default_scheduler.cancel(reminder_task_id)

    # Schedule new notification job
    reminder_task_id = default_scheduler.enqueue_at(
        notify_time,
        send_submission_reminders,
        submission_period.id).id

    submission_period.pending_tasks.update(
        {SubmissionPeriod.TASK_SEND_SUBMISSION_REMINDERS: reminder_task_id})

    logging.info('Submission reminders scheduled for %s. Job ID: %s.',
                 notify_time, reminder_task_id)


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
