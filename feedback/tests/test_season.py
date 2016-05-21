from mock import patch

from unittest import TestCase

from feedback.errors import SeasonExistsError
from feedback.models import Season
from feedback.models import User
from feedback.season import create_season


@patch('feedback.season.get_season')
class CreateSeasonTestCase(TestCase):

    def test_create_season_name_in_use(self, get_season):
        get_season.return_value = Season(name='name_in_use')

        self.assertRaises(
            SeasonExistsError,
            create_season, 'name_in_use',
            User(id='123', name='Test User', email='test_user@test_user.com'))
