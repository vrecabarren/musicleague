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
from musicleague.persistence.update import upsert_league_preferences


def insert_user(user):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                values = (user.id, user.email, user.image_url, user.joined,
                          user.name, user.profile_background)
                cur.execute(INSERT_USER, values)
    except Exception as e:
        app.logger.error('Failed INSERT_USER', exc_info=e)


def insert_invited_user(user, league_id):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                values = (user.id, user.email, league_id)
                cur.execute(INSERT_INVITED_USER, values)
    except Exception as e:
        app.logger.error('Failed INSERT_INVITED_USER', exc_info=e)


def insert_league(league):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                values = (league.id, league.created, league.name,
                          league.owner.id, LeagueStatus.CREATED)
                cur.execute(INSERT_LEAGUE, values)

        upsert_league_preferences(league)

        for user in league.users:
            insert_membership(league, user)

        for u in league.invited_users:
            insert_invited_user(u, league.id)

    except Exception as e:
        app.logger.error('Failed INSERT_LEAGUE', exc_info=e)


def insert_membership(league, user):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                values = (league.id, user.id)
                cur.execute(INSERT_MEMBERSHIP, values)
    except Exception as e:
        app.logger.error('Failed INSERT_MEMBERSHIP', exc_info=e)


def insert_round(round):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                values = (round.id, round.created, round.description, round.league.id,
                          round.name, RoundStatus.CREATED, round.submission_due_date,
                          round.vote_due_date)
                cur.execute(INSERT_ROUND, values)
    except Exception as e:
        app.logger.error('Failed INSERT_ROUND', exc_info=e)


def insert_submission(submission):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                # Determine if user previously submitted
                values = (submission.submission_period.id, submission.user.id)
                cur.execute(SELECT_SUBMISSIONS_FROM_USER, values)

                # If user has previous submissions, remove them
                if cur.rowcount > 0:
                    ranked_tracks = cur.fetchone()[1]

                    # Remove votes for previously submitted tracks
                    values = (submission.submission_period.id, ranked_tracks.keys())
                    cur.execute(DELETE_VOTES_FOR_URIS, values)

                    # Remove previously submitted tracks
                    values = (submission.submission_period.id, submission.user.id)
                    cur.execute(DELETE_SUBMISSIONS, values)

                # Insert tracks for new submission
                for uri in submission.tracks:
                    values = (submission.created, submission.submission_period.id,
                              uri, submission.user.id)
                    cur.execute(INSERT_SUBMISSION, values)
    except Exception as e:
        app.logger.error('Failed INSERT_SUBMISSION', exc_info=e)


def insert_vote(vote):
    try:
        with get_postgres_conn() as conn:
            with conn.cursor() as cur:
                # Remove previously submitted votes
                values = (vote.submission_period.id, vote.user.id)
                cur.execute(DELETE_VOTES, values)

                # Insert new votes
                for spotify_uri, weight in vote.votes.iteritems():
                    values = (vote.created, vote.submission_period.id,
                              spotify_uri, vote.user.id, weight)
                    cur.execute(INSERT_VOTE, values)
    except Exception as e:
        app.logger.error('Failed INSERT_VOTE', exc_info=e)
