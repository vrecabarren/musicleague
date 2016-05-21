from mock import patch

from unittest import TestCase

from feedback.errors import SessionExistsError
from feedback.models import Session
from feedback.season import create_season


@patch('feedback.season.get_season')
class CreateSessionTestCase(TestCase):

    def test_create_session_name_in_use(self, get_season):
        get_season.return_value = Session(name='name_in_use')

        self.assertRaises(SessionExistsError, create_season, 'name_in_use')
