from feedback.models import Submission


def create_submission(tracks, submission_period, user, persist=True):
    new_submission = Submission(tracks=tracks, user=user)
    if persist:
        new_submission.save()
        submission_period.submissions.append(new_submission)
        submission_period.save()
    return new_submission
