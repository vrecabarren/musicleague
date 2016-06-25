import logging

from feedback.notify import user_submit_reminder_notification
from feedback.spotify import create_or_update_playlist


class TYPES:
    COMPLETE_SUBMISSION_PERIOD = 'csp'
    CREATE_PLAYLIST = 'cp'
    SEND_SUBMISSION_REMINDERS = 'ssr'


def complete_submission_period(submission_period_id):
    try:
        from feedback.submission_period import get_submission_period

        get_submission_period(submission_period_id)

        # TODO implement scoring
    except:
        logging.exception('Error occurred while completing submission period!')


def create_playlist(submission_period_id):
    try:
        from feedback.submission_period import get_submission_period

        submission_period = get_submission_period(submission_period_id)
        create_or_update_playlist(submission_period)
    except:
        logging.exception('Error occurred while creating playlist!')


def send_submission_reminders(submission_period_id):
    try:
        from feedback.submission_period import get_submission_period

        submission_period = get_submission_period(submission_period_id)
        league = submission_period.league
        users_submitted = set([s.user for s in submission_period.submissions])
        to_notify = set(league.users) - users_submitted
        for user in to_notify:
            logging.warning('%s has not submitted! Notifying.', user.name)
            user_submit_reminder_notification(user, league)

    except:
        logging.exception('Error occurred while sending submission reminders!')
