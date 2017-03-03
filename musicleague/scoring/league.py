from itertools import groupby

from musicleague.models import RankingEntry
from musicleague.models import Scoreboard
from musicleague.scoring import EntrySortKey


def calculate_league_scoreboard(league):
    """ Calculate and store scoreboard on league. The scoreboard consists of
    a dict where keys are the rankings for each entry. The values for the
    scoreboard are lists of entries. In most cases, the list will have a
    length of 1; however, if two or more users are tied, the list will grow
    in length for a particular ranking.
    """
    league.scoreboard = Scoreboard()

    # Create a RankingEntry for each song with corresponding User
    entries = {user.id: RankingEntry(user=user)
               for user in league.users}

    # Get song entries for each entry
    for round in league.submission_periods:
        for entry_list in round.scoreboard.rankings.values():
            for entry in entry_list:
                user_id = entry.submission.user.id
                if user_id in entries:
                    entries[user_id].entries.append(entry)

    # Sort entries on each entry by number of points awarded
    for entry in entries.values():
        entry.entries = sorted(entry.entries,
                               key=lambda x: x.points,
                               reverse=True)

    # Rank entries and assign to league scoreboard with string keys
    rankings = rank_entries(entries.values())
    for rank, entries in rankings.iteritems():
        league.scoreboard._rankings[str(rank)] = entries

    league.save()
    return league


def rank_entries(entries):
    """ Given a list of RankingEntry entities, return a dict where the key
    is the ranking and the value is a list of RankingEntry entities for that
    ranking. In general, we aim for this list to have a length of 1 for each
    key since a list with length > 1 means there is a tie for the ranking.
    """
    entries = sorted(entries, key=RankingEntrySortKey, reverse=True)
    grouped_entries = groupby(entries, key=RankingEntrySortKey)
    entries = [list(group) for _, group in grouped_entries]

    # Index entries by ranking
    return {(i + 1): entries for i, entries in enumerate(entries)}


class RankingEntrySortKey(EntrySortKey):

    def _ordered_cmp(self, other):
        _cmp_order = [
            self._cmp_entry_points
        ]

        for _cmp in _cmp_order:
            diff = _cmp(other)
            if diff != 0:
                return diff

        return 0

    def _cmp_entry_points(self, other):
        """ Compare two RankingEntry objects based on the raw number of
        points.
        """
        if self.obj.points > other.points:
            return 1
        elif self.obj.points < other.points:
            return -1
        return 0
