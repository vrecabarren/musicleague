import collections
import operator

def build_voting_chart_datasets(round):
    """
    Put together a vote-by-vote report of scoring
    for each submission in a round.

    Example dataset format:

    {
        'spotify:track:5EYi2rH4LYs6M21ZLOyQTx': [1, 11, 21],
        'spotify:track:5mRrklQD0rvuN6sV10HfPn': [4, 8, 16]
    }

    :param round: a Round
    :return: a dictionary mapping each submitted track's URI to a list of accumulating scores
    """
    if not round.is_complete:
        return {}

    votes_by_uri = {t: [0] for t in round.all_tracks}

    for vote in sorted(round.votes, key=operator.attrgetter('created')):
        for uri, points in votes_by_uri.items():
            prev_total = points[-1]
            new_points = vote.votes.get(uri, 0)
            points.append(prev_total + new_points)

    return votes_by_uri
