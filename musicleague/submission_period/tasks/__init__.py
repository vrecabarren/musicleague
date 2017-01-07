import logging

from musicleague import app
from musicleague import celery
from musicleague.notify import user_submit_reminder_notification
from musicleague.notify import user_vote_reminder_notification
from musicleague.spotify import create_or_update_playlist


class TYPES:
    """ Keys used to store ETA in entity for tasks below. Must be unique. """
    COMPLETE_SUBMISSION_PERIOD = 'csp'
    CREATE_PLAYLIST = 'cp'
    SEND_SUBMISSION_REMINDERS = 'ssr'
    SEND_VOTE_REMINDERS = 'svr'


@celery.task
def complete_submission_period(submission_period_id):
    if not submission_period_id:
        logging.error('No submission period id for completion!')
        return

    try:
        from musicleague.submission_period import get_submission_period

        get_submission_period(submission_period_id)

        # TODO implement scoring
    except:
        logging.exception('Error occurred while completing submission period!')


@celery.task
def create_playlist(submission_period_id):
    if not submission_period_id:
        logging.error('No submission period id for playlist creation!')
        return

    try:
        with app.app_context():
            from musicleague.submission_period import get_submission_period

            submission_period = get_submission_period(submission_period_id)
            create_or_update_playlist(submission_period)
    except:
        logging.exception('Error occurred while creating playlist!')


@celery.task
def send_submission_reminders(submission_period_id):
    if not submission_period_id:
        logging.error('No submission period id for submission reminders!')
        return False

    try:
        from musicleague.submission_period import get_submission_period

        submission_period = get_submission_period(submission_period_id)
        league = submission_period.league
        users_submitted = set([s.user for s in submission_period.submissions])
        to_notify = set(league.users) - users_submitted
        for user in to_notify:
            logging.warning('%s has not submitted! Notifying.', user.name)
            user_submit_reminder_notification(user, submission_period)
        return True

    except Exception as e:
        logging.exception('Error while sending submission reminders: %s', e)
        return False


@celery.task
def send_vote_reminders(submission_period_id):
    if not submission_period_id:
        logging.error('No submission period id for vote reminders!')
        return False

    try:
        from musicleague.submission_period import get_submission_period

        submission_period = get_submission_period(submission_period_id)
        league = submission_period.league
        users_voted = set([v.user for v in submission_period.votes])
        to_notify = set(league.users) - users_voted
        for user in to_notify:
            logging.warning('%s has not submitted! Notifying.', user.name)
            user_vote_reminder_notification(user, submission_period)
        return True

    except Exception as e:
        logging.exception('Error while sending vote reminders: %s', e)
        return False
