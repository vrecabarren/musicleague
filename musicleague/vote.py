from datetime import datetime

from musicleague.models import Vote


def create_or_update_vote(votes, submission_period, league, user):
    v = next((vote for vote in submission_period.votes if vote.user == user), None)

    if v:
        v.votes = votes
        v.count += 1
        v.updated = datetime.utcnow()

        from musicleague.persistence.insert import insert_vote
        insert_vote(v)
    else:
        v = create_vote(votes, submission_period, user, league)

    return v


def create_vote(votes, submission_period, user, league):
    new_vote = Vote(
        votes=votes, user=user, created=datetime.utcnow(), league=league,
        submission_period=submission_period)

    from musicleague.persistence.insert import insert_vote
    insert_vote(new_vote)

    return new_vote


def get_vote(vote_id):
    try:
        return Vote.objects(id=vote_id).get()
    except Vote.DoesNotExist:
        return None


def get_my_vote(user, submission_period):
    return next(
        (v for v in submission_period.votes
         if v.user.id == user.id), None)