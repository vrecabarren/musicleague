from flask import g
from flask import redirect
from flask import url_for

from musicleague import app
from musicleague.routes.decorators import login_required
from musicleague.league import get_league
from musicleague.spotify import create_or_update_playlist


CREATE_PLAYLIST_URL = '/l/<league_id>/playlist/create/'
VIEW_PLAYLIST_URL = '/l/<league_id>/playlist/'


@app.route(CREATE_PLAYLIST_URL)
@login_required
def create_spotify_playlist(league_id):
    league = get_league(league_id)
    if league and league.has_owner(g.user):
        playlist = create_or_update_playlist(league.current_submission_period)
        return redirect(playlist.get('external_urls').get('spotify'))
    return redirect(url_for('view_league', league_id=league_id))


@app.route(VIEW_PLAYLIST_URL)
def view_playlist(league_id):
    league = get_league(league_id)
    if league and league.playlist_url:
        return redirect(league.playlist_url)
    return redirect(url_for('view_league', league_id=league_id))
