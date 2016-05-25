from flask import g

from spotipy import oauth2

from feedback.environment import get_setting
from feedback.environment.variables import SPOTIFY_CLIENT_ID
from feedback.environment.variables import SPOTIFY_CLIENT_SECRET
from feedback.environment.variables import SPOTIFY_REDIRECT_URI


def get_spotify_oauth():
    client_id = get_setting(SPOTIFY_CLIENT_ID)
    client_secret = get_setting(SPOTIFY_CLIENT_SECRET)
    redirect_uri = get_setting(SPOTIFY_REDIRECT_URI)
    scope = 'user-read-email playlist-modify-public'
    spotify_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri, scope=scope)
    return spotify_oauth


def create_playlist(submission_period):
    tracks = []
    for submission in submission_period.submissions:
        tracks.extend(submission.tracks)
    playlist = g.spotify.user_playlist_create(
        g.user.id, str(submission_period.id))
    g.spotify.user_playlist_add_tracks(g.user.id, playlist.get('id'), tracks)

    submission_period.playlist_created = True
    external_urls = playlist.get('external_urls')
    submission_period.playlist_url = external_urls.get('spotify')
    submission.save()

    return playlist
