from datetime import datetime
from datetime import timedelta
import logging
import requests

from flask import render_template

from feedback import default_scheduler
from feedback import notification_queue
from feedback.environment import is_deployed
from feedback.environment import get_setting
from feedback.environment.variables import MAILGUN_API_BASE_URL
from feedback.environment.variables import MAILGUN_API_KEY
from feedback.environment.variables import NOTIFICATION_SENDER


HTML_PATH = 'email/html/%s'
TXT_PATH = 'email/txt/%s'


def owner_user_submitted_notification(owner, submission):
    if not owner.preferences.owner_user_submitted_notifications:
        return

    default_scheduler.enqueue_at(datetime.utcnow() + timedelta(seconds=90),
                                 logging.warning,
                                 'Sent email notification to owner for submit')

    notification_queue.enqueue_call(
        func=_send_email,
        args=(owner.email,
              'Music League - User Submitted',
              _txt_email('submitted.txt', submission=submission),
              _html_email('submitted.html', submission=submission)))


def user_added_to_league_notification(user, league):
    if not user.preferences.user_added_to_league_notifications:
        return

    notification_queue.enqueue_call(
        func=_send_email,
        args=(user.email,
              'Music League - New League',
              _txt_email('added.txt', league=league),
              _html_email('added.html', league=league)))


def user_removed_from_league_notification(user, league):
    if not user.preferences.user_removed_from_league_notifications:
        return

    notification_queue.enqueue_call(
        func=_send_email,
        args=(user.email,
              'Music League - New League',
              _txt_email('removed.txt', league=league),
              _html_email('removed.html', league=league)))


def user_submit_reminder_notification(user, league):
    if not user.preferences.user_submit_reminder_notifications:
        return

    notification_queue.enqueue_call(
        func=_send_email,
        args=(user.email,
              'Music League - Submission Reminder',
              _txt_email('reminder.txt', league=league),
              _html_email('reminder.html', league=league)))


def _send_email(to, subject, text, html):
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
        return


def _txt_email(template, **kwargs):
    return render_template(TXT_PATH % template, **kwargs)


def _html_email(template, **kwargs):
    return render_template(HTML_PATH % template, **kwargs)
