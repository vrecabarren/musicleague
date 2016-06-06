from datetime import datetime
from datetime import timedelta

from feedback.models import SubmissionPeriod


def create_submission_period(league):
    name = '%s - SP %s' % (league.name, len(league.submission_periods) + 1)
    submission_due_date = datetime.now() + timedelta(days=5)
    vote_due_date = submission_due_date + timedelta(days=2)
    new_submission_period = SubmissionPeriod(
        name=name, league=league, submission_due_date=submission_due_date,
        vote_due_date=vote_due_date)
    new_submission_period.save()

    # Mark all other previous submission periods as not current
    for submission_period in league.submission_periods:
        if submission_period.is_current:
            submission_period.is_current = False
            submission_period.save()

    league.submission_periods.append(new_submission_period)
    league.save()

    return new_submission_period


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects(id=submission_period_id).get()
    except SubmissionPeriod.DoesNotExist:
        return None
