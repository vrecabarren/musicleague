from random import shuffle

from spotipy import oauth2

from musicleague.environment import get_setting
from musicleague.environment.variables import ADD_BOT_REDIRECT_URI
from musicleague.environment.variables import SPOTIFY_CLIENT_ID
from musicleague.environment.variables import SPOTIFY_CLIENT_SECRET
from musicleague.environment.variables import SPOTIFY_REDIRECT_URI
from musicleague.notify import user_playlist_created_notification


OAUTH_SCOPES = 'user-read-email playlist-modify-public'
BOT_SCOPES = 'playlist-modify-public playlist-modify-private'


def get_spotify_oauth(bot=False):
    client_id = get_setting(SPOTIFY_CLIENT_ID)
    client_secret = get_setting(SPOTIFY_CLIENT_SECRET)
    redirect_uri = get_setting(SPOTIFY_REDIRECT_URI)
    scopes = OAUTH_SCOPES
    if bot:
        redirect_uri = get_setting(ADD_BOT_REDIRECT_URI)
        scopes = BOT_SCOPES

    spotify_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri, scope=scopes)
    return spotify_oauth


def create_or_update_playlist(submission_period):
    from musicleague.bot import get_botify
    bot_id, botify = get_botify()

    tracks = []
    for submission in submission_period.submissions:
        tracks.extend(submission.tracks)
    shuffle(tracks)

    # Create new playlist and link to this submission period
    if not submission_period.playlist_created:
        playlist_name = str(submission_period.name)
        playlist = botify.user_playlist_create(
            bot_id, playlist_name, public=False)

        botify.user_playlist_add_tracks(bot_id, playlist.get('id'), tracks)

        external_urls = playlist.get('external_urls')
        submission_period.playlist_id = playlist.get('id')
        submission_period.playlist_url = external_urls.get('spotify')
        submission_period.save()

        user_playlist_created_notification(submission_period)

    # Update existing playlist for this submission period
    else:
        # TODO Only get the playlist's id
        playlist = botify.user_playlist(bot_id, submission_period.playlist_id)
        botify.user_playlist_replace_tracks(
            bot_id, submission_period.playlist_id, tracks)

    return playlist
