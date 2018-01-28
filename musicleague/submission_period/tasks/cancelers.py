from musicleague import app
from musicleague import scheduler
from musicleague.environment import is_deployed
from musicleague.submission_period.tasks import TYPES


def cancel_round_completion(submission_period):
    if not is_deployed():
        return

    job_id = '%s_%s' % (submission_period.id, TYPES.COMPLETE_SUBMISSION_PERIOD)
    cancel_pending_task(job_id)
    app.logger.info('Completion canceled for %s', job_id)


def cancel_playlist_creation(submission_period):
    if not is_deployed():
        return

    job_id = '%s_%s' % (submission_period.id, TYPES.CREATE_PLAYLIST)
    cancel_pending_task(job_id)
    app.logger.info('Playlist creation canceled for %s.', job_id)


def cancel_submission_reminders(submission_period):
    if not is_deployed():
        return

    job_id = '%s_%s' % (submission_period.id, TYPES.SEND_SUBMISSION_REMINDERS)
    cancel_pending_task(job_id)
    app.logger.info('Submission reminders canceled for %s.', job_id)


def cancel_vote_reminders(submission_period):
    if not is_deployed():
        return

    job_id = '%s_%s' % (submission_period.id, TYPES.SEND_VOTE_REMINDERS)
    cancel_pending_task(job_id)
    app.logger.info('Vote reminders canceled for %s.', job_id)


def cancel_pending_task(job_id):
    if not job_id:
        app.logger.warning('No task_id for cancel_pending_task')
        return

    app.logger.info('Cancel job id %s', job_id)
    scheduler.cancel(job_id)
