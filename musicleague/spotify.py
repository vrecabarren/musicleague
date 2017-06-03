from random import shuffle
import re

from spotipy import oauth2

from musicleague.environment import get_setting
from musicleague.environment import is_deployed
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


def create_playlist(submission_period):
    if not submission_period or not is_deployed():
        return

    from musicleague.bot import get_botify
    bot_id, botify = get_botify()

    playlist_name = str(submission_period.name)
    playlist_description = str(submission_period.description or '')
    tracks = submission_period.all_tracks
    shuffle(tracks)

    playlist = botify.user_playlist_create(bot_id, playlist_name,
                                           description=playlist_description)

    botify.user_playlist_add_tracks(bot_id, playlist.get('id'), tracks)

    external_urls = playlist.get('external_urls')
    submission_period.playlist_id = playlist.get('id')
    submission_period.playlist_url = external_urls.get('spotify')
    submission_period.save()

    user_playlist_created_notification(submission_period)

    return playlist


def update_playlist(submission_period):
    if not submission_period or not submission_period.playlist_id:
        return

    if not is_deployed():
        return

    from musicleague.bot import get_botify
    bot_id, botify = get_botify()

    tracks = submission_period.all_tracks
    shuffle(tracks)

    # TODO Reference submission period's url so we don't have to return this
    playlist = botify.user_playlist(bot_id, submission_period.playlist_id)
    botify.user_playlist_replace_tracks(
        bot_id, submission_period.playlist_id, tracks)

    return playlist


def create_or_update_playlist(submission_period):
    if not submission_period or not is_deployed():
        return

    if not submission_period.playlist_created:
        # Create new playlist and link to this submission period
        playlist = create_playlist(submission_period)

    else:
        # Update existing playlist for this submission period
        playlist = update_playlist(submission_period)

    return playlist


def to_uri(url_or_uri):
    uri_regex = 'spotify:track:[A-Za-z0-9]{22}'
    url_regex = ('(?:http|https):\/\/(?:open|play)\.spotify\.com\/track\/'
                 '(?P<id>[A-Za-z0-9]{22})')

    # If valid URI, no need to modify
    if re.match(uri_regex, url_or_uri):
        return url_or_uri

    # Has to be a valid track URL to mutate. If not, return None.
    if not re.match(url_regex, url_or_uri):
        return None

    return 'spotify:track:%s' % re.match(url_regex, url_or_uri).group('id')
