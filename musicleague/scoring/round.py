from collections import Counter
from itertools import groupby

from musicleague.models import Scoreboard
from musicleague.models import ScoreboardEntry
from musicleague.scoring import EntrySortKey


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
    entries = sorted(entries, key=ScoreboardEntrySortKey, reverse=True)
    grouped_entries = groupby(entries, key=ScoreboardEntrySortKey)
    entries = [list(group) for _, group in grouped_entries]

    # Index entries by ranking
    rankings = {}
    for i, entries in enumerate(entries):
        rankings[i + 1] = entries

    return rankings


class ScoreboardEntrySortKey(EntrySortKey):

    def _ordered_cmp(self, other):
        _cmp_order = [
            self._cmp_entry_points,
            self._cmp_entry_num_voters,
            self._cmp_entry_highest_vote
        ]

        for _cmp in _cmp_order:
            diff = _cmp(other)
            if diff != 0:
                return diff

        return 0

    def _cmp_entry_points(self, other):
        """ Compare two ScoreboardEntry objects based on the raw number of
        points.
        """
        if self.obj.points > other.points:
            return 1
        elif self.obj.points < other.points:
            return -1
        return 0

    def _cmp_entry_num_voters(self, other):
        """ Compare two ScoreboardEntry objects based on the number of unique
        users who voted for each.
        """
        if len(self.obj.votes) > len(other.votes):
            return 1
        elif len(self.obj.votes) < len(other.votes):
            return -1
        return 0

    def _cmp_entry_highest_vote(self, other):
        """ Compare two ScoreboardEntry objects based on the highest
        individual asymmetric vote received.
        """
        self_votes = [v.votes[self.obj.uri] for v in self.obj.votes]
        other_votes = [v.votes[other.uri] for v in other.votes]

        # Get sorted lists of asymmetric votes. We can't use set() for this as
        # duplicates should be kept intact when doing the diff.
        self_counter = Counter(self_votes)
        self_counter.subtract(Counter(other_votes))
        self_asym = sorted(list(self_counter.elements()), reverse=True)

        other_counter = Counter(other_votes)
        other_counter.subtract(Counter(self_votes))
        other_asym = sorted(list(other_counter.elements()), reverse=True)

        if next(iter(self_asym), 0) > next(iter(other_asym), 0):
            return 1
        elif next(iter(self_asym), 0) < next(iter(other_asym), 0):
            return -1

        return 0
