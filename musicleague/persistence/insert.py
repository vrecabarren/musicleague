from musicleague import app
from musicleague.persistence.statements import DELETE_SUBMISSIONS
from musicleague.persistence.statements import DELETE_VOTES
from musicleague.persistence.statements import INSERT_LEAGUE
from musicleague.persistence.statements import INSERT_MEMBERSHIP
from musicleague.persistence.statements import INSERT_ROUND
from musicleague.persistence.statements import INSERT_SUBMISSION
from musicleague.persistence.statements import INSERT_USER
from musicleague.persistence.statements import INSERT_VOTE


def insert_user(user):
    try:
        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_USER,
                    (str(user.id), user.email, user.image_url, user.joined, user.name, user.profile_background))
    except Exception as e:
        app.logger.warning('Failed INSERT_USER: %s', str(e), exc_info=e)


def insert_league(league):
    try:
        for u in league.users:
            insert_user(u)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_LEAGUE,
                    (str(league.id), league.created, league.name,
                     str(league.owner.id)))

                for u in league.users:
                    cur.execute(INSERT_MEMBERSHIP, (str(league.id), str(u.id)))

                for round in league.submission_periods:
                    insert_round(round, insert_deps=False)

    except Exception as e:
        app.logger.warning('Failed INSERT_LEAGUE: %s', str(e), exc_info=e)


def insert_round(round, insert_deps=True):
    try:
        if insert_deps:
            insert_league(round.league)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    INSERT_ROUND,
                    (str(round.id), round.created, round.description, str(round.league.id),
                     round.name, round.submission_due_date,
                     round.vote_due_date))
                for submission in round.submissions:
                    insert_submission(submission, insert_deps=False)
                for vote in round.votes:
                    insert_vote(vote, insert_deps=False)
    except Exception as e:
        app.logger.warning('Failed INSERT_ROUND: %s', str(e), exc_info=e)


def insert_submission(submission, insert_deps=True):
    try:
        if insert_deps:
            insert_round(submission.submission_period)
            insert_user(submission.user)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                for track in submission.tracks:
                    cur.execute(
                        INSERT_SUBMISSION,
                        ((submission.updated or submission.created),
                         str(submission.submission_period.id),
                         track, str(submission.user.id)))
    except Exception as e:
        app.logger.warning('Failed INSERT_SUBMISSION: %s', str(e), exc_info=e)


def insert_vote(vote, insert_deps=True):
    try:
        if insert_deps:
            insert_round(vote.submission_period)
            insert_user(vote.user)
            for submission in vote.submission_period.submissions:
                insert_submission(submission)

        from musicleague import postgres_conn
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                for spotify_uri, weight in vote.votes.iteritems():
                    cur.execute(
                        INSERT_VOTE,
                        ((vote.updated or vote.created),
                         str(vote.submission_period.id),
                         spotify_uri, str(vote.user.id),
                         weight))
    except Exception as e:
        app.logger.warning('Failed INSERT_VOTE: %s', str(e), exc_info=e)