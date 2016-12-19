import logging
import requests

from flask import render_template

from musicleague import app
from musicleague import celery
from musicleague.environment import is_deployed
from musicleague.environment import get_setting
from musicleague.environment.variables import MAILGUN_API_BASE_URL
from musicleague.environment.variables import MAILGUN_API_KEY
from musicleague.environment.variables import NOTIFICATION_SENDER


HTML_PATH = 'email/html/%s'
TXT_PATH = 'email/txt/%s'


def owner_all_users_submitted_notification(owner, submission_period):
    if not submission_period or not owner or not owner.email:
        return

    if not owner.preferences.owner_all_users_submitted_notifications:
        return

    _send_email.apply_async(
        args=[owner.email,
              'Music League - All Users Submitted',
              _txt_email('all_submitted.txt',
                         submission_period=submission_period),
              _html_email('all_submitted.html',
                          submission_period=submission_period)]
    )


def owner_user_submitted_notification(owner, submission):
    if not submission or not owner or not owner.email:
        return

    if not owner.preferences.owner_user_submitted_notifications:
        return

    _send_email.apply_async(
        args=[owner.email,
              'Music League - User Submitted',
              _txt_email('submitted.txt', submission=submission),
              _html_email('submitted.html', submission=submission)]
    )


def owner_all_users_voted_notification(owner, submission_period):
    if not submission_period or not owner or not owner.email:
        return

    if not owner.preferences.owner_all_users_voted_notifications:
        return

    _send_email.apply_async(
        args=[owner.email,
              'Music League - All Users Voted',
              _txt_email('all_voted.txt',
                         submission_period=submission_period),
              _html_email('all_voted.html',
                          submission_period=submission_period)]
    )


def owner_user_voted_notification(owner, vote):
    if not vote or not owner or not owner.email:
        return

    if not owner.preferences.owner_user_voted_notifications:
        return

    _send_email.apply_async(
        args=[owner.email,
              'Music League - User Voted',
              _txt_email('voted.txt', vote=vote),
              _html_email('voted.html', vote=vote)]
    )


def user_added_to_league_notification(user, league):
    if not league or not user or not user.email:
        return

    if not user.preferences.user_added_to_league_notifications:
        return

    _send_email.apply_async(
        args=[user.email,
              'Music League - New League',
              _txt_email('added.txt', league=league),
              _html_email('added.html', league=league)]
    )


def user_invited_to_league_notification(invited_user, league):
    if not league or not invited_user or not invited_user.email:
        return

    _send_email.apply_async(
        args=[invited_user.email,
              'Music League - You Are Invited',
              _txt_email('invited.txt', user=invited_user, league=league),
              _html_email('invited.html', user=invited_user, league=league)]
    )


def user_last_to_submit_notification(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    _send_email.apply_async(
        args=[user.email,
              'Music League - Last to Submit',
              _txt_email('last_to_submit.txt',
                         submission_period=submission_period),
              _html_email('last_to_submit.html',
                          submission_period=submission_period)]
    )


def user_last_to_vote_notification(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    _send_email.apply_async(
        args=[user.email,
              'Music League - Last to Vote',
              _txt_email('last_to_vote.txt',
                         submission_period=submission_period),
              _html_email('last_to_vote.html',
                          submission_period=submission_period)]
    )


def user_playlist_created_notification(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    to = submission_period.league.users[0].email
    bcc_list = ','.join(
        u.email for u in submission_period.league.users[1:]
        if u.email and u.preferences.user_playlist_created_notifications)

    _send_email.apply_async(
        args=[to,
              'Music League - New Playlist',
              _txt_email('playlist.txt', submission_period=submission_period),
              _html_email('playlist.html', submission_period=submission_period)
              ],
        kwargs={'additional_data': {'bcc': bcc_list}}
    )


def user_removed_from_league_notification(user, league):
    if league or not user or not user.email:
        return

    if not user.preferences.user_removed_from_league_notifications:
        return

    _send_email.apply_async(
        args=[user.email,
              'Music League - New League',
              _txt_email('removed.txt', league=league),
              _html_email('removed.html', league=league)]
    )


def user_submit_reminder_notification(user, league):
    if not league or not user or not user.email:
        return

    if not user.preferences.user_submit_reminder_notifications:
        return

    _send_email.apply_async(
        args=[user.email,
              'Music League - Submission Reminder',
              _txt_email('submit_reminder.txt', league=league),
              _html_email('submit_reminder.html', league=league)]
    )


def user_vote_reminder_notification(user, league):
    if not league or not user or not user.email:
        return

    if not user.preferences.user_vote_reminder_notifications:
        return

    _send_email.apply_async(
        args=[user.email,
              'Music League - Vote Reminder',
              _txt_email('vote_reminder.txt', league=league),
              _html_email('vote_reminder.html', league=league)]
    )


@celery.task
def _send_email(to, subject, text, html, additional_data=None):
    if not is_deployed():
        logging.info(text)
        return

    api_key = get_setting(MAILGUN_API_KEY)
    api_base_url = get_setting(MAILGUN_API_BASE_URL)
    request_url = '{}/messages'.format(api_base_url)
    sender = get_setting(NOTIFICATION_SENDER)

    data = {
        "from": sender,
        "to": to,
        "subject": subject,
        "text": text,
        "html": html
    }

    if isinstance(additional_data, dict):
        data.update(additional_data)

    request = requests.post(request_url, auth=("api", api_key), data=data)

    if request.status_code != 200:
        logging.warning(
            u'Mail send failed. Status: {}, Response: {}'.format(
                request.status_code, request.text))
        return


def _txt_email(template, **kwargs):
    with app.app_context():
        return render_template(TXT_PATH % template, **kwargs)


def _html_email(template, **kwargs):
    with app.app_context():
        return render_template(HTML_PATH % template, **kwargs)
