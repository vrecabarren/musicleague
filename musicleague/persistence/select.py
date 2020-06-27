from collections import defaultdict
from pytz import utc

from musicleague.persistence import get_postgres_conn
from musicleague.persistence.models import Bot
from musicleague.persistence.models import InvitedUser
from musicleague.persistence.models import League
from musicleague.persistence.models import LeaguePreferences
from musicleague.persistence.models import RankingEntry
from musicleague.persistence.models import Round
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.models import ScoreboardEntry
from musicleague.persistence.models import Submission
from musicleague.persistence.models import User
from musicleague.persistence.models import UserPreferences
from musicleague.persistence.models import Vote
from musicleague.persistence.statements import SELECT_BOT
from musicleague.persistence.statements import SELECT_INVITED_USERS_COUNT
from musicleague.persistence.statements import SELECT_INVITED_USERS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUE_ID_FOR_ROUND
from musicleague.persistence.statements import SELECT_LEAGUE_PREFERENCES
from musicleague.persistence.statements import SELECT_LEAGUES_COUNT
from musicleague.persistence.statements import SELECT_LEAGUES_FOR_USER
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_PLACED_FOR_USER
from musicleague.persistence.statements import SELECT_PREVIOUS_SUBMISSION
from musicleague.persistence.statements import SELECT_ROUND
from musicleague.persistence.statements import SELECT_ROUNDS_COUNT
from musicleague.persistence.statements import SELECT_ROUNDS_FOR_LEAGUE
from musicleague.persistence.statements import SELECT_ROUNDS_IN_LEAGUE_WITH_STATUS
from musicleague.persistence.statements import SELECT_SCOREBOARD
from musicleague.persistence.statements import SELECT_SUBMISSIONS
from musicleague.persistence.statements import SELECT_SUBMISSIONS_COUNT
from musicleague.persistence.statements import SELECT_USER
from musicleague.persistence.statements import SELECT_USER_BY_EMAIL
from musicleague.persistence.statements import SELECT_USER_PREFERENCES
from musicleague.persistence.statements import SELECT_USERS_COUNT
from musicleague.persistence.statements import SELECT_USERS_FOR_LEAGUE
from musicleague.persistence.statements import SELECT_VOTES
from musicleague.persistence.statements import SELECT_VOTES_COUNT


def select_bot(bot_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (bot_id,)
            cur.execute(SELECT_BOT, values)
            if cur.rowcount < 1:
                return None

            access_token, refresh_token, expires_at = cur.fetchone()
            bot = Bot(id=bot_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
            return bot


def select_user(user_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_USER, (user_id,))
            if cur.rowcount < 1:
                return None

            email, image_url, is_admin, joined, name, profile_bg = cur.fetchone()
            u = User(user_id, email, image_url, is_admin, joined, name, profile_bg)

            # TODO This could be done in one fetch with a join
            u.preferences = select_user_preferences(user_id)

            return u


def select_user_by_email(user_email):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_USER_BY_EMAIL, (user_email,))
            if cur.rowcount < 1:
                return None

            user_id, image_url, is_admin, joined, name, profile_bg = cur.fetchone()
            u = User(user_id, user_email, image_url, is_admin, joined, name, profile_bg)

            # TODO This could be done in one fetch with a join
            u.preferences = select_user_preferences(user_id)

            return u


def select_user_preferences(user_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_USER_PREFERENCES, (user_id,))
            up = UserPreferences()
            if cur.rowcount < 1:
                return up

            (up.owner_all_users_submitted_notifications,
             up.owner_all_users_voted_notifications,
             up.owner_user_left_notifications,
             up.owner_user_submitted_notifications,
             up.owner_user_voted_notifications,
             up.user_added_to_league_notifications,
             up.user_playlist_created_notifications,
             up.user_removed_from_league_notifications,
             up.user_submit_reminder_notifications,
             up.user_vote_reminder_notifications) = cur.fetchone()

            return up


def select_users_count():
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_USERS_COUNT)
            return cur.fetchone()[0]


def select_invited_users_count():
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_INVITED_USERS_COUNT)
            return cur.fetchone()[0]


def select_league(league_id, exclude_properties=None):
    if exclude_properties is None:
        exclude_properties = []

    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_LEAGUE, (league_id,))
            if cur.rowcount < 1:
                return None

            created, name, owner_id, status = cur.fetchone()
            league = League(id=league_id, created=created, name=name, owner_id=owner_id, status=status)
            league.preferences = select_league_preferences(league_id)

            user_idx = {}
            cur.execute(SELECT_USERS_FOR_LEAGUE, (league_id,))
            for user_tup in cur.fetchall():
                user_id, email, image_url, is_admin, joined, name, profile_bg = user_tup
                user = User(user_id, email,image_url, is_admin, joined, name, profile_bg)
                user.preferences = select_user_preferences(user_id)
                league.users.append(user)
                user_idx[user_id] = user
                if user_id == league.owner_id:
                    league.owner = user

            # If owner is not participating in league, retrieve
            league.owner = league.owner or select_user(owner_id)

            if 'invited_users' not in exclude_properties:
                cur.execute(SELECT_INVITED_USERS_IN_LEAGUE, (league_id,))
                for user_tup in cur.fetchall():
                    invite_id, email = user_tup
                    league.invited_users.append(InvitedUser(invite_id, email, league_id))

            round_uri_entry_idx = defaultdict(dict)
            if 'rounds' not in exclude_properties:
                cur.execute(SELECT_ROUNDS_FOR_LEAGUE, (league_id,))
                for round_tup in cur.fetchall():
                    r = Round(
                        id=round_tup[0],
                        league_id=league_id,
                        created=round_tup[1],
                        description=round_tup[2],
                        name=round_tup[3],
                        playlist_url=round_tup[4],
                        status=round_tup[5],
                        submissions_due=utc.localize(round_tup[6]),
                        votes_due=utc.localize(round_tup[7]),
                    )
                    r.league = league
                    league.submission_periods.append(r)

            for round in league.submission_periods:
                if 'submissions' not in exclude_properties:
                    cur.execute(SELECT_SUBMISSIONS, (round.id,))
                    for submission_tup in cur.fetchall():
                        created, user_id, revision, tracks = submission_tup
                        submitter = user_idx.get(user_id, None)
                        if submitter is None:
                            submitter = select_user(user_id)
                            if submitter is None:
                                continue
                            user_idx[user_id] = submitter

                        # TODO Retrieve comments field
                        s = Submission(user=submitter, tracks=tracks.keys(), comments=[], created=created)
                        s.count = revision
                        s.league = league
                        s.submission_period = round
                        round.submissions.append(s)
                        for uri, ranking in tracks.iteritems():
                            entry = ScoreboardEntry(uri=uri, submission=s, place=ranking)
                            round_uri_entry_idx[round.id][uri] = entry

                if 'votes' not in exclude_properties:
                    cur.execute(SELECT_VOTES, (round.id,))
                    for vote_tup in cur.fetchall():
                        created, user_id, votes, comments = vote_tup
                        voter = user_idx.get(user_id, None)
                        if voter is None:
                            voter = select_user(user_id)
                            if voter is None:
                                continue
                            user_idx[user_id] = voter

                        v = Vote(user=voter, votes=votes, comments=comments, created=created)
                        v.league = league
                        v.submission_period = round
                        round.votes.append(v)
                        for uri, weight in votes.iteritems():
                            # TODO Deal with case where submitter was removed from league
                            if round.id not in round_uri_entry_idx:
                                continue

                            if uri not in round_uri_entry_idx[round.id]:
                                continue

                            round_uri_entry_idx[round.id][uri].votes.append(v)

                    # For each submission, sort votes by points descending
                    for round_id, entries in round_uri_entry_idx.iteritems():
                        for uri, entry in entries.iteritems():
                            entry.votes.sort(key=lambda x:x.votes[uri], reverse=True)

            if 'scoreboard' not in exclude_properties:
                user_entry_idx = defaultdict(list)
                for round in league.submission_periods:
                    entries_by_uri = round_uri_entry_idx[round.id]
                    for entry in sorted(entries_by_uri.values(), key=lambda x: x.points, reverse=True):
                        round.scoreboard.add_entry(entry, entry.place)
                        if round.is_complete:
                            user_entry_idx[entry.submission.user.id].append(entry)

                if len(user_entry_idx):
                    cur.execute(SELECT_SCOREBOARD, (league_id,))
                    for scoreboard_tup in cur.fetchall():
                        user_id, rank = scoreboard_tup
                        u = user_idx.get(user_id, None)
                        le = RankingEntry(league=league, user=u, place=rank)
                        le.entries = user_entry_idx[user_id]
                        league.scoreboard.add_entry(le, rank)

            return league


def select_league_preferences(league_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_LEAGUE_PREFERENCES, (league_id,))
            if cur.rowcount < 1:
                return None

            lp = LeaguePreferences()
            (lp.track_count, lp.point_bank_size, lp.max_points_per_song,
             lp.downvote_bank_size, lp.max_downvotes_per_song,
             lp.submission_reminder_time, lp.vote_reminder_time) = cur.fetchone()
            return lp


def select_leagues_for_user(user_id, exclude_properties=None):
    if exclude_properties is None:
        exclude_properties = []

    leagues = []
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_LEAGUES_FOR_USER, (user_id, user_id))
            for league_tup in cur.fetchall():
                league_id, created, name, owner_id, status = league_tup
                league = League(id=league_id, created=created, name=name, owner_id=owner_id, status=status)

                cur.execute(SELECT_USERS_FOR_LEAGUE, (league_id,))
                for user_tup in cur.fetchall():
                    user_id, email, image_url, is_admin, joined, name, profile_bg = user_tup
                    user = User(user_id, email,image_url, is_admin, joined, name, profile_bg)
                    league.users.append(user)
                    if user_id == league.owner_id:
                        league.owner = user

                # If owner is not participating in league, retrieve
                league.owner = league.owner or select_user(owner_id)

                leagues.append(league)

    return leagues


def select_leagues_count():
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_LEAGUES_COUNT)
            return cur.fetchone()[0]


def select_memberships_count(user_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_MEMBERSHIPS_COUNT, (user_id,))
            return cur.fetchone()[0]


def select_memberships_placed(user_id):
    placed = defaultdict(int)
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_MEMBERSHIPS_PLACED_FOR_USER, (user_id,))
            for placed_tup in cur.fetchall():
                rank, count = placed_tup
                placed[rank] = count

    return placed


def select_round(round_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_ROUND, (round_id,))
            if cur.rowcount < 1:
                return None

            round_tup = cur.fetchone()
            return Round(
                id=round_id,
                league_id=round_tup[0],
                created=round_tup[1],
                description=round_tup[2],
                name=round_tup[3],
                playlist_url=round_tup[4],
                status=round_tup[5],
                submissions_due=utc.localize(round_tup[6]),
                votes_due=utc.localize(round_tup[7]),
            )


def select_league_id_for_round(round_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_LEAGUE_ID_FOR_ROUND, (round_id,))
            return cur.fetchone()[0]


def select_rounds_count():
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_ROUNDS_COUNT)
            return cur.fetchone()[0]


def select_rounds_incomplete_count(league_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_ROUNDS_IN_LEAGUE_WITH_STATUS, (league_id, RoundStatus.CREATED))
            return cur.rowcount


def select_previous_submission(user_id, spotify_uri, exclude_league_id):
    created, league = None, None
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_PREVIOUS_SUBMISSION, (user_id, spotify_uri, exclude_league_id))
            if cur.rowcount > 0:
                created, league = cur.fetchone()
    return created, league


def select_submissions_count():
    submissions_count = -1
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_SUBMISSIONS_COUNT)
            if cur.rowcount > 0:
                submissions_count = cur.fetchone()[0]
    return submissions_count


def select_votes_count():
    votes_count = -1
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_VOTES_COUNT)
            if cur.rowcount > 0:
                votes_count = cur.fetchone()[0]
    return votes_count
