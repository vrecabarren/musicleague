import logging

from flask import escape
from flask import g
from flask import redirect
from flask import request
from flask import url_for

from feedback import app
from feedback.routes.decorators import league_required
from feedback.routes.decorators import login_required
from feedback.routes.decorators import templated
from feedback.league import create_league
from feedback.submit import get_submission
from feedback.user import get_user_by_email


ADD_USER_FOR_LEAGUE_URL = '/l/<league_name>/users/add/'
CREATE_LEAGUE_URL = '/l/create/'
REMOVE_LEAGUE_URL = '/l/<league_name>/remove/'
REMOVE_SUBMISSION_URL = '/l/<league_name>/<submission_period_id>/<submission_id>/remove/'  # noqa
REMOVE_USER_FOR_LEAGUE_URL = '/l/<league_name>/users/remove/<user_id>/'
VIEW_LEAGUE_URL = '/l/<league_name>/'


@app.route(ADD_USER_FOR_LEAGUE_URL, methods=['POST'])
@login_required
@league_required
def add_user_for_league(league_name, **kwargs):
    league = kwargs.get('league')
    user = get_user_by_email(escape(request.form.get('email')))
    if user and user not in league.users and league.owner == g.user:
        league.users.append(user)
        league.save()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(REMOVE_USER_FOR_LEAGUE_URL, methods=['GET'])
@login_required
@league_required
def remove_user_for_league(league_name, user_id, **kwargs):
    league = kwargs.get('league')
    if league.owner == g.user:
        league.users = [u for u in league.users if str(u.id) != user_id]
        logging.warning(len(league.users))
        league.save()
    return redirect(url_for('view_league', league_name=league_name))


@app.route(CREATE_LEAGUE_URL, methods=['POST'])
@login_required
def post_create_league():
    try:
        league_name = escape(request.form.get('league_name'))
        league = create_league(league_name, g.user)
        return redirect(
            url_for(view_league.__name__, league_name=league.name))
    except Exception as e:
        logging.exception('There was an exception: %s', e)


@app.route(REMOVE_LEAGUE_URL)
@login_required
@league_required
def remove_league(league_name, **kwargs):
    league = kwargs.get('league')
    if league and league.owner == g.user:
        league.delete()
    return redirect(url_for('profile'))


@app.route(REMOVE_SUBMISSION_URL)
@login_required
def remove_submission(league_name, submission_period_id, submission_id,
                      **kwargs):
    league = kwargs.get('league')
    if league and league.owner == g.user:
        submission = get_submission(submission_id)
        submission.delete()
    return redirect(url_for('view_submission_period', league_name=league_name,
                            submission_period_id=submission_period_id))


@app.route(VIEW_LEAGUE_URL, methods=['GET'])
@templated('league.html')
@login_required
@league_required
def view_league(league_name, **kwargs):
    return {
        'user': g.user,
        'league': kwargs.get('league'),
        'edit': request.args.get('edit')
    }
