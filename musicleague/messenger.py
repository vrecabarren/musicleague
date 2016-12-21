import httplib
import json
import logging
import requests

from musicleague.environment import get_setting
from musicleague.environment.variables import MESSENGER_PAGE_ACCESS_TOKEN


def process_data(data):
    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    process_message(sender_id, message_text)

                if messaging_event.get("delivery"):
                    pass

                if messaging_event.get("optin"):
                    pass

                if messaging_event.get("postback"):
                    pass


def process_message(sender_id, message_text):
    send_message(sender_id, "You said: {}".format(message_text))


def send_message(recipient_id, message_text):
    logging.warn("Sending message: %s: %s", recipient_id, message_text)
    access_token = get_setting(MESSENGER_PAGE_ACCESS_TOKEN)
    params = {"access_token": access_token}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)

    if r.status_code == httplib.OK:
        logging.warn("Message succeeded")
    else:
        logging.warn("Message failed. Status: %s", r.status_code)
