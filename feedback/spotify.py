from random import shuffle

from flask import g

from spotipy import oauth2

from feedback.environment import get_setting
from feedback.environment.variables import SPOTIFY_CLIENT_ID
from feedback.environment.variables import SPOTIFY_CLIENT_SECRET
from feedback.environment.variables import SPOTIFY_REDIRECT_URI
from feedback.notify import user_playlist_created_notification


OAUTH_SCOPES = ['user-read-email',
                'playlist-modify-public']


def get_spotify_oauth():
    client_id = get_setting(SPOTIFY_CLIENT_ID)
    client_secret = get_setting(SPOTIFY_CLIENT_SECRET)
    redirect_uri = get_setting(SPOTIFY_REDIRECT_URI)
    scopes = ' '.join(OAUTH_SCOPES)
    spotify_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri, scope=scopes,
        cache_path='.spotipyoauthcache')
    return spotify_oauth


def create_or_update_playlist(submission_period):
    tracks = []
    for submission in submission_period.submissions:
        tracks.extend(submission.tracks)
    shuffle(tracks)

    # Create new playlist and link to this submission period
    if not submission_period.playlist_created:
        playlist_name = str(submission_period.name)
        playlist = g.spotify.user_playlist_create(g.user.id, playlist_name)

        g.spotify.user_playlist_add_tracks(
            g.user.id, playlist.get('id'), tracks)

        external_urls = playlist.get('external_urls')
        submission_period.playlist_id = playlist.get('id')
        submission_period.playlist_url = external_urls.get('spotify')
        submission_period.save()

        user_playlist_created_notification(submission_period)

    # Update existing playlist for this submission period
    else:
        # TODO Only get the playlist's id
        playlist = g.spotify.user_playlist(
            g.user.id, submission_period.playlist_id)
        g.spotify.user_playlist_replace_tracks(
            g.user.id, submission_period.playlist_id, tracks)

    return playlist
