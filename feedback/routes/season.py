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
from feedback.season import create_season
from feedback.season import get_season
from feedback.submit import create_submission_period
from feedback.submit import get_submission_period
from feedback.user import get_user_by_email


@app.route(urls.ADD_USER_FOR_SEASON_URL, methods=['POST'])
def add_user_for_season(season_name):
    season = get_season(season_name)
    user = get_user_by_email(escape(request.form.get('email')))
    if user and season.owner == g.user:
        season.users.append(user)
        season.save()
    return redirect(url_for('view_season', season_name=season_name))


@app.route(urls.CREATE_SEASON_URL, methods=['POST'])
@login_required
def post_create_season():
    try:
        season_name = escape(request.form.get('season_name'))
        season = create_season(season_name, g.user)
        return redirect(
            url_for(view_season.__name__, season_name=season.name))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(urls.CREATE_SUBMISSION_PERIOD_URL)
@login_required
def post_create_submission_period(season_name):
    season = get_season(season_name)
    if season.owner == g.user:
        create_submission_period(season)
    return redirect(url_for('view_season', season_name=season_name))


@app.route(urls.REMOVE_SEASON_URL)
@login_required
def remove_season(season_name):
    season = get_season(season_name)
    if season and season.owner == g.user:
        season.delete()
    return redirect(url_for('profile'))


@app.route(urls.REMOVE_SUBMISSION_PERIOD_URL)
@login_required
def remove_submission_period(season_name, submission_period_id):
    season = get_season(season_name)
    if season and season.owner == g.user:
        submission_period = get_submission_period(submission_period_id)
        submission_period.delete()
    return redirect(url_for('view_season', season_name=season_name))


@app.route(urls.VIEW_SEASON_URL, methods=['GET'])
@login_required
def view_season(season_name):
    season = get_season(season_name)
    kwargs = {
        'user': g.user,
        'season': season
    }
    return render_template("season.html", **kwargs)


@app.route(urls.VIEW_SUBMISSION_PERIOD_URL)
@login_required
def view_submission_period(season_name, submission_period_id):
    season = get_season(season_name)
    submission_period = get_submission_period(submission_period_id)

    kwargs = {
        'user': g.user,
        'season': season,
        'submission_period': submission_period
    }

    return render_template("submission_period.html", **kwargs)
