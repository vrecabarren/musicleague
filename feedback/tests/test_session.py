from mock import patch

from unittest import TestCase

from feedback.errors import SessionExistsError
from feedback.models import Session
from feedback.session import create_session


@patch('feedback.session.get_session')
class CreateSessionTestCase(TestCase):

    def test_create_session_name_in_use(self, get_session):
        get_session.return_value = Session(name='name_in_use')

        self.assertRaises(SessionExistsError, create_session, 'name_in_use')
