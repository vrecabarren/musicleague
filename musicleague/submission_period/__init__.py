from datetime import datetime
from datetime import timedelta

from musicleague import app
from musicleague.models import SubmissionPeriod
from musicleague.persistence.statements import DELETE_ROUND
from musicleague.persistence.statements import INSERT_ROUND
from musicleague.persistence.statements import UPDATE_ROUND
from musicleague.submission_period.tasks.cancelers import cancel_pending_task
from musicleague.submission_period.tasks.schedulers import schedule_playlist_creation  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_round_completion  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_submission_reminders  # noqa
from musicleague.submission_period.tasks.schedulers import schedule_vote_reminders  # noqa


def create_submission_period(
        league, name=None, description=None, submission_due_date=None,
        vote_due_date=None):

    name = name or ('Round %s' % (len(league.submission_periods) + 1))
    description = description or ''
    submission_due_date = submission_due_date or (
        datetime.utcnow() + timedelta(days=5))
    vote_due_date = vote_due_date or (datetime.utcnow() + timedelta(days=7))

    new_submission_period = SubmissionPeriod(
        name=name,
        description=description,
        created=datetime.utcnow(),
        league=league,
        submission_due_date=submission_due_date,
        vote_due_date=vote_due_date)

    # Save to get id for notification tasks
    new_submission_period.save()

    schedule_playlist_creation(new_submission_period)
    schedule_round_completion(new_submission_period)
    schedule_submission_reminders(new_submission_period)
    schedule_vote_reminders(new_submission_period)

    new_submission_period.save()

    app.logger.info('Submission period created: %s', new_submission_period.id)

    league.submission_periods.append(new_submission_period)
    league.save()

    try:
        from musicleague import postgres_conn

        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_ROUND,
                    (new_submission_period.id, description, league.id,
                     name, submission_due_date, vote_due_date))
    except Exception as e:
        app.logger.warning('Failed INSERT_ROUND: %s', str(e))
        pass

    return new_submission_period


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects().get(id=submission_period_id)

    except SubmissionPeriod.DoesNotExist:
        return None


def remove_submission_period(submission_period_id, submission_period=None):
    if submission_period is None:
        submission_period = get_submission_period(submission_period_id)

    if (not submission_period or
            str(submission_period.id) != str(submission_period_id)):
        return

    league = submission_period.league

    # Cancel all scheduled tasks
    for pending_task_id in submission_period.pending_tasks.values():
        cancel_pending_task(pending_task_id)

    submission_period.delete()

    try:
        from musicleague import postgres_conn

        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(DELETE_ROUND, (submission_period_id,))
    except:
        pass

    league.reload('submission_periods')
    app.logger.info('Submission period removed: %s', submission_period_id)

    return submission_period


def update_submission_period(submission_period_id, name, description,
                             submission_due_date, vote_due_date):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period:
        return

    submission_period.name = name
    submission_period.description = description
    submission_period.submission_due_date = submission_due_date
    submission_period.vote_due_date = vote_due_date

    # Reschedule playlist creation and submission/vote reminders if needed
    schedule_playlist_creation(submission_period)
    schedule_round_completion(submission_period)
    schedule_submission_reminders(submission_period)
    schedule_vote_reminders(submission_period)

    submission_period.save()

    try:
        from musicleague import postgres_conn

        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_ROUND,
                    (submission_period_id, description,
                     submission_period.league.id,
                     name, submission_due_date, vote_due_date))
                cur.execute(
                    UPDATE_ROUND,
                    (description, name, submission_due_date, vote_due_date))
    except Exception as e:
        app.logger.warning('Failed UPDATE_ROUND: %s', str(e))
        pass

    return submission_period
