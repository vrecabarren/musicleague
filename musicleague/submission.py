from datetime import datetime

from musicleague.models import Submission


def create_or_update_submission(tracks, submission_period, league, user):
    """ If the specified user already has a Submission for the specified
    submission_period, update it with the latest set of tracks submitted.
    If not, create one.
    """
    # TODO Use submission_period.league instead of passing league
    s = None
    for submission in submission_period.submissions:
        if submission.user == user:
            s = submission
            break

    if s:
        s.tracks = tracks
        s.count += 1
        s.updated = datetime.utcnow()
        s.save()
    else:
        s = create_submission(tracks, submission_period, user, league)

    return s


def create_submission(tracks, submission_period, user, league, persist=True):
    """ Create a new Submission for specified user in the specified round. """
    # TODO Use submission_period.league instead of passing league
    new_submission = Submission(
        tracks=tracks, user=user, created=datetime.utcnow(), league=league,
        submission_period=submission_period)
    if persist:
        new_submission.save()
        submission_period.submissions.append(new_submission)
        submission_period.save()
    return new_submission


def get_submission(submission_id):
    """ Return submission if submission_id found; otherwise, return None. """
    try:
        return Submission.objects(id=submission_id).get()
    except Submission.DoesNotExist:
        return None


def get_my_submission(user, submission_period):
    return next(
        (s for s in submission_period.submissions
         if s.user.id == user.id), None)
