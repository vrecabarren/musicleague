from datetime import datetime
from datetime import timedelta
import logging
from pytz import utc

from rq.exceptions import NoSuchJobError
from rq.job import Job

from musicleague import redis_conn
from musicleague import scheduler
from musicleague.environment import is_deployed
from musicleague.persistence.select import select_league
from musicleague.submission_period.tasks import complete_submission_period
from musicleague.submission_period.tasks import complete_submission_process
from musicleague.submission_period.tasks import send_submission_reminders
from musicleague.submission_period.tasks import send_vote_reminders
from musicleague.submission_period.tasks import TYPES


def schedule_round_completion(submission_period):
    if not is_deployed():
        return

    completion_time = submission_period.vote_due_date

    job_id = '%s_%s' % (submission_period.id, TYPES.COMPLETE_SUBMISSION_PERIOD)

    try:
        # If job has been previously scheduled, reschedule
        job = Job.fetch(job_id, connection=redis_conn)
        scheduler.change_execution_time(job, completion_time)

        logging.info('Round completion changed to %s for %s.',
                     completion_time, job.id)

    except NoSuchJobError:
        # If job has not been previously scheduled, enqueue
        job = scheduler.enqueue_at(
            completion_time, complete_submission_period, str(submission_period.id),
            job_id=job_id)

        logging.info('Round completion enqueued for %s as %s',
                     completion_time, job.id)


def schedule_playlist_creation(submission_period):
    if not is_deployed():
        return

    creation_time = submission_period.submission_due_date

    job_id = '%s_%s' % (submission_period.id, TYPES.CREATE_PLAYLIST)

    try:
        # If job has been previously scheduled, reschedule
        job = Job.fetch(job_id, connection=redis_conn)
        scheduler.change_execution_time(job, creation_time)

        logging.info('Playlist creation changed to %s for %s',
                     creation_time, job.id)

    except NoSuchJobError:
        # If job has not been previously scheduled, enqueue
        job = scheduler.enqueue_at(
            creation_time, complete_submission_process, str(submission_period.id),
            job_id=job_id)

        logging.info('Playlist creation enqueued for %s as %s.',
                     creation_time, job.id)


def schedule_submission_reminders(submission_period):
    if not is_deployed():
        return

    # TODO Select preference instead of entire league
    league = select_league(submission_period.league_id)

    diff = league.preferences.submission_reminder_time
    notify_time = submission_period.submission_due_date - timedelta(hours=diff)

    job_id = '%s_%s' % (submission_period.id, TYPES.SEND_SUBMISSION_REMINDERS)

    # If notification time would be in the past, cancel
    # any enqueued job instead of scheduling
    if notify_time < utc.localize(datetime.now()):
        logging.info('Not rescheduling submission reminder - '
                     'datetime has passed for %s.', submission_period.id)
        scheduler.cancel(job_id)
        return

    try:
        # If job has been previously scheduled, reschedule
        job = Job.fetch(job_id, connection=redis_conn)
        scheduler.change_execution_time(job, notify_time)

        logging.info('Submission reminder changed to %s for %s.',
                     notify_time, job.id)

    except NoSuchJobError:
        # If job jas not been previously scheduled, enqueue
        job = scheduler.enqueue_at(
            notify_time, send_submission_reminders, str(submission_period.id),
            job_id=job_id)

        logging.info('Submission reminder scheduled for %s as %s.',
                     submission_period.id, job.id)


def schedule_vote_reminders(submission_period):
    if not is_deployed():
        return

    # TODO Select preference instead of entire league
    league = select_league(submission_period.league_id)

    diff = league.preferences.vote_reminder_time
    notify_time = submission_period.vote_due_date - timedelta(hours=diff)

    job_id = '%s_%s' % (submission_period.id, TYPES.SEND_VOTE_REMINDERS)

    # If notification time would be in the past, cancel
    # any enqueued job instead of scheduling
    if notify_time < utc.localize(datetime.now()):
        logging.info('Not rescheduling vote reminder - '
                     'datetime has passed for %s.', submission_period.id)
        scheduler.cancel(job_id)
        return

    try:
        # If job has been previously scheduled, reschedule
        job = Job.fetch(job_id, connection=redis_conn)
        scheduler.change_execution_time(job, notify_time)

        logging.info('Vote reminder changed to %s for %s.',
                     notify_time, job.id)

    except NoSuchJobError:
        # If job has not been previously scheduled, enqueue
        job = scheduler.enqueue_at(
            notify_time, send_vote_reminders, str(submission_period.id),
            job_id=job_id)

        logging.info('Vote reminder scheduled for %s as %s.',
                     submission_period.id, job.id)
