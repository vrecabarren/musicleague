from rq.decorators import job

from musicleague import app
from musicleague import redis_conn
from musicleague.notify import user_all_voted_notification
from musicleague.notify import user_new_round_notification
from musicleague.notify import user_submit_reminder_notification
from musicleague.notify import user_vote_reminder_notification
from musicleague.persistence.select import select_round
from musicleague.scoring.league import calculate_league_scoreboard
from musicleague.scoring.round import calculate_round_scoreboard
from musicleague.spotify import create_or_update_playlist


class TYPES:
    """ Keys used to store ETA in entity for tasks below. Must be unique. """
    COMPLETE_SUBMISSION_PERIOD = 'csp'
    CREATE_PLAYLIST = 'cp'
    SEND_SUBMISSION_REMINDERS = 'ssr'
    SEND_VOTE_REMINDERS = 'svr'


@job('default', connection=redis_conn)
def complete_submission_process(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for completion!')
        return

    try:
        from musicleague.submission_period.tasks.cancelers import cancel_playlist_creation  # noqa
        from musicleague.submission_period.tasks.cancelers import cancel_submission_reminders  # noqa

        submission_period = select_round(submission_period_id)
        create_or_update_playlist(submission_period)
        cancel_playlist_creation(submission_period)
        cancel_submission_reminders(submission_period)
        submission_period.save()

    except:
        app.logger.exception(
            'Error occurred while completing submission process!')


@job('default', connection=redis_conn)
def complete_submission_period(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for completion!')
        return

    try:
        from musicleague.submission_period.tasks.cancelers import cancel_round_completion  # noqa
        from musicleague.submission_period.tasks.cancelers import cancel_vote_reminders

        submission_period = select_round(submission_period_id)
        calculate_round_scoreboard(submission_period)

        # Reload league to include updates to scored round
        submission_period.league.reload('submission_periods')
        calculate_league_scoreboard(submission_period.league)

        user_all_voted_notification(submission_period)

        cancel_round_completion(submission_period)
        cancel_vote_reminders(submission_period)
        submission_period.save()

        for idx, sp in enumerate(submission_period.league.submission_periods):
            if str(sp.id) == str(submission_period_id):
                if len(submission_period.league.submission_periods) > (idx + 1):
                    user_new_round_notification(submission_period.league.submission_periods[idx + 1])

    except:
        app.logger.exception(
            'Error occurred while completing submission period!')


@job('default', connection=redis_conn)
def create_playlist(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for playlist creation!')
        return

    try:
        with app.app_context():
            submission_period = select_round(submission_period_id)
            create_or_update_playlist(submission_period)
    except:
        app.logger.exception('Error occurred while creating playlist!')


@job('default', connection=redis_conn)
def send_submission_reminders(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for submission reminders!')
        return False

    try:
        submission_period = select_round(submission_period_id)
        for user in submission_period.have_not_submitted:
            app.logger.warning('%s has not submitted! Notifying.', user.name)
            user_submit_reminder_notification(user, submission_period)
        return True

    except Exception as e:
        app.logger.exception('Error while sending submission reminders: %s', e)
        return False


@job('default', connection=redis_conn)
def send_vote_reminders(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for vote reminders!')
        return False

    try:
        submission_period = select_round(submission_period_id)
        for user in submission_period.have_not_voted:
            app.logger.warning('%s has not submitted! Notifying.', user.name)
            user_vote_reminder_notification(user, submission_period)
        return True

    except Exception as e:
        app.logger.exception('Error while sending vote reminders: %s', e)
        return False
