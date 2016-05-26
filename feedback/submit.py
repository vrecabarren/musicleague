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
        s.save()
    else:
        s = create_submission(tracks, submission_period, user)

    return s


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


def get_submission_period(submission_period_id):
    try:
        return SubmissionPeriod.objects(id=submission_period_id).get()
    except SubmissionPeriod.DoesNotExist:
        return None
