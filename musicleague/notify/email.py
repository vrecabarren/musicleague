import httplib
import requests

import sendgrid
from flask import render_template
from rq.decorators import job
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Personalization

from musicleague import app
from musicleague import redis_conn
from musicleague.environment import is_deployed
from musicleague.environment import get_setting
from musicleague.environment.variables import MAILGUN_API_BASE_URL
from musicleague.environment.variables import MAILGUN_API_KEY
from musicleague.environment.variables import NOTIFICATION_SENDER
from musicleague.environment.variables import SENDGRID_API_KEY


HTML_PATH = 'email/html/%s'
TXT_PATH = 'email/txt/%s'


def owner_user_submitted_email(owner, submission):
    if not submission or not owner or not owner.email:
        return

    _send_email.delay(
        owner.email,
        'Music League - User Submitted',
        _txt_email('submitted.txt', submission=submission),
        _html_email('submitted.html', submission=submission)
    )


def owner_user_voted_email(owner, vote):
    if not vote or not owner or not owner.email:
        return

    _send_email.delay(
        owner.email,
        'Music League - User Voted',
        _txt_email('voted.txt', vote=vote),
        _html_email('voted.html', vote=vote)
    )


def user_added_to_league_email(user, league):
    if not league or not user or not user.email:
        return

    _send_email.delay(
        user.email,
        'Music League - New League',
        _txt_email('added.txt', league=league),
        _html_email('added.html', league=league)
    )


def user_all_voted_email(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    to = submission_period.league.owner.email

    bcc_list = [
        u.email for u in submission_period.league.users
        if u.email and not submission_period.league.has_owner(u)
    ]

    _send_email.delay(
        to,
        'Music League - The Votes Are In',
        _txt_email('all_voted.txt', submission_period=submission_period),
        _html_email('all_voted.html', submission_period=submission_period),
        bcc_list=(bcc_list or None)
    )


def user_invited_to_league_email(invited_user, league):
    if not league or not invited_user or not invited_user.email:
        return

    _send_email.delay(
        invited_user.email,
        'Music League - You Are Invited',
        _txt_email('invited.txt', user=invited_user, league=league),
        _html_email('invited.html', user=invited_user, league=league)
    )


def user_last_to_submit_email(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    _send_email.delay(
        user.email,
        'Music League - Last to Submit',
        _txt_email('last_to_submit.txt', submission_period=submission_period),
        _html_email('last_to_submit.html', submission_period=submission_period)
    )


def user_last_to_vote_email(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    _send_email.delay(
        user.email,
        'Music League - Last to Vote',
        _txt_email('last_to_vote.txt', submission_period=submission_period),
        _html_email('last_to_vote.html', submission_period=submission_period)
    )


def user_new_round_email(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    # Less than 2 users leads to invalid BCC list
    if len(submission_period.league.users) < 2:
        app.logger.info('Skipping new round email with < 2 users')
        return

    to = submission_period.league.owner.email

    bcc_list = [
        u.email for u in submission_period.league.users
        if u.email and not submission_period.league.has_owner(u)
        and u.preferences.user_playlist_created_notifications
    ]

    _send_email.delay(
        to,
        'Music League - Round Starting',
        _txt_email('new_round.txt', submission_period=submission_period),
        _html_email('new_round.html', submission_period=submission_period),
        bcc_list=(bcc_list or None)
    )


def user_playlist_created_email(submission_period):
    if not submission_period or not submission_period.league.users:
        return

    # Less than 2 users leads to invalid BCC list
    if len(submission_period.league.users) < 2:
        app.logger.info('Skipping playlist email with < 2 users')
        return

    to = submission_period.league.owner.email

    bcc_list = [
        u.email for u in submission_period.league.users
        if u.email and not submission_period.league.has_owner(u)
        and u.preferences.user_playlist_created_notifications
    ]

    _send_email.delay(
        to,
        'Music League - New Playlist',
        _txt_email('playlist.txt', submission_period=submission_period),
        _html_email('playlist.html', submission_period=submission_period),
        bcc_list=(bcc_list or None)
    )


def user_submit_reminder_email(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    _send_email.delay(
        user.email,
        'Music League - Submission Reminder',
        _txt_email('submit_reminder.txt',
                   league=submission_period.league,
                   submission_period=submission_period),
        _html_email('submit_reminder.html',
                    league=submission_period.league,
                    submission_period=submission_period)
    )


def user_vote_reminder_email(user, submission_period):
    if not submission_period or not user or not user.email:
        return

    _send_email.delay(
        user.email,
        'Music League - Vote Reminder',
        _txt_email('vote_reminder.txt',
                   league=submission_period.league,
                   submission_period=submission_period),
        _html_email('vote_reminder.html',
                    league=submission_period.league,
                    submission_period=submission_period))


@job('default', connection=redis_conn)
def _send_email(to, subject, text, html, bcc_list=None):
    if not is_deployed():
        app.logger.info(text)
        return
    
    api_key = get_setting(SENDGRID_API_KEY)
    
    from_email = Email(get_setting(NOTIFICATION_SENDER))
    to_email = Email(to)
    mail = Mail(from_email, subject, to_email)
    mail.add_content(Content("text/plain", text))
    mail.add_content(Content("text/html", html))

    if bcc_list is not None:
        bcc_personalization = Personalization()
        for bcc in bcc_list:
            bcc_personalization.add_bcc(Email(bcc))
        mail.add_personalization(bcc_personalization)

    sg = sendgrid.SendGridAPIClient(apikey=api_key)
    response = sg.client.mail.send.post(request_body=mail.get())

    if response.status_code != httplib.OK:
        app.logger.warning(
            u'Mail send failed. Status: {}, Response: {}'.format(
                response.status_code, response.__dict__))
        return


@job('default', connection=redis_conn)
def _send_email_old(to, subject, text, html, additional_data=None):
    if not is_deployed():
        app.logger.info(text)
        return

    api_key = get_setting(MAILGUN_API_KEY)
    api_base_url = get_setting(MAILGUN_API_BASE_URL)
    request_url = '{}/messages'.format(api_base_url)
    sender = get_setting(NOTIFICATION_SENDER)

    if not (api_key and api_base_url and sender):
        app.logger.warning('Missing email provider configuration, will not send')
        return

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
        app.logger.warning(
            u'Mail send failed. Status: {}, Response: {}'.format(
                request.status_code, request.text))
        return


def _txt_email(template, **kwargs):
    with app.app_context():
        return render_template(TXT_PATH % template, **kwargs)


def _html_email(template, **kwargs):
    with app.app_context():
        return render_template(HTML_PATH % template, **kwargs)
