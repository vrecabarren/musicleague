import time
import unittest

from spotipy import Spotify

from musicleague.bot import create_bot
from musicleague.environment.variables import SPOTIFY_BOT_USERNAME
from musicleague.tests.utils.environment import set_environment_state


class GetBotifyTestCase(unittest.TestCase):

    def setUp(self):
        self.bot_id = 'bot_id'
        self.access_token = 'access_token'
        self.refresh_token = 'refresh_token'
        self.expires_at = 1

        set_environment_state(SPOTIFY_BOT_USERNAME.key, self.bot_id)

        self.bot = create_bot(self.bot_id, self.access_token,
                              self.refresh_token, self.expires_at)

    def tearDown(self):
        self.bot.delete()

    def test_no_bot(self):
        from musicleague.bot import get_botify

        self.bot.delete()

        bot_id, bot = get_botify()

        self.assertIsNone(bot_id)
        self.assertIsNone(bot)

    def test_bot_not_expired(self):
        from musicleague.bot import get_botify

        self.bot.expires_at = int(time.time()) + 999
        self.bot.save()

        bot_id, bot = get_botify()

        self.assertEqual(self.bot_id, bot_id)
        self.assertIsInstance(bot, Spotify)
        self.assertEqual(self.access_token, bot._auth)
