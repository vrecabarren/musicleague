from datetime import timedelta
import logging

from musicleague import scheduler
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

    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.COMPLETE_SUBMISSION_PERIOD))

    job = scheduler.enqueue_at(
        completion_time, complete_submission_period, str(submission_period.id))

    submission_period.pending_tasks.update(
        {TYPES.COMPLETE_SUBMISSION_PERIOD: job.id})

    logging.info('Submission period completion scheduled for %s. Job ID: %s.',
                 completion_time, job.id)


def schedule_playlist_creation(submission_period):
    if not is_deployed():
        return

    creation_time = submission_period.submission_due_date

    # Cancel scheduled creation job if one exists
    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.CREATE_PLAYLIST))

    # Schedule new playlist creation task
    job = scheduler.enqueue_at(
        creation_time, create_playlist, str(submission_period.id))

    submission_period.pending_tasks.update({TYPES.CREATE_PLAYLIST: job.id})

    logging.info('Playlist creation scheduled for %s. Job ID: %s.',
                 creation_time, job.id)


def schedule_submission_reminders(submission_period):
    if not is_deployed():
        return

    diff = submission_period.league.preferences.submission_reminder_time
    notify_time = submission_period.submission_due_date - timedelta(hours=diff)

    # Cancel scheduled notification job if one exists
    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_SUBMISSION_REMINDERS))

    # Schedule new submission reminder task
    job = scheduler.enqueue_at(
        notify_time, send_submission_reminders, str(submission_period.id))

    submission_period.pending_tasks.update(
        {TYPES.SEND_SUBMISSION_REMINDERS: job.id})

    logging.info('Submission reminders scheduled for %s. Job ID: %s.',
                 notify_time, job.id)


def schedule_vote_reminders(submission_period):
    if not is_deployed():
        return

    diff = submission_period.league.preferences.vote_reminder_time
    notify_time = submission_period.vote_due_date - timedelta(hours=diff)

    # Cancel scheduled notification job if one exists
    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_VOTE_REMINDERS))

    # Schedule new vote reminder task
    job = scheduler.enqueue_at(
        notify_time, send_vote_reminders, str(submission_period.id))

    submission_period.pending_tasks.update({TYPES.SEND_VOTE_REMINDERS: job.id})

    logging.info('Vote reminders scheduled for %s. Job ID: %s.',
                 notify_time, job.id)


def cancel_pending_task(job_id):
    if not job_id:
        logging.warning('No task_id for cancel_pending_task')
        return

    logging.info('Cancel job id %s', job_id)
    scheduler.cancel(job_id)
