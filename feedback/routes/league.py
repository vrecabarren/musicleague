import logging

from flask import escape
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback import app
from feedback.routes import urls
from feedback.routes.decorators import login_required
from feedback.league import create_league
from feedback.league import get_league
from feedback.submit import create_submission_period
from feedback.submit import get_submission
from feedback.submit import get_submission_period
from feedback.user import get_user_by_email


@app.route(urls.ADD_USER_FOR_LEAGUE_URL, methods=['POST'])
def add_user_for_league(league_name):
    league = get_league(league_name)
    user = get_user_by_email(escape(request.form.get('email')))
    if user and user not in league.users and league.owner == g.user:
        league.users.append(user)
        league.save()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(urls.CREATE_LEAGUE_URL, methods=['POST'])
@login_required
def post_create_league():
    try:
        league_name = escape(request.form.get('league_name'))
        league = create_league(league_name, g.user)
        return redirect(
            url_for(view_league.__name__, league_name=league.name))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(urls.CREATE_SUBMISSION_PERIOD_URL)
@login_required
def post_create_submission_period(league_name):
    league = get_league(league_name)
    if league.owner == g.user:
        create_submission_period(league)
    return redirect(url_for('view_league', league_name=league_name))


@app.route(urls.REMOVE_LEAGUE_URL)
@login_required
def remove_league(league_name):
    league = get_league(league_name)
    if league and league.owner == g.user:
        league.delete()
    return redirect(url_for('profile'))


@app.route(urls.REMOVE_SUBMISSION_URL)
@login_required
def remove_submission(league_name, submission_period_id, submission_id):
    league = get_league(league_name)
    if league and league.owner == g.user:
        submission = get_submission(submission_id)
        submission.delete()
    return redirect(url_for('view_submission_period', league_name=league_name,
                            submission_period_id=submission_period_id))


@app.route(urls.REMOVE_SUBMISSION_PERIOD_URL)
@login_required
def remove_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    if league and league.owner == g.user:
        submission_period = get_submission_period(submission_period_id)
        submission_period.delete()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(urls.VIEW_LEAGUE_URL, methods=['GET'])
@login_required
def view_league(league_name):
    league = get_league(league_name)
    kwargs = {
        'user': g.user,
        'league': league,
        'edit': request.args.get('edit')
    }
    return render_template("league.html", **kwargs)


@app.route(urls.VIEW_LEAGUE_URL, methods=['POST'])
@login_required
def rename_submission_period(league_name):
    submission_period_id = request.args.get('edit')
    new_name = request.form.get('new_name')
    if not submission_period_id or not new_name:
        return redirect(request.referrer)

    submission_period = get_submission_period(submission_period_id)
    submission_period.name = new_name
    submission_period.save()

    return redirect(url_for('view_league', league_name=league_name))


@app.route(urls.VIEW_SUBMISSION_PERIOD_URL)
@login_required
def view_submission_period(league_name, submission_period_id):
    league = get_league(league_name)
    submission_period = get_submission_period(submission_period_id)

    all_tracks = []
    for submission in submission_period.submissions:
        all_tracks.extend(submission.tracks)

    tracks = g.spotify.tracks(all_tracks).get('tracks') if all_tracks else []

    kwargs = {
        'user': g.user,
        'league': league,
        'submission_period': submission_period,
        'tracks': tracks
    }

    return render_template("submission_period.html", **kwargs)
