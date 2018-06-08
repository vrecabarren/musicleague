from rq.decorators import job

from musicleague import app
from musicleague import redis_conn
from musicleague.notify import user_all_voted_notification
from musicleague.notify import user_new_round_notification
from musicleague.notify import user_submit_reminder_notification
from musicleague.notify import user_vote_reminder_notification
from musicleague.persistence.models import LeagueStatus
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.select import select_league
from musicleague.persistence.select import select_league_id_for_round
from musicleague.persistence.update import update_league_status
from musicleague.persistence.update import update_round_status
from musicleague.scoring.league import calculate_league_scoreboard
from musicleague.scoring.round import calculate_round_scoreboard
from musicleague.spotify import create_or_update_playlist


class TYPES:
    """ Keys used to store ETA in entity for tasks below. Must be unique. """
    COMPLETE_SUBMISSION_PERIOD = 'csp'
    CREATE_PLAYLIST = 'cp'
    NOTIFY_SUBMISSION_PERIOD = 'nsp'
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

        league_id = select_league_id_for_round(submission_period_id)
        league = select_league(league_id, exclude_properties=['votes', 'scoreboard', 'invited_users'])
        submission_period = next((r for r in league.submission_periods
                                  if r.id == submission_period_id), None)

        update_round_status(submission_period, RoundStatus.ACCEPTING_VOTES)

        # Set new status so old status isn't persisted with playlist URL 
        submission_period.status = RoundStatus.ACCEPTING_VOTES

        create_or_update_playlist(submission_period)
        cancel_playlist_creation(submission_period)
        cancel_submission_reminders(submission_period)

    except Exception as e:
        app.logger.exception(
            'Error occurred while completing submission process!', exc_info=e,
            extra={'round': submission_period_id})


@job('default', connection=redis_conn)
def complete_submission_period(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for completion!')
        return

    try:
        from musicleague.submission_period.tasks.cancelers import cancel_round_completion  # noqa
        from musicleague.submission_period.tasks.cancelers import cancel_vote_reminders

        league_id = select_league_id_for_round(submission_period_id)
        league = select_league(league_id)
        submission_period = next((r for r in league.submission_periods
                                  if r.id == submission_period_id), None)
        calculate_round_scoreboard(submission_period)
        update_round_status(submission_period, RoundStatus.COMPLETE)

        league = select_league(submission_period.league_id)
        calculate_league_scoreboard(league)

        user_all_voted_notification(submission_period)

        cancel_round_completion(submission_period)
        cancel_vote_reminders(submission_period)

        if league.is_complete:
            update_league_status(league.id, LeagueStatus.COMPLETE)
        else:
            from musicleague.submission_period.tasks.schedulers import schedule_new_round_notification
            schedule_new_round_notification(league.current_submission_period)

    except Exception as e:
        app.logger.exception(
            'Error occurred while completing submission period!', exc_info=e,
            extra={'round': submission_period_id})


@job('default', connection=redis_conn)
def notify_new_round(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for new round notification!')
        return

    try:
        with app.app_context():
            league_id = select_league_id_for_round(submission_period_id)
            league = select_league(
                league_id, exclude_properties=['submissions', 'votes', 'scoreboard', 'invited_users'])
            submission_period = next((r for r in league.submission_periods if r.id == submission_period_id), None)

            user_new_round_notification(submission_period)

    except Exception as e:
        app.logger.exception('Error occurred while notifying new round!', exc_info=e,
                             extra={'round': submission_period_id})


@job('default', connection=redis_conn)
def create_playlist(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for playlist creation!')
        return

    try:
        with app.app_context():
            league_id = select_league_id_for_round(submission_period_id)
            league = select_league(league_id, exclude_properties=['votes', 'scoreboard', 'invited_users'])
            submission_period = next((r for r in league.submission_periods if r.id == submission_period_id), None)

            create_or_update_playlist(submission_period)
    except Exception as e:
        app.logger.exception('Error occurred while creating playlist!', exc_info=e,
                             extra={'round': submission_period_id})


@job('default', connection=redis_conn)
def send_submission_reminders(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for submission reminders!')
        return False

    try:
        league_id = select_league_id_for_round(submission_period_id)
        league = select_league(league_id, exclude_properties=['votes', 'scoreboard', 'invited_users'])
        submission_period = next((r for r in league.submission_periods if r.id == submission_period_id), None)
        for user in submission_period.have_not_submitted:
            app.logger.debug('User has not submitted! Notifying.', extra={'user': str(user.id)})
            user_submit_reminder_notification(user, submission_period)
        return True

    except Exception as e:
        app.logger.exception('Error while sending submission reminders!', exc_info=e,
                             extra={'round': submission_period_id})
        return False


@job('default', connection=redis_conn)
def send_vote_reminders(submission_period_id):
    if not submission_period_id:
        app.logger.error('No submission period id for vote reminders!')
        return False

    try:
        league_id = select_league_id_for_round(submission_period_id)
        league = select_league(league_id, exclude_properties=['scoreboard', 'invited_users'])
        submission_period = next((r for r in league.submission_periods if r.id == submission_period_id), None)
        for user in submission_period.have_not_voted:
            app.logger.debug('User has not voted! Notifying.', extra={'user': str(user.id)})
            user_vote_reminder_notification(user, submission_period)
        return True

    except Exception as e:
        app.logger.exception('Error while sending vote reminders!', exc_info=e,
                             extra={'round': submission_period_id})
        return False
