from musicleague.messenger import send_message


def owner_all_users_submitted_messenger(owner, submission_period):
    if not submission_period or not owner or not owner.email:
        return

    if owner.messenger:
        send_message(
            owner.messenger.id,
            "All users have submitted for {}".format(submission_period.name))


def owner_user_submitted_messenger(owner, submission):
    if not submission or not owner or not owner.email:
        return

    if owner.messenger:
        send_message(
            owner.messenger.id,
            "{} just submitted for {}".format(
                submission.user.name, submission.submission_period.name))


def owner_all_users_voted_messenger(owner, submission_period):
    if not submission_period or not owner or not owner.email:
        return

    if owner.messenger:
        send_message(
            owner.messenger.id,
            "All users have voted for {}".format(submission_period.name))


def owner_user_voted_messenger(owner, vote):
    if not vote or not owner or not owner.email:
        return

    if owner.messenger:
        send_message(
            owner.messenger.id,
            "{} just voted for {}".format(
                vote.user.name, vote.submission_period.name))


def user_added_to_league_messenger(user, league):
    if not league or not user or not user.email:
        return

    if user.messenger:
        send_message(
            user.messenger.id,
            "You've been added to the league {}".format(league.name))


def user_invited_to_league_messenger(invited_user, league):
    if not league or not invited_user or not invited_user.email:
        return

    # TODO Determine if there is ever a scenario where this could be used


def user_last_to_submit_messenger(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    if user.messenger:
        send_message(
            user.messenger.id,
            "You're the last to submit for {}".format(submission_period.name))


def user_last_to_vote_messenger(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    if user.messenger:
        send_message(
            user.messenger.id,
            "You're the last to vote for {}".format(submission_period.name))


def user_playlist_created_messenger(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    for user in submission_period.league.users:
        if user.messenger:
            send_message(
                user.messenger.id,
                "A new playlist has been created for {}.\n"
                "Listen to it here: {}".format(
                    submission_period.name, submission_period.playlist_url))


def user_removed_from_league_messenger(user, league):
    if league or not user or not user.email:
        return

    if user.messenger:
        send_message(
            user.messenger.id,
            "You've been removed from the league {}".format(league.name))


def user_submit_reminder_messenger(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    if user.messenger:
        send_message(
            user.messenger.id,
            "It's time to submit for {}".format(submission_period.name))


def user_vote_reminder_messenger(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    if user.messenger:
        send_message(
            user.messenger.id,
            "It's time to vote for {}".format(submission_period.name))
