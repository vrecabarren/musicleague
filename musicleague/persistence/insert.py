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
                    (str(user.id), user.email, user.image_url, user.joined, user.name, user.profile_background))
    except Exception as e:
        app.logger.error('Failed INSERT_USER', exc_info=e)


def insert_invited_user(user, league_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_INVITED_USER, (str(user.id), user.email, str(league_id)))
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
                if league.is_complete:
                    status = LeagueStatus.COMPLETE
                elif league.is_active:
                    status = LeagueStatus.IN_PROGRESS
                else:
                    status = LeagueStatus.COMPLETE

                cur.execute(
                    INSERT_LEAGUE,
                    (str(league.id), league.created, league.name,
                     str(league.owner.id), status))

                for user in league.users:
                    insert_membership(league, user)

                for round in league.submission_periods:
                    upsert_round(round)
                    for submission in round.submissions:
                        insert_submission(submission, insert_deps=False)
                    for vote in round.votes:
                        insert_vote(vote, insert_deps=False)

        upsert_league_preferences(league)

        for u in league.invited_users:
            insert_invited_user(u, str(league.id))

    except Exception as e:
        app.logger.error('Failed INSERT_LEAGUE', exc_info=e)


def insert_membership(league, user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(INSERT_MEMBERSHIP, (str(league.id), str(user.id)))
    except Exception as e:
        app.logger.error('Failed INSERT_MEMBERSHIP', exc_info=e)


def insert_round(round, insert_deps=True):
    try:
        if insert_deps:
            insert_league(round.league)

        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                if round.is_complete:
                    status = RoundStatus.COMPLETE
                else:
                    status = RoundStatus.CREATED

                cur.execute(
                    INSERT_ROUND,
                    (str(round.id), round.created, round.description, str(round.league.id),
                     round.name, status, round.submission_due_date,
                     round.vote_due_date))
                for submission in round.submissions:
                    insert_submission(submission, insert_deps=False)
                for vote in round.votes:
                    insert_vote(vote, insert_deps=False)
    except Exception as e:
        app.logger.error('Failed INSERT_ROUND', exc_info=e)


def insert_submission(submission, insert_deps=True):
    try:
        if insert_deps:
            insert_round(submission.submission_period)
            insert_user(submission.user)

        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                # Determine if user previously submitted
                cur.execute(
                    SELECT_SUBMISSIONS_FROM_USER,
                    (str(submission.submission_period.id),
                     str(submission.user.id)))
                if cur.rowcount > 0:
                    ranked_tracks = cur.fetchone()[1]

                    # Remove votes for previously submitted tracks
                    cur.execute(
                        DELETE_VOTES_FOR_URIS,
                        (str(submission.submission_period.id),
                         ranked_tracks.keys()))

                    # Remove previously submitted tracks
                    cur.execute(
                        DELETE_SUBMISSIONS,
                        (str(submission.submission_period.id),
                         str(submission.user.id)))

                # Insert tracks for new submission
                for track in submission.tracks:
                    cur.execute(
                        INSERT_SUBMISSION,
                        (submission.created,
                         str(submission.submission_period.id),
                         track, str(submission.user.id)))
    except Exception as e:
        app.logger.error('Failed INSERT_SUBMISSION', exc_info=e)


def insert_vote(vote, insert_deps=True):
    try:
        if insert_deps:
            insert_round(vote.submission_period)
            insert_user(vote.user)
            for submission in vote.submission_period.submissions:
                insert_submission(submission)

        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                # Remove previously submitted votes
                cur.execute(
                    DELETE_VOTES,
                    (str(vote.submission_period.id),
                     str(vote.user.id)))

                # Insert weights for new vote
                for spotify_uri, weight in vote.votes.iteritems():
                    cur.execute(
                        INSERT_VOTE,
                        (vote.created,
                         str(vote.submission_period.id),
                         spotify_uri, str(vote.user.id),
                         weight))
    except Exception as e:
        app.logger.error('Failed INSERT_VOTE', exc_info=e)
