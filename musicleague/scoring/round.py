from collections import Counter
from itertools import groupby

from musicleague.models import Scoreboard
from musicleague.models import ScoreboardEntry


def calculate_round_scoreboard(round):
    """ Calculate and store scoreboard on round. The scoreboard consists of
    a dict where keys are the rankings for each entry. The values for the
    scoreboard are lists of entries. In most cases, the list will have a
    length of 1; however, if two or more songs are tied, the list will grow
    in length for a particular ranking.
    """
    round.scoreboard = Scoreboard()

    # Create a ScoreboardEntry for each song with corresponding Submission
    entries = {uri: ScoreboardEntry(uri=uri, submission=submission)
               for submission in round.submissions
               for uri in submission.tracks}

    # Get Votes for each entry
    for vote in round.votes:
        for uri, points in vote.votes.iteritems():
            if points > 0:
                entries[uri].votes.append(vote)

    # Sort votes on each entry by number of points awarded
    for entry in entries.values():
        entry.votes = sorted(entry.votes,
                             key=lambda x: x.votes[entry.uri],
                             reverse=True)

    # Rank entries and assign to round scoreboard with string keys
    rankings = rank_entries(entries.values())
    for rank, entries in rankings.iteritems():
        round.scoreboard._rankings[str(rank)] = entries

    round.save()
    return round


def rank_entries(entries):
    """ Given a list of ScoreboardEntry entities, return a dict where the key
    is the ranking and the value is a list of ScoreboardEntry entities for that
    ranking. In general, we aim for this list to have a length of 1 for each
    key since a list with length > 1 means there is a tie for the ranking.
    """
    entries = sorted(entries, cmp=entry_sort_cmp, reverse=True)
    grouped_entries = groupby(entries, key=entry_group_key)
    entries = [list(group) for _, group in grouped_entries]

    # Index entries by ranking
    rankings = {}
    for i, entries in enumerate(entries):
        rankings[i + 1] = entries

    return rankings


def entry_sort_cmp(entry1, entry2):
    cmp_order = [
        _cmp_entry_points,
        _cmp_entry_num_voters,
        _cmp_entry_highest_vote
    ]

    for cmp in cmp_order:
        diff = cmp(entry1, entry2)
        if diff != 0:
            return diff

    return 0


def _cmp_entry_points(entry1, entry2):
    """ Compare two ScoreboardEntry objects based on the raw number of points.
    """
    if entry1.points > entry2.points:
        return 1
    elif entry1.points < entry2.points:
        return -1
    return 0


def _cmp_entry_num_voters(entry1, entry2):
    """ Compare two ScoreboardEntry objects based on the number of users who
    voted for each.
    """
    if len(entry1.votes) > len(entry2.votes):
        return 1
    elif len(entry1.votes) < len(entry2.votes):
        return -1
    return 0


def _cmp_entry_highest_vote(entry1, entry2):
    """ Compare two ScoreboardEntry objects based on the highest asymmetric
    individual vote received.
    """
    entry1_votes = set([vote.votes[entry1.uri] for vote in entry1.votes])
    entry2_votes = set([vote.votes[entry2.uri] for vote in entry2.votes])

    # Get sorted lists of asymmetric votes. We can't use set() for this as
    # duplicates should be kept intact when doing the diff.
    entry1_counter = Counter(entry1_votes)
    entry1_counter.subtract(Counter(entry2_votes))
    entry1_asym = sorted(list(entry1_counter.elements()), reverse=True)

    entry2_counter = Counter(entry2_votes)
    entry2_counter.subtract(Counter(entry1_votes))
    entry2_asym = sorted(list(entry2_counter.elements()), reverse=True)

    if next(iter(entry1_asym), 0) > next(iter(entry2_asym), 0):
        return 1
    elif next(iter(entry1_asym), 0) < next(iter(entry2_asym), 0):
        return -1

    return 0


def entry_group_key(entry):
    return (entry.points, len(entry.votes))
