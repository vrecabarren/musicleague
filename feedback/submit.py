from feedback.models import Submission
from feedback.models import SubmissionPeriod


def create_submission(tracks, submission_period, user, persist=True):
    new_submission = Submission(tracks=tracks, user=user)
    if persist:
        new_submission.save()
        submission_period.submissions.append(new_submission)
        submission_period.save()
    return new_submission


def create_submission_period(season):
    name = '%s - SP %s' % (season.name, len(season.submission_periods) + 1)
    new_submission_period = SubmissionPeriod(name=name)
    new_submission_period.save()

    # Mark all other previous submission periods as not current
    for submission_period in season.submission_periods:
        if submission_period.is_current:
            submission_period.is_current = False
            submission_period.save()

    season.submission_periods.append(new_submission_period)
    season.save()

    return new_submission_period
