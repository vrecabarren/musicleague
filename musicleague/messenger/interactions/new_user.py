from flask import url_for

from musicleague.messenger.context import create_context
from musicleague.messenger.send import send_message
from musicleague.user import get_user


def process_new_user(messenger_id):
    create_context(messenger_id)

    send_message(
        messenger_id,
        "Hi! I don't believe we've spoken before. Please provide the ID given "
        "to you on the Music League website.\u000AIf you don't have one, you "
        "can find it here: {}".format(url_for('user_id')))


def process_link_user(context, messenger_id, message_text):
    user = get_user(message_text)
    if not user:
        send_message(messenger_id,
                     "I'm sorry. I didn't find a user with that ID.")
        return

    context.user = user
    context.save()

    user.messenger = context
    user.save()

    send_message(messenger_id,
                 "I've linked your Facebook and Music League accounts!")
