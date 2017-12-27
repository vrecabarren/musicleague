from collections import defaultdict

from musicleague import app
from musicleague.persistence.models import League
from musicleague.persistence.models import RankingEntry
from musicleague.persistence.models import Round
from musicleague.persistence.models import ScoreboardEntry
from musicleague.persistence.models import Submission
from musicleague.persistence.models import User
from musicleague.persistence.models import Vote
from musicleague.persistence.statements import SELECT_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUES_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_FOR_USER
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_PLACED_FOR_USER
from musicleague.persistence.statements import SELECT_ROUND
from musicleague.persistence.statements import SELECT_ROUNDS_COUNT
from musicleague.persistence.statements import SELECT_ROUNDS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_SCOREBOARD
from musicleague.persistence.statements import SELECT_SUBMISSIONS_COUNT
from musicleague.persistence.statements import SELECT_SUBMISSIONS_FROM_USER
from musicleague.persistence.statements import SELECT_USER
from musicleague.persistence.statements import SELECT_USERS_COUNT
from musicleague.persistence.statements import SELECT_USERS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_VOTES_COUNT
from musicleague.persistence.statements import SELECT_VOTES_FROM_USER


def select_user(user_id):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USER, (str(user_id),))
                email, image_url, is_admin, joined, name, profile_bg = cur.fetchone()
                return User(user_id, email, image_url, is_admin, joined, name, profile_bg)
    except Exception as e:
        app.logger.warning('Failed SELECT_USER: %s', str(e), exc_info=e)


def select_users_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USERS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_USERS_COUNT: %s', str(e), exc_info=e)


def select_league(league_id, exclude_properties=None):
    if exclude_properties is None:
        exclude_properties = []

    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUE, (str(league_id),))
                league_tup = cur.fetchone()
                l = League(
                    id=str(league_id),
                    created=league_tup[0],
                    name=league_tup[1],
                    owner_id=league_tup[2]
                )

                if 'rounds' not in exclude_properties:
                    cur.execute(SELECT_ROUNDS_IN_LEAGUE, (str(league_id),))
                    for round_tup in cur.fetchall():
                        round_id = round_tup[0]
                        r = select_round(round_id)
                        r.league = l
                        l.submission_periods.append(r)

                cur.execute(SELECT_USERS_IN_LEAGUE, (str(league_id),))
                user_idx = {}
                uri_entry_idx = {}
                for user_tup in cur.fetchall():
                    user_id = user_tup[0]
                    u = select_user(user_id)
                    l.users.append(u)
                    user_idx[user_id] = u
                    if user_id == l.owner_id:
                        l.owner = u

                    if 'submissions' not in exclude_properties or 'rounds' not in exclude_properties:
                        for round in l.submission_periods:

                            cur.execute(SELECT_SUBMISSIONS_FROM_USER, (round.id, user_id))
                            created_tracks = cur.fetchone() if cur.rowcount else (None, None)
                            created, tracks = created_tracks
                            if created is not None and tracks is not None:
                                s = Submission(user=u, tracks=tracks.keys(), created=created)
                                round.submissions.append(s)
                                for uri, ranking in tracks.iteritems():
                                    uri_entry_idx[uri] = ScoreboardEntry(s, ranking, uri)

                for user in l.users:
                    if 'votes' not in exclude_properties or 'rounds' not in exclude_properties:
                        for round in l.submission_periods:

                            cur.execute(SELECT_VOTES_FROM_USER, (round.id, user.id))
                            created_votes = cur.fetchone() if cur.rowcount else (None, None)
                            created, votes = created_votes
                            if created is not None and votes is not None:
                                v = Vote(user=user, votes=votes, created=created)
                                round.votes.append(v)
                                for uri, weight in votes.iteritems():
                                    if uri not in uri_entry_idx:
                                        # TODO Deal with case where submitter was removed from league
                                        continue
                                    uri_entry_idx[uri].votes.append(v)

                if 'scoreboard' not in exclude_properties:
                    user_entry_idx = defaultdict(list)
                    for entry in uri_entry_idx.values():
                        user_entry_idx[entry.submission.user.id].append(entry)

                    cur.execute(SELECT_SCOREBOARD, (str(league_id),))
                    for scoreboard_tup in cur.fetchall():
                        user_id, rank = scoreboard_tup
                        u = user_idx.get(user_id, None)
                        le = RankingEntry(user=u, rank=rank)
                        le.entries = user_entry_idx[user_id]
                        l.scoreboard.add_entry(le, rank)

                return l
    except Exception as e:
        app.logger.warning('Failed SELECT_LEAGUE: %s', str(e), exc_info=e)


def select_leagues_for_user(user_id, exclude_properties=None):
    if exclude_properties is None:
        exclude_properties = []

    leagues = []
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_FOR_USER, (str(user_id),))
                for membership_tup in cur.fetchall():
                    league_id = membership_tup[0]
                    league = select_league(league_id, exclude_properties=exclude_properties)
                    leagues.append(league)
    except Exception as e:
        app.logger.warning('Failed SELECT_MEMBERSHIPS_FOR_USER: %s', str(e), exc_info=e)

    return leagues


def select_leagues_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUES_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_LEAGUES_COUNT: %s', str(e), exc_info=e)


def select_memberships_count(user_id):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_COUNT, (str(user_id),))
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_MEMBERSHIPS_COUNT: %s', str(e), exc_info=e)


def select_memberships_placed(user_id):
    placed = defaultdict(int)
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_PLACED_FOR_USER, (str(user_id),))
                for placed_tup in cur.fetchall():
                    rank, count = placed_tup
                    placed[rank] = count
    except Exception as e:
        app.logger.warning('Failed SELECT_MEMBERSHIPS_PLACED_FOR_USER: %s', str(e), exc_info=e)

    return placed


def select_round(round_id):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUND, (str(round_id),))
                round_tup = cur.fetchone()
                r = Round(
                    id=str(round_id),
                    created=round_tup[0],
                    description=round_tup[1],
                    name=round_tup[2],
                    playlist_url=round_tup[3],
                    submissions_due=round_tup[4],
                    votes_due=round_tup[5],
                )
                return r
    except Exception as e:
        app.logger.warning('Failed SELECT_ROUND: %s', str(e), exc_info=e)


def select_rounds_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUNDS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_ROUNDS_COUNT: %s', str(e), exc_info=e)


def select_submissions_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_SUBMISSIONS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_SUBMISSIONS_COUNT: %s', str(e), exc_info=e)


def select_votes_count():
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_VOTES_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.warning('Failed SELECT_VOTES_COUNT: %s', str(e), exc_info=e)
