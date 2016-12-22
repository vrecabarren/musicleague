from musicleague.messenger.context import get_context
from musicleague.messenger.interactions.new_user import process_link_user
from musicleague.messenger.interactions.new_user import process_new_user


def process_data(data):
    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    process_message(sender_id, message_text)


def process_message(sender_id, message_text):
    context = get_context(sender_id)

    # If this is not a user we have interacted with, get info to link account
    if not context:
        process_new_user(sender_id)

    # If this is a user we've interacted with but accounts aren't linked, link
    elif context and not context.user:
        process_link_user(context, sender_id, message_text)
