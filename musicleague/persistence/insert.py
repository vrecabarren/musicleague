from musicleague import app
from musicleague.persistence.statements import INSERT_LEAGUE
from musicleague.persistence.statements import INSERT_ROUND
from musicleague.persistence.statements import INSERT_SUBMISSION
from musicleague.persistence.statements import INSERT_USER
from musicleague.persistence.statements import INSERT_VOTE
from musicleague.persistence.statements import SELECT_SUBMISSION_ID


def insert_user(user):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_USER,
                    (str(user.id), user.email, user.joined, user.name))
    except Exception as e:
        app.logger.warning('Failed INSERT_USER: %s', str(e))


def insert_league(league):
    try:
        insert_user(league.owner)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_LEAGUE,
                    (str(league.id), league.created, league.name,
                     str(league.owner.id)))
    except Exception as e:
        app.logger.warning('Failed INSERT_LEAGUE: %s', str(e))


def insert_round(round):
    try:
        insert_league(round.league)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_ROUND,
                    (str(round.id), round.created, round.description, str(round.league.id),
                     round.name, round.submission_due_date,
                     round.vote_due_date))
    except Exception as e:
        app.logger.warning('Failed INSERT_ROUND: %s', str(e))


def insert_submission(submission):
    try:
        insert_round(submission.submission_period)
        insert_user(submission.user)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                for track in submission.tracks:
                    cur.execute(
                        INSERT_SUBMISSION,
                        (submission.created,
                         str(submission.submission_period.id),
                         track, str(submission.user.id),
                         submission.updated or submission.created))
    except Exception as e:
        app.logger.warning('Failed INSERT_SUBMISSION: %s', str(e))


def insert_vote(vote):
    try:
        insert_round(vote.submission_period)
        insert_user(vote.user)
        for submission in vote.submission_period.submissions:
            insert_submission(submission)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                for spotify_uri, weight in vote.votes.iteritems():
                    #  Get the submission_id that this vote is targeted at
                    cur.execute(
                        SELECT_SUBMISSION_ID,
                        (str(vote.submission_period.id), spotify_uri))
                    submission_id = cur.fetchone()[0]

                    cur.execute(
                        INSERT_VOTE,
                        (vote.created, str(vote.submission_period.id),
                         submission_id, str(vote.user.id),
                         vote.updated or vote.created,
                         weight))
    except Exception as e:
        app.logger.warning('Failed INSERT_VOTE: %s', str(e))