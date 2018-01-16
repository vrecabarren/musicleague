from musicleague import app
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.models import Round
from musicleague.persistence.models import RoundStatus
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
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPDATE_USER,
                    (user.email, user.image_url, user.name,
                     user.profile_background, user.is_admin,
                     str(user.id)))
    except Exception as e:
        app.logger.error('Failed UPDATE_USER', exc_info=e)


def upsert_user(user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPSERT_USER,
                    (str(user.id),
                     user.email,
                     user.image_url,
                     user.joined,
                     user.name,
                     user.profile_background,
                     user.is_admin))
    except Exception as e:
        app.logger.error('Failed UPSERT_USER', exc_info=e)


def upsert_bot(bot):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPSERT_BOT,
                    (str(bot.id),
                     bot.access_token,
                     bot.refresh_token,
                     bot.expires_at))
    except Exception as e:
        app.logger.error('Failed UPSERT_BOT', exc_info=e)


def upsert_user_preferences(user):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPSERT_USER_PREFERENCES,
                    (str(user.id),
                     user.preferences.owner_all_users_submitted_notifications,
                     user.preferences.owner_all_users_voted_notifications,
                     user.preferences.owner_user_left_notifications,
                     user.preferences.owner_user_submitted_notifications,
                     user.preferences.owner_user_voted_notifications,
                     user.preferences.user_added_to_league_notifications,
                     user.preferences.user_playlist_created_notifications,
                     user.preferences.user_removed_from_league_notifications,
                     user.preferences.user_submit_reminder_notifications,
                     user.preferences.user_vote_reminder_notifications))
    except Exception as e:
        app.logger.error('Failed UPSERT_USER_PREFERENCES', exc_info=e)


def update_league(league):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_LEAGUE, (league.name, league.status, str(league.id)))
    except Exception as e:
        app.logger.error('Failed UPDATE_LEAGUE', exc_info=e)


def upsert_league_preferences(league):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPSERT_LEAGUE_PREFERENCES,
                    (str(league.id), league.preferences.track_count,
                     league.preferences.point_bank_size,
                     league.preferences.max_points_per_song,
                     league.preferences.downvote_bank_size,
                     league.preferences.max_downvotes_per_song,
                     league.preferences.submission_reminder_time,
                     league.preferences.vote_reminder_time))
    except Exception as e:
        app.logger.error('Failed UPSERT_LEAGUE_PREFERENCES', exc_info=e)


def update_league_status(league, status):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_LEAGUE_STATUS, (status, str(league.id)))
    except Exception as e:
        app.logger.error('Failed UPDATE_LEAGUE_STATUS', exc_info=e)


def update_membership_rank(league, user, rank):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_MEMBERSHIP_RANK, (rank, str(league.id), str(user.id)))
    except Exception as e:
        app.logger.error('Failed UPDATE_MEMBERSHIP_RANK', exc_info=e)


def update_round(round):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(
                    UPDATE_ROUND,
                    (round.description, round.name, round.status, round.submission_due_date, round.vote_due_date, round.id))
    except Exception as e:
        app.logger.error('Failed UPDATE_ROUND', exc_info=e)


def upsert_round(round):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                if type(round) is Round:
                    league_id = round.league_id
                    status = round.status
                else:
                    league_id = str(round.league.id)
                    status = RoundStatus.COMPLETE if round.is_complete else RoundStatus.CREATED

                cur.execute(
                    UPSERT_ROUND,
                    (str(round.id), round.created, round.description, league_id, round.name,
                     round.playlist_url, status, round.submission_due_date, round.vote_due_date))
    except Exception as e:
        app.logger.error('Failed UPSERT_ROUND', exc_info=e)


def update_round_status(round, status):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_ROUND_STATUS, (status, str(round.id)))
    except Exception as e:
        app.logger.error('Failed UPDATE_ROUND_STATUS', exc_info=e)


def update_submission_rank(round, spotify_uri, rank):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(UPDATE_SUBMISSION_RANK, (rank, str(round.id), spotify_uri))
    except Exception as e:
        app.logger.error('Failed UPDATE_SUBMISSION_RANK', exc_info=e)
