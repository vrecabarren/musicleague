from musicleague.persistence import get_postgres_conn
from musicleague.persistence.statements import UPDATE_LEAGUE
from musicleague.persistence.statements import UPDATE_LEAGUE_STATUS
from musicleague.persistence.statements import UPDATE_MEMBERSHIP_RANK
from musicleague.persistence.statements import UPDATE_ROUND
from musicleague.persistence.statements import UPDATE_ROUND_STATUS
from musicleague.persistence.statements import UPDATE_SUBMISSION_RANK
from musicleague.persistence.statements import UPDATE_USER
from musicleague.persistence.statements import UPSERT_BOT
from musicleague.persistence.statements import UPSERT_LEAGUE_PREFERENCES
from musicleague.persistence.statements import UPSERT_ROUND
from musicleague.persistence.statements import UPSERT_USER
from musicleague.persistence.statements import UPSERT_USER_PREFERENCES


def update_user(user):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (user.email, user.image_url, user.name,
                      user.profile_background, user.is_admin, user.id)
            cur.execute(UPDATE_USER, values)


def upsert_user(user):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (user.id, user.email, user.image_url, user.joined,
                      user.name, user.profile_background, user.is_admin)
            cur.execute(UPSERT_USER, values)


def upsert_bot(bot):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (bot.id, bot.access_token, bot.refresh_token, bot.expires_at)
            cur.execute(UPSERT_BOT, values)


def upsert_user_preferences(user):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (user.id,
                      user.preferences.owner_all_users_submitted_notifications,
                      user.preferences.owner_all_users_voted_notifications,
                      user.preferences.owner_user_left_notifications,
                      user.preferences.owner_user_submitted_notifications,
                      user.preferences.owner_user_voted_notifications,
                      user.preferences.user_added_to_league_notifications,
                      user.preferences.user_playlist_created_notifications,
                      user.preferences.user_removed_from_league_notifications,
                      user.preferences.user_submit_reminder_notifications,
                      user.preferences.user_vote_reminder_notifications)
            cur.execute(UPSERT_USER_PREFERENCES, values)


def update_league(league):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (league.name, league.status, league.id)
            cur.execute(UPDATE_LEAGUE, values)


def upsert_league_preferences(league):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (league.id,
                      league.preferences.track_count,
                      league.preferences.point_bank_size,
                      league.preferences.max_points_per_song,
                      league.preferences.downvote_bank_size,
                      league.preferences.max_downvotes_per_song,
                      league.preferences.submission_reminder_time,
                      league.preferences.vote_reminder_time)
            cur.execute(UPSERT_LEAGUE_PREFERENCES, values)


def update_league_status(league_id, status):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (status, league_id)
            cur.execute(UPDATE_LEAGUE_STATUS, values)


def update_membership_rank(league, user, rank):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (rank, league.id, user.id)
            cur.execute(UPDATE_MEMBERSHIP_RANK, values)


def update_round(round):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (round.description, round.name, round.status,
                      round.submission_due_date, round.vote_due_date, round.id)
            cur.execute(UPDATE_ROUND, values)


def upsert_round(round):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (round.id, round.created, round.description, round.league_id,
                      round.name, round.playlist_url, round.status,
                      round.submission_due_date, round.vote_due_date)
            cur.execute(UPSERT_ROUND, values)


def update_round_status(round, status):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (status, round.id)
            cur.execute(UPDATE_ROUND_STATUS, values)


def update_submission_rank(round, spotify_uri, rank):
    with get_postgres_conn() as conn:
        with conn.cursor() as cur:
            values = (rank, round.id, spotify_uri)
            cur.execute(UPDATE_SUBMISSION_RANK, values)
