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
