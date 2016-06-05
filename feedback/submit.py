from datetime import datetime

from feedback.models import Submission
from feedback.models import SubmissionPeriod


def create_or_update_submission(tracks, submission_period, user):
    s = None
    for submission in submission_period.submissions:
        if submission.user == user:
            s = submission
            break

    if s:
        s.tracks = tracks
        s.count += 1
        s.updated = datetime.now()
        s.save()
    else:
        s = create_submission(tracks, submission_period, user)

    return s


def create_submission(tracks, submission_period, user, persist=True):
    new_submission = Submission(
        tracks=tracks, user=user, created=datetime.now())
    if persist:
        new_submission.save()
        submission_period.submissions.append(new_submission)
        submission_period.save()
    return new_submission


def create_submission_period(league):
    name = '%s - SP %s' % (league.name, len(league.submission_periods) + 1)
    new_submission_period = SubmissionPeriod(name=name)
    new_submission_period.save()

    # Mark all other previous submission periods as not current
    for submission_period in league.submission_periods:
        if submission_period.is_current:
            submission_period.is_current = False
            submission_period.save()

    league.submission_periods.append(new_submission_period)
    league.save()

    return new_submission_period


def get_submission(submission_id):
    try:
        return Submission.objects(id=submission_id).get()
    except SubmissionPeriod.DoesNotExist:
        return None


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects(id=submission_period_id).get()
    except SubmissionPeriod.DoesNotExist:
        return None
