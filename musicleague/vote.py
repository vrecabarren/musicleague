from datetime import datetime

from musicleague.models import Vote


def create_or_update_vote(votes, submission_period, league, user):
    v = None
    for vote in submission_period.votes:
        if vote.user == user:
            v = vote
            break

    if v:
        v.votes = votes
        v.count += 1
        v.updated = datetime.utcnow()
        v.save()
    else:
        v = create_vote(votes, submission_period, user, league)

    return v


def create_vote(votes, submission_period, user, league, persist=True):
    new_vote = Vote(
        votes=votes, user=user, created=datetime.utcnow(), league=league,
        submission_period=submission_period)
    if persist:
        new_vote.save()
        submission_period.votes.append(new_vote)
        submission_period.save()
    return new_vote


def get_vote(vote_id):
    try:
        return Vote.objects(id=vote_id).get()
    except Vote.DoesNotExist:
        return None
