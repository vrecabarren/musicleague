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
    entries = {}
    for submission in round.submissions:
        for uri in submission.tracks:
            entries[uri] = ScoreboardEntry(uri=uri, submission=submission)

    # Get Votes for each song
    for vote in round.votes:
        for uri, points in vote.votes.iteritems():
            if points > 0:
                entries[uri].votes.append(vote)

    # Sort votes by number of points awarded
    for entry in entries.values():
        entry.votes = sorted(entry.votes,
                             key=lambda x: x.votes[entry.uri],
                             reverse=True)

    # Determine ranking for each ScoreboardEntry
    entries_by_points = defaultdict(list)
    for _, entry in entries.iteritems():
        entries_by_points[entry.points].append(entry)

    # Create Scoreboard. Though rankings use ints, keys must be strings.
    point_ranking = sorted(entries_by_points.keys(), reverse=True)
    for i in range(len(point_ranking)):
        points_for_ranking = point_ranking[i]
        rank_entries = entries_by_points[points_for_ranking]
        round.scoreboard._rankings[str(i + 1)] = rank_entries

    round.save()
    return round


def calculate_league_scoreboard(league):
    pass
