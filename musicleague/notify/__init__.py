
from musicleague.notify.email import owner_all_users_submitted_email
from musicleague.notify.email import owner_all_users_voted_email
from musicleague.notify.email import owner_user_submitted_email
from musicleague.notify.email import owner_user_voted_email
from musicleague.notify.email import user_added_to_league_email
from musicleague.notify.email import user_invited_to_league_email
from musicleague.notify.email import user_last_to_submit_email
from musicleague.notify.email import user_last_to_vote_email
from musicleague.notify.email import user_playlist_created_email
from musicleague.notify.email import user_removed_from_league_email
from musicleague.notify.email import user_submit_reminder_email
from musicleague.notify.email import user_vote_reminder_email

from musicleague.notify.messenger import owner_all_users_submitted_messenger
from musicleague.notify.messenger import owner_all_users_voted_messenger
from musicleague.notify.messenger import owner_user_submitted_messenger
from musicleague.notify.messenger import owner_user_voted_messenger
from musicleague.notify.messenger import user_added_to_league_messenger
from musicleague.notify.messenger import user_last_to_submit_messenger
from musicleague.notify.messenger import user_last_to_vote_messenger
from musicleague.notify.messenger import user_playlist_created_messenger
from musicleague.notify.messenger import user_removed_from_league_messenger
from musicleague.notify.messenger import user_submit_reminder_messenger
from musicleague.notify.messenger import user_vote_reminder_messenger


def owner_all_users_submitted_notification(submission_period):
    if not submission_period:
        return False

    owner = submission_period.league.owner
    if not owner:
        return False

    if not owner.preferences.owner_all_users_submitted_notifications:
        return False

    owner_all_users_submitted_email(owner, submission_period)
    owner_all_users_submitted_messenger(owner, submission_period)
    return True


def owner_user_submitted_notification(submission):
    if not submission:
        return False

    owner = submission.league.owner
    if not owner:
        return False

    if not owner.preferences.owner_user_submitted_notifications:
        return False

    owner_user_submitted_email(owner, submission)
    owner_user_submitted_messenger(owner, submission)
    return True


def owner_all_users_voted_notification(submission_period):
    if not submission_period:
        return

    owner = submission_period.league.owner
    if not owner:
        return

    if not owner.preferences.owner_all_users_voted_notifications:
        return

    owner_all_users_voted_email(owner, submission_period)
    owner_all_users_voted_messenger(owner, submission_period)


def owner_user_voted_notification(vote):
    if not vote:
        return

    owner = vote.league.owner
    if not owner:
        return

    if not owner.preferences.owner_user_voted_notifications:
        return

    owner_user_voted_email(owner, vote)
    owner_user_voted_messenger(owner, vote)


def user_added_to_league_notification(user, league):
    if not league or not user:
        return

    if not user.preferences.user_added_to_league_notifications:
        return

    user_added_to_league_email(user, league)
    user_added_to_league_messenger(user, league)


def user_invited_to_league_notification(invited_user, league):
    if not league or not invited_user:
        return

    user_invited_to_league_email(invited_user, league)


def user_last_to_submit_notification(user, submission_period):
    if not submission_period or not user:
        return

    user_last_to_submit_email(user, submission_period)
    user_last_to_submit_messenger(user, submission_period)


def user_last_to_vote_notification(user, submission_period):
    if not submission_period or not user:
        return

    user_last_to_vote_email(user, submission_period)
    user_last_to_vote_messenger(user, submission_period)


def user_playlist_created_notification(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    user_playlist_created_email(submission_period)
    user_playlist_created_messenger(submission_period)


def user_removed_from_league_notification(user, league):
    if league or not user:
        return

    if not user.preferences.user_removed_from_league_notifications:
        return

    user_removed_from_league_email(user, league)
    user_removed_from_league_messenger(user, league)


def user_submit_reminder_notification(user, submission_period):
    if not submission_period or not user:
        return

    if not user.preferences.user_submit_reminder_notifications:
        return

    user_submit_reminder_email(user, submission_period)
    user_submit_reminder_messenger(user, submission_period)


def user_vote_reminder_notification(user, submission_period):
    if not submission_period or not user:
        return

    if not user.preferences.user_vote_reminder_notifications:
        return

    user_vote_reminder_email(user, submission_period)
    user_vote_reminder_messenger(user, submission_period)
