from mock import patch

from unittest import TestCase

from feedback.errors import LeagueExistsError
from feedback.models import League
from feedback.models import User
from feedback.league import create_league


@patch('feedback.league.get_league')
class CreateLeagueTestCase(TestCase):

    def test_create_league_name_in_use(self, get_league):
        get_league.return_value = League(name='name_in_use')

        self.assertRaises(
            LeagueExistsError,
            create_league, 'name_in_use',
            User(id='123', name='Test User', email='test_user@test_user.com'))
