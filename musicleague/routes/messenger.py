import httplib
import json
import requests

from flask import request

from musicleague import app
from musicleague.environment import get_setting
from musicleague.environment.variables import MESSENGER_PAGE_ACCESS_TOKEN
from musicleague.environment.variables import MESSENGER_VERIFY_TOKEN


MESSENGER_HOOK_URL = '/messenger/'


@app.route(MESSENGER_HOOK_URL, methods=['GET'])
def verify():
    # When the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    hub_mode = request.args.get('hub.mode')
    hub_challenge = request.args.get('hub.challenge')
    if hub_mode == 'subscribe' and hub_challenge:

        # Verify request is from Facebook
        hub_token = request.args.get('hub.verify_token')
        verify_token = get_setting(MESSENGER_VERIFY_TOKEN)
        if hub_token != verify_token:
            return 'TOKEN MISMATCH', httplib.UNAUTHORIZED

        return hub_challenge, httplib.OK

    return 'Hello World', httplib.OK


@app.route(MESSENGER_HOOK_URL, methods=['POST'])
def webhook():
    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    # recipient_id = messaging_event["recipient"]["id"]
                    # message_text = messaging_event["message"]["text"]

                    send_message(sender_id, "got it, thanks!")

                if messaging_event.get("delivery"):
                    pass

                if messaging_event.get("optin"):
                    pass

                if messaging_event.get("postback"):
                    pass

    return "ok", httplib.OK


def send_message(recipient_id, message_text):
    access_token = get_setting(MESSENGER_PAGE_ACCESS_TOKEN)
    params = {"access_token": access_token}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    if r.status_code != httplib.OK:
        pass
