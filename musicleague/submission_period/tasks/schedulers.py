from datetime import datetime
from datetime import timedelta
import logging
from pytz import utc

from musicleague import scheduler
from musicleague.environment import is_deployed
from musicleague.persistence.select import select_league
from musicleague.submission_period.tasks import complete_submission_period
from musicleague.submission_period.tasks import complete_submission_process
from musicleague.submission_period.tasks import send_submission_reminders
from musicleague.submission_period.tasks import send_vote_reminders
from musicleague.submission_period.tasks import TYPES
from musicleague.submission_period.tasks.cancelers import cancel_playlist_creation  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_round_completion  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_submission_reminders  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_vote_reminders


def schedule_round_completion(submission_period):
    if not is_deployed():
        return

    completion_time = submission_period.vote_due_date

    cancel_round_completion(submission_period)

    job = scheduler.enqueue_at(
        completion_time, complete_submission_period, str(submission_period.id))

    submission_period.pending_tasks.update(
        {TYPES.COMPLETE_SUBMISSION_PERIOD: job.id})
    logging.info('Completion scheduled for %s.', submission_period.id)


def schedule_playlist_creation(submission_period):
    if not is_deployed():
        return

    creation_time = submission_period.submission_due_date

    # Cancel scheduled creation job if one exists
    cancel_playlist_creation(submission_period)

    # Schedule new playlist creation task
    job = scheduler.enqueue_at(
        creation_time, complete_submission_process, str(submission_period.id))

    submission_period.pending_tasks.update({TYPES.CREATE_PLAYLIST: job.id})
    logging.info('Playlist creation scheduled for %s. Job ID: %s.',
                 creation_time, job.id)


def schedule_submission_reminders(submission_period):
    if not is_deployed():
        return

    league = select_league(submission_period.league_id)

    diff = league.preferences.submission_reminder_time
    notify_time = submission_period.submission_due_date - timedelta(hours=diff)

    # Cancel scheduled notification job if one exists
    cancel_submission_reminders(submission_period)

    if notify_time < utc.localize(datetime.now()):
        logging.info('Not rescheduling submission reminder - '
                     'datetime has passed for %s.', submission_period.id)
        return

    # Schedule new submission reminder task
    job = scheduler.enqueue_at(
        notify_time, send_submission_reminders, str(submission_period.id))

    submission_period.pending_tasks.update(
        {TYPES.SEND_SUBMISSION_REMINDERS: job.id})
    logging.info('Submission reminder scheduled for %s.', submission_period.id)


def schedule_vote_reminders(submission_period):
    if not is_deployed():
        return

    league = select_league(submission_period.league_id)

    diff = league.preferences.vote_reminder_time
    notify_time = submission_period.vote_due_date - timedelta(hours=diff)

    # Cancel scheduled notification job if one exists
    cancel_vote_reminders(submission_period)

    if notify_time < utc.localize(datetime.now()):
        logging.info('Not rescheduling vote reminder - '
                     'datetime has passed for %s.', submission_period.id)

    # Schedule new vote reminder task
    job = scheduler.enqueue_at(
        notify_time, send_vote_reminders, str(submission_period.id))

    submission_period.pending_tasks.update({TYPES.SEND_VOTE_REMINDERS: job.id})
    logging.info('Vote reminder scheduled for %s.', submission_period.id)
