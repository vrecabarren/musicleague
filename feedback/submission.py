from datetime import datetime

from feedback.models import Submission
from feedback.models import SubmissionPeriod


def create_or_update_submission(tracks, submission_period, league, user):
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
        s = create_submission(tracks, submission_period, user, league)

    return s


def create_submission(tracks, submission_period, user, league, persist=True):
    new_submission = Submission(
        tracks=tracks, user=user, created=datetime.now(), league=league,
        submission_period=submission_period)
    if persist:
        new_submission.save()
        submission_period.submissions.append(new_submission)
        submission_period.save()
    return new_submission


def get_submission(submission_id):
    try:
        return Submission.objects(id=submission_id).get()
    except SubmissionPeriod.DoesNotExist:
        return None
