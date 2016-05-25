import logging

from flask import escape
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session as session
from flask import url_for

from spotipy import Spotify

from feedback import app
from feedback.api import create_season
from feedback.api import get_season
from feedback.models import Submission
from feedback.season import get_seasons_for_user
from feedback.spotify import create_playlist
from feedback.spotify import get_spotify_oauth
from feedback.submit import create_submission
from feedback.user import create_or_update_user
from feedback.user import get_user
from feedback.views import urls
from feedback.views.decorators import login_required


@app.before_request
def before_request():
    current_user = session['current_user'] if 'current_user' in session else ''
    g.user = get_user(current_user) if current_user else None

    access_token = session['access_token'] if 'access_token' in session else ''
    g.spotify = Spotify(access_token) if access_token else None


@app.route(urls.HELLO_URL)
def hello():
    kwargs = {
        'user': g.user,
        'oauth_url': get_spotify_oauth().get_authorize_url()
    }
    return render_template("hello.html", **kwargs)


@app.route(urls.PROFILE_URL)
@login_required
def profile():
    seasons = get_seasons_for_user(g.user)
    kwargs = {
        'user': g.user,
        'seasons': seasons
    }
    return render_template("profile.html", **kwargs)


@app.route(urls.LOGOUT_URL)
@login_required
def logout():
    session.pop('current_user')
    return redirect(url_for("hello"))


@app.route(urls.LOGIN_URL)
def login():
    if 'current_user' not in session:
        url = request.url
        oauth = get_spotify_oauth()
        code = oauth.parse_response_code(url)
        if code:
            token_info = oauth.get_access_token(code)
            access_token = token_info['access_token']
            session['access_token'] = access_token

            spotify = Spotify(access_token)
            user = create_or_update_user(
                id=spotify.current_user().get('id'),
                email=spotify.current_user().get('email'),
                name=spotify.current_user().get('display_name'))

            session['current_user'] = user.id

    return redirect(url_for('profile'))


@app.route(urls.VIEW_USER_URL)
def view_user(user_id):
    kwargs = {
        'page_user': get_user(user_id)
    }
    return render_template("user.html", **kwargs)


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


@app.route(urls.REMOVE_SEASON_URL)
@login_required
def remove_season(season_name):
    season = get_season(season_name)
    if season and season.owner == g.user:
        season.delete()
    return redirect(url_for('profile'))


@app.route(urls.VIEW_SEASON_URL, methods=['GET'])
@login_required
def view_season(season_name):
    season = get_season(season_name)
    kwargs = {
        'user': g.user,
        'season': season
    }
    return render_template("season.html", **kwargs)


@app.route(urls.VIEW_SUBMIT_URL, methods=['GET'])
@login_required
def view_submit(season_name):
    season = get_season(season_name)
    kwargs = {
        'user': g.user,
        'season': season
    }
    return render_template("submit.html", **kwargs)


@app.route(urls.VIEW_SUBMIT_URL, methods=['POST'])
@login_required
def post_submit(season_name):
    season = get_season(season_name)
    tracks = [
        escape(request.form.get('track1')),
        escape(request.form.get('track2'))
    ]

    submission_period = season.current_submission_period

    submission = create_submission(tracks, submission_period, g.user)

    return redirect(
        url_for('view_confirm_submit', season_name=season_name,
                submission_id=submission.id))


@app.route(urls.CONFIRM_SUBMIT_URL, methods=['GET'])
@login_required
def view_confirm_submit(season_name, submission_id):
    season = get_season(season_name)
    tracks = Submission.objects(id=submission_id).get().tracks
    spotify_tracks = [g.spotify.track(t_url) for t_url in tracks]
    kwargs = {
        'user': g.user,
        'season': season,
        'tracks': spotify_tracks
    }

    return render_template("confirm.html", **kwargs)


@app.route(urls.CONFIRM_SUBMIT_URL, methods=['POST'])
@login_required
def post_confirm_submit(season_name, submission_id):
    submission = Submission.objects(id=submission_id).get()
    submission.confirmed = True
    submission.save()
    return redirect(url_for('profile'))


@app.route(urls.CREATE_PLAYLIST_URL)
@login_required
def create_spotify_playlist(season_name):
    season = get_season(season_name)
    if season.owner == g.user:
        playlist = create_playlist(season.current_submission_period)
        return redirect(playlist.get('external_urls').get('spotify'))
    return redirect(url_for('view_season', season_name=season_name))


@app.route(urls.VIEW_PLAYLIST_URL)
def view_playlist(season_name):
    season = get_season(season_name)
    if season and season.playlist_url:
        return redirect(season.playlist_url)
    return redirect(url_for('view_season', season_name=season_name))
