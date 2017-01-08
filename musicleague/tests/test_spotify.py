import unittest

from mock import Mock
from mock import patch

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from musicleague.environment.variables import ADD_BOT_REDIRECT_URI
from musicleague.environment.variables import SPOTIFY_CLIENT_ID
from musicleague.environment.variables import SPOTIFY_CLIENT_SECRET
from musicleague.environment.variables import SPOTIFY_REDIRECT_URI
from musicleague.league import create_league
from musicleague.spotify import BOT_SCOPES
from musicleague.spotify import create_or_update_playlist
from musicleague.spotify import create_playlist
from musicleague.spotify import get_spotify_oauth
from musicleague.spotify import OAUTH_SCOPES
from musicleague.spotify import to_uri
from musicleague.spotify import update_playlist
from musicleague.submission_period import create_submission_period
from musicleague.tests.utils.environment import set_environment_state
from musicleague.user import create_user


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


class CreatePlaylistTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    @patch('musicleague.bot.get_botify')
    def test_no_submission_period(self, get_bot):
        self.assertIsNone(create_playlist(None))
        self.assertFalse(get_bot.called)

    @patch(PATCH_PATH + 'user_playlist_created_notification')
    @patch('musicleague.bot.get_botify')
    def test_create_playlist(self, get_bot, notify):
        bot_id = 'bot_id'
        mock_botify = Mock(spec=Spotify)
        playlist_id = '6UeSakyzhiEt4NB3UAd6NQ'
        playlist_url = 'https://open.spotify.com/user/billboard.com/playlist/6UeSakyzhiEt4NB3UAd6NQ'  # noqa
        playlist = {'id': playlist_id,
                    'external_urls': {'spotify': playlist_url}}
        mock_botify.user_playlist_create.return_value = playlist
        get_bot.return_value = bot_id, mock_botify

        returned_playlist = create_playlist(self.submission_period)

        self.assertEqual(playlist, returned_playlist)

        self.assertTrue(get_bot.called)
        mock_botify.user_playlist_create.assert_called_once_with(
            bot_id, self.submission_period.name)
        mock_botify.user_playlist_add_tracks.assert_called_once_with(
            bot_id, playlist_id, self.submission_period.all_tracks)

        notify.assert_called_once_with(self.submission_period)


class UpdatePlaylistTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    @patch('musicleague.bot.get_botify')
    def test_no_submission_period(self, get_bot):
        self.assertIsNone(update_playlist(None))
        self.assertFalse(get_bot.called)

    @patch('musicleague.bot.get_botify')
    def test_no_submission_period_playlist_id(self, get_bot):
        self.assertIsNone(update_playlist(self.submission_period))
        self.assertFalse(get_bot.called)

    @patch('musicleague.bot.get_botify')
    def test_update_playlist(self, get_bot):
        playlist_id = '6UeSakyzhiEt4NB3UAd6NQ'
        playlist_url = 'https://open.spotify.com/user/billboard.com/playlist/6UeSakyzhiEt4NB3UAd6NQ'  # noqa
        playlist = {'id': playlist_id,
                    'external_urls': {'spotify': playlist_url}}
        self.submission_period.playlist_id = playlist_id
        self.submission_period.playlist_url = playlist_url
        self.submission_period.save()

        bot_id = 'bot_id'
        mock_botify = Mock(spec=Spotify)
        mock_botify.user_playlist.return_value = playlist
        get_bot.return_value = bot_id, mock_botify

        returned_playlist = update_playlist(self.submission_period)

        self.assertEqual(playlist, returned_playlist)

        self.assertTrue(get_bot.called)
        mock_botify.user_playlist_replace_tracks.assert_called_once_with(
            bot_id, playlist_id, self.submission_period.all_tracks)


class CreateOrUpdatePlaylistTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

        self.playlist_id = '6UeSakyzhiEt4NB3UAd6NQ'
        self.playlist_url = 'https://open.spotify.com/user/billboard.com/playlist/6UeSakyzhiEt4NB3UAd6NQ'  # noqa
        self.playlist = {'id': self.playlist_id,
                         'external_urls': {'spotify': self.playlist_url}}

        self.submission_period.playlist_id = self.playlist_id
        self.submission_period.playlist_url = self.playlist_url
        self.submission_period.save()

        self.bot_id = 'bot_id'
        self.mock_botify = Mock(spec=Spotify)
        self.mock_botify.user_playlist.return_value = self.playlist
        self.mock_botify.user_playlist_create.return_value = self.playlist

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    @patch('musicleague.bot.get_botify')
    def test_no_submission_period(self, get_bot):
        get_bot.return_value = self.bot_id, self.mock_botify

        self.assertIsNone(create_or_update_playlist(None))

        self.assertFalse(self.mock_botify.user_playlist_create.called)
        self.assertFalse(self.mock_botify.user_playlist_replace_tracks.called)

    @patch(PATCH_PATH + 'user_playlist_created_notification')
    @patch('musicleague.bot.get_botify')
    def test_create_playlist(self, get_bot, notify):
        get_bot.return_value = self.bot_id, self.mock_botify

        self.submission_period.playlist_url = ''
        self.submission_period.save()

        playlist = create_or_update_playlist(self.submission_period)

        self.assertEqual(self.playlist, playlist)
        self.assertFalse(self.mock_botify.user_playlist_replace_tracks.called)
        self.mock_botify.user_playlist_create.assert_called_once_with(
            self.bot_id, self.submission_period.name)
        notify.assert_called_once_with(self.submission_period)

    @patch('musicleague.bot.get_botify')
    def test_update_playlist(self, get_bot):
        get_bot.return_value = self.bot_id, self.mock_botify

        playlist = create_or_update_playlist(self.submission_period)

        self.assertEqual(self.playlist, playlist)
        self.assertFalse(self.mock_botify.user_playlist_create.called)
        self.mock_botify.user_playlist_replace_tracks.assert_called_once_with(
            self.bot_id, self.playlist_id, self.submission_period.all_tracks)


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
