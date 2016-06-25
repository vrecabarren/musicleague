from datetime import timedelta
import logging

from feedback import scheduler
from feedback.submission_period.tasks import complete_submission_period
from feedback.submission_period.tasks import create_playlist
from feedback.submission_period.tasks import send_submission_reminders
from feedback.submission_period.tasks import TYPES


def schedule_complete_submission_period(submission_period):
    completion_time = submission_period.vote_due_date

    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.COMPLETE_SUBMISSION_PERIOD))

    completion_task_id = scheduler.enqueue_at(
        completion_time,
        complete_submission_period,
        submission_period.id).id

    submission_period.pending_tasks.update(
        {TYPES.COMPLETE_SUBMISSION_PERIOD: completion_task_id})

    logging.info('Submission period completion scheduled for %s. Job ID: %s.',
                 completion_time, completion_task_id)


def schedule_playlist_creation(submission_period):
    # TODO Check preferences

    creation_time = submission_period.submission_due_date

    # Cancel scheduled creation job if one exists
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.CREATE_PLAYLIST))

    # Schedule new playlist creation task
    creation_task_id = scheduler.enqueue_at(
        creation_time,
        create_playlist,
        submission_period.id).id

    submission_period.pending_tasks.update(
        {TYPES.CREATE_PLAYLIST: creation_task_id})

    logging.info('Playlist creation scheduled for %s. Job ID: %s.',
                 creation_time, creation_task_id)


def schedule_submission_reminders(submission_period):
    # TODO Check preferences
    notify_time = submission_period.submission_due_date - timedelta(hours=2)

    # Cancel scheduled notification job if one exists
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_SUBMISSION_REMINDERS))

    # Schedule new submission reminder task
    reminder_task_id = scheduler.enqueue_at(
        notify_time,
        send_submission_reminders,
        submission_period.id).id

    submission_period.pending_tasks.update(
        {TYPES.SEND_SUBMISSION_REMINDERS: reminder_task_id})

    logging.info('Submission reminders scheduled for %s. Job ID: %s.',
                 notify_time, reminder_task_id)


def _cancel_pending_task(task_id):
    if not task_id:
        return

    scheduler.cancel(task_id)
