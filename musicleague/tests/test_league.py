import unittest

from musicleague.league import create_league
from musicleague.user import create_user


class LeagueTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user("1", "Test User", "user@test.com", "")
        self.league = create_league(self.user)

    def tearDown(self):
        self.user.delete()
        self.league.delete()

    def test_remove_league(self):
        from musicleague.league import remove_league

        league = remove_league(self.league.id)

        self.assertIsNotNone(league)
        self.assertEqual(0, len(league.submission_periods))
