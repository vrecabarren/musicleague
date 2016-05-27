from flask import g
from flask import redirect
from flask import url_for

from feedback import app
from feedback.routes import urls
from feedback.routes.decorators import login_required
from feedback.season import get_season
from feedback.spotify import create_or_update_playlist


@app.route(urls.CREATE_PLAYLIST_URL)
@login_required
def create_spotify_playlist(season_name):
    season = get_season(season_name)
    if season.owner == g.user:
        playlist = create_or_update_playlist(season.current_submission_period)
        return redirect(playlist.get('external_urls').get('spotify'))
    return redirect(url_for('view_season', season_name=season_name))


@app.route(urls.VIEW_PLAYLIST_URL)
def view_playlist(season_name):
    season = get_season(season_name)
    if season and season.playlist_url:
        return redirect(season.playlist_url)
    return redirect(url_for('view_season', season_name=season_name))
