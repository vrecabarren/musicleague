import unittest

from mock import patch

from spotipy.oauth2 import SpotifyOAuth

from musicleague.environment.variables import ADD_BOT_REDIRECT_URI
from musicleague.environment.variables import SPOTIFY_CLIENT_ID
from musicleague.environment.variables import SPOTIFY_CLIENT_SECRET
from musicleague.environment.variables import SPOTIFY_REDIRECT_URI
from musicleague.spotify import BOT_SCOPES
from musicleague.spotify import get_spotify_oauth
from musicleague.spotify import OAUTH_SCOPES
from musicleague.spotify import to_uri
from musicleague.tests.utils.environment import set_environment_state


PATCH_PATH = 'musicleague.spotify.'


class GetSpotifyOauthTestCase(unittest.TestCase):

    def setUp(self):
        self.client_id = 'client_id'
        set_environment_state(SPOTIFY_CLIENT_ID.key, self.client_id)

        self.client_secret = 'client_secret'
        set_environment_state(SPOTIFY_CLIENT_SECRET.key, self.client_secret)

        self.redirect_uri = 'redirect_uri'
        set_environment_state(SPOTIFY_REDIRECT_URI.key, self.redirect_uri)

        self.bot_redirect_uri = 'bot_redirect_uri'
        set_environment_state(ADD_BOT_REDIRECT_URI.key, self.bot_redirect_uri)

    @patch(PATCH_PATH + 'oauth2.SpotifyOAuth', wraps=SpotifyOAuth)
    def test_spotify_oauth(self, oauth_construct):

        oauth = get_spotify_oauth()

        self.assertIsInstance(oauth, SpotifyOAuth)
        oauth_construct.assert_called_once_with(
            self.client_id, self.client_secret, self.redirect_uri,
            scope=OAUTH_SCOPES)

    @patch(PATCH_PATH + 'oauth2.SpotifyOAuth', wraps=SpotifyOAuth)
    def test_spotify_bot_oauth(self, oauth_construct):

        oauth = get_spotify_oauth(bot=True)

        self.assertIsInstance(oauth, SpotifyOAuth)
        oauth_construct.assert_called_once_with(
            self.client_id, self.client_secret, self.bot_redirect_uri,
            scope=BOT_SCOPES)


class ToUriTestCase(unittest.TestCase):

    def test_non_track_uri(self):
        album_uri = 'spotify:album:0QA8bVnLCxOpCYMhIdT6rz'
        self.assertIsNone(to_uri(album_uri))

    def test_non_track_url(self):
        album_url = 'https://open.spotify.com/album/0QA8bVnLCxOpCYMhIdT6rz'
        self.assertIsNone(to_uri(album_url))

    def test_track_uri(self):
        track_uri = 'spotify:track:0YhEJmOYZoRdKNPbCvHs8R'
        self.assertEqual(track_uri, to_uri(track_uri))

    def test_track_url(self):
        track_uri = 'spotify:track:0YhEJmOYZoRdKNPbCvHs8R'
        track_url = 'https://open.spotify.com/track/0YhEJmOYZoRdKNPbCvHs8R'
        self.assertEqual(track_uri, to_uri(track_url))
