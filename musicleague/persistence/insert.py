from musicleague import app
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.models import LeagueStatus
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.statements import DELETE_VOTES
from musicleague.persistence.statements import DELETE_VOTES_FOR_URIS
from musicleague.persistence.statements import INSERT_INVITED_USER
from musicleague.persistence.statements import INSERT_LEAGUE
from musicleague.persistence.statements import INSERT_MEMBERSHIP
from musicleague.persistence.statements import INSERT_ROUND
from musicleague.persistence.statements import INSERT_SUBMISSION
from musicleague.persistence.statements import INSERT_USER
from musicleague.persistence.statements import INSERT_VOTE
from musicleague.persistence.statements import DELETE_SUBMISSIONS
from musicleague.persistence.statements import SELECT_SUBMISSIONS_FROM_USER


def insert_user(user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_USER,
                    (user.id, user.email, user.image_url, user.joined, user.name, user.profile_background))
    except Exception as e:
        app.logger.error('Failed INSERT_USER', exc_info=e)


def insert_invited_user(user, league_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_INVITED_USER, (user.id, user.email, league_id))
    except Exception as e:
        app.logger.error('Failed INSERT_INVITED_USER', exc_info=e)


def insert_league(league):
    try:
        for u in league.users:
            insert_user(u)

        postgres_conn = get_postgres_conn()
        from musicleague.persistence.update import upsert_league_preferences
        from musicleague.persistence.update import upsert_round
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_LEAGUE,
                    (league.id, league.created, league.name,
                     league.owner.id, LeagueStatus.CREATED))

                for user in league.users:
                    insert_membership(league, user)

                for round in league.submission_periods:
                    upsert_round(round)
                    for submission in round.submissions:
                        insert_submission(submission)
                    for vote in round.votes:
                        insert_vote(vote)

        upsert_league_preferences(league)

        for u in league.invited_users:
            insert_invited_user(u, league.id)

    except Exception as e:
        app.logger.error('Failed INSERT_LEAGUE', exc_info=e)


def insert_membership(league, user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(INSERT_MEMBERSHIP, (league.id, user.id))
    except Exception as e:
        app.logger.error('Failed INSERT_MEMBERSHIP', exc_info=e)


def insert_round(round):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_ROUND,
                    (round.id, round.created, round.description, round.league.id,
                     round.name, RoundStatus.CREATED, round.submission_due_date,
                     round.vote_due_date))
                for submission in round.submissions:
                    insert_submission(submission)
                for vote in round.votes:
                    insert_vote(vote)
    except Exception as e:
        app.logger.error('Failed INSERT_ROUND', exc_info=e)


def insert_submission(submission):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                # Determine if user previously submitted
                cur.execute(
                    SELECT_SUBMISSIONS_FROM_USER,
                    (submission.submission_period.id,
                     submission.user.id))
                if cur.rowcount > 0:
                    ranked_tracks = cur.fetchone()[1]

                    # Remove votes for previously submitted tracks
                    cur.execute(
                        DELETE_VOTES_FOR_URIS,
                        (submission.submission_period.id,
                         ranked_tracks.keys()))

                    # Remove previously submitted tracks
                    cur.execute(
                        DELETE_SUBMISSIONS,
                        (submission.submission_period.id,
                         submission.user.id))

                # Insert tracks for new submission
                for track in submission.tracks:
                    cur.execute(
                        INSERT_SUBMISSION,
                        (submission.created,
                         submission.submission_period.id,
                         track, submission.user.id))
    except Exception as e:
        app.logger.error('Failed INSERT_SUBMISSION', exc_info=e)


def insert_vote(vote):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                # Remove previously submitted votes
                cur.execute(
                    DELETE_VOTES,
                    (vote.submission_period.id,
                     vote.user.id))

                # Insert weights for new vote
                for spotify_uri, weight in vote.votes.iteritems():
                    cur.execute(
                        INSERT_VOTE,
                        (vote.created,
                         vote.submission_period.id,
                         spotify_uri, vote.user.id,
                         weight))
    except Exception as e:
        app.logger.error('Failed INSERT_VOTE', exc_info=e)
