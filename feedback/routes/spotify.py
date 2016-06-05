from flask import g
from flask import redirect
from flask import url_for

from feedback import app
from feedback.routes.decorators import login_required
from feedback.league import get_league
from feedback.spotify import create_or_update_playlist


CREATE_PLAYLIST_URL = '/l/<league_name>/playlist/create/'
VIEW_PLAYLIST_URL = '/l/<league_name>/playlist/'


@app.route(CREATE_PLAYLIST_URL)
@login_required
def create_spotify_playlist(league_name):
    league = get_league(league_name)
    if league.owner == g.user:
        playlist = create_or_update_playlist(league.current_submission_period)
        return redirect(playlist.get('external_urls').get('spotify'))
    return redirect(url_for('view_league', league_name=league_name))


@app.route(VIEW_PLAYLIST_URL)
def view_playlist(league_name):
    league = get_league(league_name)
    if league and league.playlist_url:
        return redirect(league.playlist_url)
    return redirect(url_for('view_league', league_name=league_name))
