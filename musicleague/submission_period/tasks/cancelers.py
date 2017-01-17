import logging

from musicleague import scheduler
from musicleague.environment import is_deployed
from musicleague.submission_period.tasks import TYPES


def cancel_round_completion(submission_period):
    if not is_deployed():
        return

    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.COMPLETE_SUBMISSION_PERIOD))

    submission_period.pending_tasks.pop(TYPES.COMPLETE_SUBMISSION_PERIOD, None)

    logging.info('Completion canceled for %s', submission_period.id)


def cancel_playlist_creation(submission_period):
    if not is_deployed():
        return

    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.CREATE_PLAYLIST))

    submission_period.pending_tasks.pop(TYPES.CREATE_PLAYLIST, None)
    logging.info('Playlist creation canceled for %s.', submission_period.id)


def cancel_submission_reminders(submission_period):
    if not is_deployed():
        return

    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_SUBMISSION_REMINDERS))

    submission_period.pending_tasks.pop(TYPES.SEND_SUBMISSION_REMINDERS, None)
    logging.info('Submission reminders canceled for %s.', submission_period.id)


def cancel_vote_reminders(submission_period):
    if not is_deployed():
        return

    cancel_pending_task(
        submission_period.pending_tasks.get(TYPES.SEND_VOTE_REMINDERS))

    submission_period.pending_tasks.pop(TYPES.SEND_VOTE_REMINDERS, None)
    logging.info('Vote reminders canceled for %s.', submission_period.id)


def cancel_pending_task(job_id):
    if not job_id:
        logging.warning('No task_id for cancel_pending_task')
        return

    logging.info('Cancel job id %s', job_id)
    scheduler.cancel(job_id)
