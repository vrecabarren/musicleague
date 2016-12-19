from datetime import timedelta
import logging

from musicleague import celery
from musicleague.environment import is_deployed
from musicleague.submission_period.tasks import complete_submission_period
from musicleague.submission_period.tasks import create_playlist
from musicleague.submission_period.tasks import send_submission_reminders
from musicleague.submission_period.tasks import send_vote_reminders
from musicleague.submission_period.tasks import TYPES


def schedule_complete_submission_period(submission_period):
    if not is_deployed():
        return

    completion_time = submission_period.vote_due_date

    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.COMPLETE_SUBMISSION_PERIOD))

    task = complete_submission_period.apply_async(
        args=[str(submission_period.id)], eta=completion_time)

    submission_period.pending_tasks.update(
        {TYPES.COMPLETE_SUBMISSION_PERIOD: task.task_id})

    logging.info('Submission period completion scheduled for %s. Job ID: %s.',
                 completion_time, task.task_id)


def schedule_playlist_creation(submission_period):
    if not submission_period.league.preferences.auto_playlist_creation:
        return

    creation_time = submission_period.submission_due_date

    # Cancel scheduled creation job if one exists
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.CREATE_PLAYLIST))

    # Schedule new playlist creation task
    task = create_playlist.apply_async(
        args=[str(submission_period.id)], eta=creation_time)

    submission_period.pending_tasks.update(
        {TYPES.CREATE_PLAYLIST: task.task_id})

    logging.info('Playlist creation scheduled for %s. Job ID: %s.',
                 creation_time, task.task_id)


def schedule_submission_reminders(submission_period):
    if not is_deployed():
        return

    diff = submission_period.league.preferences.submission_reminder_time
    notify_time = submission_period.submission_due_date - timedelta(hours=diff)

    # Cancel scheduled notification job if one exists
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_SUBMISSION_REMINDERS))

    # Schedule new submission reminder task
    task = send_submission_reminders.apply_async(
        args=[str(submission_period.id)], eta=notify_time)

    submission_period.pending_tasks.update(
        {TYPES.SEND_SUBMISSION_REMINDERS: task.task_id})

    logging.info('Submission reminders scheduled for %s. Job ID: %s.',
                 notify_time, task.task_id)


def schedule_vote_reminders(submission_period):
    if not is_deployed():
        return

    diff = submission_period.league.preferences.vote_reminder_time
    notify_time = submission_period.vote_due_date - timedelta(hours=diff)

    # Cancel scheduled notification job if one exists
    _cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_VOTE_REMINDERS))

    # Schedule new vote reminder task
    task = send_vote_reminders.apply_async(
        args=[str(submission_period.id)], eta=notify_time)

    submission_period.pending_tasks.update(
        {TYPES.SEND_VOTE_REMINDERS: task.task_id})

    logging.info('Vote reminders scheduled for %s. Job ID: %s.',
                 notify_time, task.task_id)


def _cancel_pending_task(task_id):
    if not task_id:
        logging.warning('No task_id for _cancel_pending_task')
        return

    logging.info('Revoking celery task %s', task_id)
    celery.control.revoke(task_id, terminate=True)
