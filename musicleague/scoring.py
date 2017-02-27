from collections import defaultdict

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
    rankings = rank_entries(entries)
    for rank, entries in rankings.iteritems():
        round.scoreboard._rankings[str(rank)] = entries

    round.save()
    return round


def rank_entries(entries):
    rankings = {}

    # Determine ranking for each ScoreboardEntry
    entries_by_points = defaultdict(list)
    for _, entry in entries.iteritems():
        entries_by_points[entry.points].append(entry)

    # Ranking entries by number of points
    point_ranking = sorted(entries_by_points.keys(), reverse=True)
    ranked_by_points = []
    for i in range(len(point_ranking)):
        points_for_ranking = point_ranking[i]
        rank_entries = entries_by_points[points_for_ranking]
        ranked_by_points.append(rank_entries)

    # Break ties by number of voters
    ranked_by_voters = []
    for i in range(len(ranked_by_points)):
        entries = ranked_by_points[i]
        if len(entries) == 1:
            ranked_by_voters.append(entries)
            continue

        # When we encounter a tie, group the tied members by number of voters
        from itertools import groupby
        entries = sorted(entries, key=lambda x: len(x.votes), reverse=True)
        entries = groupby(entries, key=lambda x: len(x.votes))
        for _, group in entries:
            ranked_by_voters.append(list(group))

        import logging
        logging.warning(ranked_by_voters)

    # Index entries by ranking
    for i in range(len(ranked_by_voters)):
        rankings[i + 1] = ranked_by_voters[i]

    return rankings


def calculate_league_scoreboard(league):
    pass
