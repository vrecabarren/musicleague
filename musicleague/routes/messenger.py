import httplib

from flask import g
from flask import request

from musicleague import app
from musicleague.environment import get_setting
from musicleague.environment.variables import MESSENGER_VERIFY_TOKEN
from musicleague.messenger import process_data
from musicleague.models import MessengerContext


MESSENGER_HOOK_URL = '/messenger/'


@app.route('/add_messenger/<messenger_id>/', methods=['GET'])
def add_messenger(messenger_id):
    user = g.user

    context = MessengerContext(id=messenger_id, user=user)
    context.save()

    user.messenger = context
    user.save()


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
    process_data(data)
    return "OK", httplib.OK
