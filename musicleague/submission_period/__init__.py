from datetime import datetime
from datetime import timedelta

from bson import ObjectId

from musicleague import app
from musicleague.models import SubmissionPeriod
from musicleague.persistence.delete import delete_round
from musicleague.persistence.insert import insert_round
from musicleague.persistence.models import LeagueStatus
from musicleague.persistence.models import Round
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.select import select_round
from musicleague.persistence.select import select_rounds_incomplete_count
from musicleague.persistence.update import update_league_status
from musicleague.persistence.update import update_round
from musicleague.submission_period.tasks.cancelers import cancel_pending_task
from musicleague.submission_period.tasks.cancelers import cancel_playlist_creation  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_round_completion  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_submission_reminders  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_vote_reminders  # noqa
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

    new_submission_period = Round(
        id=str(ObjectId()),
        league_id=str(league.id),
        created=datetime.utcnow(),
        name=name,
        description=description,
        playlist_url='',
        status=RoundStatus.CREATED,
        submissions_due=submission_due_date,
        votes_due=vote_due_date)
    new_submission_period.league = league
    league.submission_periods.append(new_submission_period)

    schedule_playlist_creation(new_submission_period)
    schedule_round_completion(new_submission_period)
    schedule_submission_reminders(new_submission_period)
    schedule_vote_reminders(new_submission_period)

    insert_round(new_submission_period)
    update_league_status(league.id, LeagueStatus.IN_PROGRESS)

    app.logger.info('Submission period created: %s', new_submission_period.id)

    return new_submission_period


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects().get(id=submission_period_id)

    except SubmissionPeriod.DoesNotExist:
        return None


def remove_submission_period(submission_period_id, submission_period=None):
    if submission_period is None:
        submission_period = select_round(submission_period_id)

    if (not submission_period or
            submission_period.id != submission_period_id):
        return

    # Cancel all scheduled tasks
    cancel_playlist_creation(submission_period)
    cancel_round_completion(submission_period)
    cancel_submission_reminders(submission_period)
    cancel_vote_reminders(submission_period)

    delete_round(submission_period)

    num_incomplete = select_rounds_incomplete_count(submission_period.league_id)
    if num_incomplete == 0:
        update_league_status(submission_period.league_id, LeagueStatus.COMPLETE)

    app.logger.info('Submission period removed: %s', submission_period_id)

    return submission_period


def update_submission_period(submission_period_id, name, description,
                             submission_due_date, vote_due_date, submission_period=None):
    submission_period = submission_period or select_round(submission_period_id)
    if not submission_period:
        return

    submission_period.name = name
    submission_period.description = description
    submission_period.submission_due_date = submission_due_date
    submission_period.vote_due_date = vote_due_date

    if submission_period.is_complete:
        submission_period.status = RoundStatus.COMPLETE
    else:
        submission_period.status = RoundStatus.CREATED

    # Reschedule playlist creation and submission/vote reminders if needed
    schedule_playlist_creation(submission_period)
    schedule_round_completion(submission_period)
    schedule_submission_reminders(submission_period)
    schedule_vote_reminders(submission_period)

    update_round(submission_period)

    app.logger.info('Submission period updated: %s', submission_period_id)

    return submission_period
