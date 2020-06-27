from musicleague.persistence import get_postgres_conn
from musicleague.persistence.models import LeagueStatus
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
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (user.id, user.email, user.image_url, user.joined,
                      user.name, user.profile_background)
            cur.execute(INSERT_USER, values)


def insert_invited_user(user, league_id):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (user.id, user.email, league_id)
            cur.execute(INSERT_INVITED_USER, values)


def insert_league(league):
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


def insert_membership(league, user):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (league.id, user.id)
            cur.execute(INSERT_MEMBERSHIP, values)


def insert_round(round):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (round.id, round.created, round.description, round.league.id,
                      round.name, round.status, round.submission_due_date,
                      round.vote_due_date)
            cur.execute(INSERT_ROUND, values)


def insert_submission(submission):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            # Determine if user previously submitted
            values = (submission.submission_period.id, submission.user.id)
            cur.execute(SELECT_SUBMISSIONS_FROM_USER, values)

            # If user has previous submissions, remove them
            if cur.rowcount > 0:
                ranked_tracks = cur.fetchone()[2]

                # Remove votes for previously submitted tracks
                values = (submission.submission_period.id, ranked_tracks.keys())
                cur.execute(DELETE_VOTES_FOR_URIS, values)

                # Remove previously submitted tracks
                values = (submission.submission_period.id, submission.user.id)
                cur.execute(DELETE_SUBMISSIONS, values)

            # Insert tracks for new submission
            for uri in submission.tracks:
                # TODO Insert comments
                values = (submission.created, submission.submission_period.id,
                          uri, submission.user.id, submission.count)
                cur.execute(INSERT_SUBMISSION, values)


def insert_vote(vote):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            # Remove previously submitted votes
            values = (vote.submission_period.id, vote.user.id)
            cur.execute(DELETE_VOTES, values)

            to_persist = set(vote.votes.keys() + vote.comments.keys())

            # Insert new votes
            for spotify_uri in to_persist:
                weight = vote.votes.get(spotify_uri, 0)
                comment = vote.comments.get(spotify_uri, '')
                if not (weight or comment):
                    continue

                values = (vote.created, vote.submission_period.id,
                          spotify_uri, vote.user.id, weight, comment)
                cur.execute(INSERT_VOTE, values)
