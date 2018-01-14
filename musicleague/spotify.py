import json
from random import shuffle
import re

from spotipy import oauth2

from musicleague import app
from musicleague.environment import get_setting
from musicleague.environment import is_deployed
from musicleague.environment.variables import ADD_BOT_REDIRECT_URI
from musicleague.environment.variables import SPOTIFY_CLIENT_ID
from musicleague.environment.variables import SPOTIFY_CLIENT_SECRET
from musicleague.environment.variables import SPOTIFY_REDIRECT_URI
from musicleague.notify import user_playlist_created_notification
from musicleague.persistence.update import upsert_round


OAUTH_SCOPES = 'user-read-email playlist-modify-public'
BOT_SCOPES = 'playlist-modify-public playlist-modify-private'

URI_REGEX = 'spotify:track:[A-Za-z0-9]{22}'
URL_REGEX = ('(?:http|https):\/\/(?:open|play)\.spotify\.com\/track\/'
                 '(?P<id>[A-Za-z0-9]{22})')


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
    if not submission_period or not submission_period.all_tracks or not is_deployed():
        return

    from musicleague.bot import get_botify
    bot_id, botify = get_botify()

    playlist_name = str(submission_period.name)
    description = str(submission_period.description or '')
    description = description.replace('\n', ' ').replace('\r', ' ')
    tracks = submission_period.all_tracks
    shuffle(tracks)

    try:
        app.logger.info("Creating new playlist: %s", playlist_name)
        playlist = botify.user_playlist_create(
            bot_id, playlist_name, description=description)
        app.logger.info(
            "Created new playlist: %s (%s)", playlist_name, playlist.get('id'))
    except Exception as e:
        app.logger.error("Error while creating playlist with params: %s %s %s",
                         bot_id, playlist_name, json.dumps(description))
        raise

    try:
        app.logger.info("Adding tracks to new playlist: %s", tracks)
        botify.user_playlist_add_tracks(bot_id, playlist.get('id'), tracks)
    except Exception as e:
        app.logger.error("Error while adding tracks: %s", json.dumps(tracks))
        raise

    return playlist


def update_playlist(submission_period):
    if not submission_period or not submission_period.playlist_id:
        return

    if not is_deployed():
        app.logger.warn("Not deployed - skipping playlist update")
        return

    from musicleague.bot import get_botify
    bot_id, botify = get_botify()

    tracks = submission_period.all_tracks
    shuffle(tracks)

    # TODO Reference submission period's url so we don't have to return this
    try:
        app.logger.info("Replacing existing tracks with: %s", tracks)
        playlist_id = to_playlist_id(submission_period.playlist_url)
        playlist = botify.user_playlist(bot_id, playlist_id)
        botify.user_playlist_replace_tracks(bot_id, playlist_id, tracks)
    except Exception as e:
        app.logger.error("Error updating tracks: %s", json.dumps(tracks))
        raise

    return playlist


def create_or_update_playlist(submission_period):
    if not submission_period or not is_deployed():
        return

    if not submission_period.playlist_created:
        # Create new playlist and link to this submission period
        app.logger.info("Creating playlist for round: %s", submission_period.id)
        playlist = create_playlist(submission_period)
        if not playlist:
            app.logger.error('There was a problem creating the playlist')
            return

        playlist_url = playlist['external_urls']['spotify']
        submission_period.playlist_url = playlist_url
        upsert_round(submission_period)
        user_playlist_created_notification(submission_period)

    else:
        # Update existing playlist for this submission period
        app.logger.info("Updating playlist for round: %s", submission_period.id)
        playlist = update_playlist(submission_period)
        # TODO user_playlist_updated_notification(submission_period)

    return playlist


def to_playlist_uri(url_or_uri):
    # If valid URI, no need to modify
    if is_playlist_uri(url_or_uri):
        return url_or_uri

    # Has to be a valid track URL to mutate. If not, return None.
    if not is_playlist_url(url_or_uri):
        return None

    return 'spotify:track:%s' % to_playlist_id(url_or_uri)


def to_playlist_id(url_or_uri):
    if is_playlist_url(url_or_uri):
        return re.match(URL_REGEX, url_or_uri).group('id')
    elif is_playlist_uri(url_or_uri):
        return re.match(URI_REGEX, url_or_uri).group('id')
    return None


def is_playlist_uri(url_or_uri):
    return re.match(URI_REGEX, url_or_uri)


def is_playlist_url(url_or_uri):
    return re.match(URL_REGEX, url_or_uri)