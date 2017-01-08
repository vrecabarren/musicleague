from flask import url_for

from musicleague import app
from musicleague.messenger import send_message


def owner_all_users_submitted_messenger(owner, submission_period):
    if not submission_period or not owner or not owner.messenger:
        return

    send_message(
        owner.messenger.id,
        "All users have submitted for {}".format(submission_period.name))


def owner_user_submitted_messenger(owner, submission):
    if not submission or not owner or not owner.messenger:
        return

    send_message(
        owner.messenger.id,
        "{} just submitted for {}".format(
            submission.user.name, submission.submission_period.name))


def owner_all_users_voted_messenger(owner, submission_period):
    if not submission_period or not owner or not owner.messenger:
        return

    send_message(
        owner.messenger.id,
        "All users have voted for {}".format(submission_period.name))


def owner_user_voted_messenger(owner, vote):
    if not vote or not owner or not owner.messenger:
        return

    send_message(
        owner.messenger.id,
        "{} just voted for {}".format(vote.user.name,
                                      vote.submission_period.name))


def user_added_to_league_messenger(user, league):
    if not league or not user or not user.messenger:
        return

    with app.app_context():
        send_message(
            user.messenger.id,
            "You've been added to the league {}.\n{}".format(
                league.name,
                url_for('view_league', league_id=league.id, _external=True)))


def user_invited_to_league_messenger(invited_user, league):
    # TODO Determine if there is ever a scenario where this could be used
    return


def user_last_to_submit_messenger(user, submission_period):
    if not submission_period or not user or not user.messenger:
        return

    with app.app_context():
        send_message(
            user.messenger.id,
            "You're the last to submit for {}.\n{}".format(
                submission_period.name,
                url_for('view_submit', league_id=submission_period.league.id,
                        submission_period_id=submission_period.id,
                        _external=True)))


def user_last_to_vote_messenger(user, submission_period):
    if not submission_period or not user or not user.messenger:
        return

    with app.app_context():
        send_message(
            user.messenger.id,
            "You're the last to vote for {}.\n{}".format(
                submission_period.name,
                url_for('view_vote', league_id=submission_period.league.id,
                        submission_period_id=submission_period.id,
                        _external=True)))


def user_playlist_created_messenger(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    for user in submission_period.league.users:
        if not user.preferences.user_playlist_created_notifications:
            continue

        if user.messenger:
            send_message(
                user.messenger.id,
                "A new playlist has been created for {}.\n"
                "Listen to it here: {}".format(
                    submission_period.name, submission_period.playlist_url))


def user_removed_from_league_messenger(user, league):
    if not league or not user or not user.messenger:
        return

    send_message(
        user.messenger.id,
        "You've been removed from the league {}".format(league.name))


def user_submit_reminder_messenger(user, submission_period):
    if not submission_period or not user or not user.messenger:
        return

    with app.app_context():
        send_message(
            user.messenger.id,
            "It's time to submit for {}.\n{}".format(
                submission_period.name,
                url_for('view_submit', league_id=submission_period.league.id,
                        submission_period_id=submission_period.id,
                        _external=True)))


def user_vote_reminder_messenger(user, submission_period):
    if not submission_period or not user or not user.messenger:
        return

    with app.app_context():
        send_message(
            user.messenger.id,
            "It's time to vote for {}.\n{}".format(
                submission_period.name,
                url_for('view_vote', league_id=submission_period.league.id,
                        submission_period_id=submission_period.id,
                        _external=True)))
