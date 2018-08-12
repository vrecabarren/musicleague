from datetime import datetime

from musicleague.persistence.models import Vote
from musicleague.persistence.insert import insert_vote


def create_or_update_vote(votes, comments, submission_period, league, user):
    v = get_my_vote(user, submission_period)

    if v:
        v.created = datetime.utcnow()
        v.updated = datetime.utcnow()
        v.votes = votes
        v.comments = comments
        v.count += 1

        insert_vote(v)
    else:
        v = create_vote(votes, comments, submission_period, user, league)

    return v


def create_vote(votes, comments, submission_period, user, league):
    new_vote = Vote(user=user, votes=votes, comments=comments, created=datetime.utcnow())
    new_vote.league = league
    new_vote.submission_period = submission_period

    submission_period.votes.append(new_vote)

    insert_vote(new_vote)

    return new_vote


def get_my_vote(user, submission_period):
    return next(
        (v for v in submission_period.votes
         if v.user.id == user.id), None)