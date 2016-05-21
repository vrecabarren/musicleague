from spotipy import oauth2

from feedback.environment import get_setting
from feedback.environment.variables import SPOTIFY_CLIENT_ID
from feedback.environment.variables import SPOTIFY_CLIENT_SECRET
from feedback.environment.variables import SPOTIFY_REDIRECT_URI


def get_spotify_oauth():
    client_id = get_setting(SPOTIFY_CLIENT_ID)
    client_secret = get_setting(SPOTIFY_CLIENT_SECRET)
    redirect_uri = get_setting(SPOTIFY_REDIRECT_URI)
    scope = 'user-read-email'
    spotify_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri, scope=scope)
    return spotify_oauth
