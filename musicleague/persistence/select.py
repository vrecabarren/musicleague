from musicleague import app
from musicleague.models import User
from musicleague.persistence.models import RankingEntry
from musicleague.persistence.models import Submission
from musicleague.persistence.models import Vote
from musicleague.persistence.statements import SELECT_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUES_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_COUNT
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
                u = User()
                u.id = user_id
                u.email, u.image_url, u.joined, u.name, u.profile_background = cur.fetchone()
                return u
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


def select_league(league_id):
    try:
        from musicleague import postgres_conn
        from musicleague.persistence.models import League as NewLeague
        from musicleague.persistence.models import Round
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUE, (str(league_id),))
                league_tup = cur.fetchone()
                l = NewLeague(
                    id=str(league_id),
                    created=league_tup[0],
                    name=league_tup[1],
                    owner_id=league_tup[2]
                )

                cur.execute(SELECT_ROUNDS_IN_LEAGUE, (str(league_id),))
                for round_tup in cur.fetchall():
                    round_id = round_tup[0]
                    r = select_round(round_id)
                    r.league = l
                    l.submission_periods.append(r)

                cur.execute(SELECT_USERS_IN_LEAGUE, (str(league_id),))
                user_idx = {}
                for user_tup in cur.fetchall():
                    user_id = user_tup[0]
                    u = select_user(user_id)
                    l.users.append(u)
                    user_idx[user_id] = u
                    if user_id == l.owner_id:
                        l.owner = u

                    for round in l.submission_periods:

                        cur.execute(SELECT_SUBMISSIONS_FROM_USER, (round.id, user_id))
                        created, tracks = cur.fetchone() if cur.rowcount else None, None
                        if created is not None:
                            s = Submission(user=u, tracks=tracks, created=created)
                            round.submissions.append(s)

                        cur.execute(SELECT_VOTES_FROM_USER, (round.id, user_id))
                        created, votes = cur.fetchone() if cur.rowcount else None, None
                        if created is not None:
                            v = Vote(user=u, votes=votes, created=created)
                            round.votes.append(v)

                cur.execute(SELECT_SCOREBOARD, (str(league_id),))
                for score_tup in cur.fetchall():
                    user_id, rank = score_tup
                    u = user_idx.get(user_id, None)
                    le = RankingEntry(user=u, rank=rank)
                    l.scoreboard.add_entry(le, rank)

                app.logger.warning('Created league scoreboard: %s', l.scoreboard._rankings)
                app.logger.warning('League scoreboard top: %s', l.scoreboard.top)

                return l
    except Exception as e:
        app.logger.warning('Failed SELECT_LEAGUE: %s', str(e), exc_info=e)


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


def select_round(round_id):
    try:
        from musicleague import postgres_conn
        from musicleague.persistence.models import Round
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
