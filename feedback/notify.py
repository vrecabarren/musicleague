import logging
import requests

from flask import render_template

from feedback.environment import is_deployed
from feedback.environment import get_setting
from feedback.environment.variables import MAILGUN_API_BASE_URL
from feedback.environment.variables import MAILGUN_API_KEY
from feedback.environment.variables import NOTIFICATION_SENDER


HTML_PATH = 'email/html/%s'
TXT_PATH = 'email/txt/%s'


def owner_user_submitted_notification(owner, submission):
    if owner.preferences.owner_user_submitted_notifications:
        _send_mail(
            owner.email,
            'Music League - User Submitted',
            render_template(
                TXT_PATH % 'submitted.txt', submission=submission),
            render_template(
                HTML_PATH % 'submitted.html', submission=submission)
        )


def user_submit_reminder_notification(user, league):
    if user.preferences.user_submit_reminder_notifications:
        _send_mail(
            user.email,
            'Music League - Submission Reminder',
            render_template(TXT_PATH % 'reminder.txt', league=league),
            render_template(HTML_PATH % 'reminder.html', league=league)
        )


def _send_mail(to, subject, text, html):
    if not is_deployed():
        logging.info(text)
        return

    api_key = get_setting(MAILGUN_API_KEY)
    api_base_url = get_setting(MAILGUN_API_BASE_URL)
    request_url = '{}/messages'.format(api_base_url)
    sender = get_setting(NOTIFICATION_SENDER)
    request = requests.post(request_url,
                            auth=("api", api_key),
                            data={"from": sender,
                                  "to": to,
                                  "subject": subject,
                                  "text": text,
                                  "html": html})

    if request.status_code != 200:
        logging.warning(
            u'Mail send failed. Status: {}, Response: {}'.format(
                request.status_code, request.text))
