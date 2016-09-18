from unittest import TestCase

from mock import patch

from feedback.errors import UserExistsError
from feedback.models import User
from feedback.user import create_user
from feedback.user import get_user


class CreateUserTestCase(TestCase):

    @patch('feedback.user.get_user')
    def test_create_user_existing_id(self, get_user_mock):
        get_user_mock.return_value = User(id='1', email='test_user@test.com')
        self.assertRaises(
            UserExistsError,
            create_user, '1', 'Test User', 'test_user@test.com', '')

    def test_create_user_and_save(self):
        created = create_user('123', 'Test User', 'test_user@test.com', '')
        self.assertIsNotNone(created)
        self.assertEqual('Test User', created.name)
        self.assertEqual('test_user@test.com', created.email)
        self.assertEqual('', created.image_url)

        saved = get_user(created.id)
        self.assertIsNotNone(saved)
        self.assertEqual(created.name, saved.name)
        self.assertEqual(created.email, saved.email)
        self.assertEqual(created.image_url, saved.image_url)
        self.assertEqual(created.preferences, saved.preferences)
        saved.delete()
