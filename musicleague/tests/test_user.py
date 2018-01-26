from datetime import datetime
from unittest import TestCase

from musicleague.errors import UserExistsError
from musicleague.persistence.models import User
from musicleague.user import create_or_update_user
from musicleague.user import create_user
from musicleague.user import get_user
from musicleague.user import get_user_by_email


class CreateUserTestCase(TestCase):

    def setUp(self):
        self.id = '123'
        self.name = 'Test User'
        self.email = 'test_user@test.com'
        self.image_url = 'http://test.com/test_img.jpg'

    def test_create_user_existing_id(self):
        User(id=self.id, name=self.name, email=self.email,
             image_url=self.image_url, joined=datetime.utcnow())

        self.assertRaises(
            UserExistsError,
            create_user, self.id, self.name, self.email, self.image_url)

    def test_create_user_and_save(self):
        created = create_user(self.id, self.name, self.email, self.image_url)
        self.assertIsNotNone(created)
        self.assertEqual(self.name, created.name)
        self.assertEqual(self.email, created.email)
        self.assertEqual(self.image_url, created.image_url)

        saved = get_user(created.id)
        self.assertIsNotNone(saved)
        self.assertEqual(created.name, saved.name)
        self.assertEqual(created.email, saved.email)
        self.assertEqual(created.image_url, saved.image_url)
        self.assertEqual(created.preferences, saved.preferences)


class CreateOrUpdateUserTestCase(TestCase):

    def setUp(self):
        self.id = '123'
        self.name = 'Test User'
        self.email = 'test_user@test.com'
        self.image_url = 'http://test.com/test_img.jpg'

    def test_none_existing(self):
        self.assertIsNone(get_user(self.id))

        created = create_or_update_user(
            self.id, self.name, self.email, self.image_url)

        saved = get_user(self.id)
        self.assertIsNotNone(saved)
        self.assertEqual(created.name, saved.name)
        self.assertEqual(created.email, saved.email)
        self.assertEqual(created.image_url, saved.image_url)
        self.assertEqual(created.preferences, saved.preferences)

    def test_existing(self):
        User(id=self.id, name=self.name, email=self.email,
             image_url=self.image_url, joined=datetime.utcnow())

        updated = create_or_update_user(
            self.id, 'New Name', 'new_email@test.com', self.image_url)

        self.assertEqual('New Name', updated.name)
        self.assertEqual('new_email@test.com', updated.email)

        saved = get_user(self.id)
        self.assertIsNotNone(saved)
        self.assertEqual(updated.name, saved.name)
        self.assertEqual(updated.email, saved.email)
        self.assertEqual(updated.image_url, saved.image_url)
        self.assertEqual(updated.preferences, saved.preferences)


class GetUserTestCase(TestCase):

    def setUp(self):
        self.id = '123'
        self.name = 'Test User'
        self.email = 'test_user@test.com'
        self.image_url = 'http://test.com/test_img.jpg'

    def tearDown(self):
        clean_data()

    def test_none_existing(self):
        self.assertIsNone(get_user(self.id))

    def test_existing(self):
        User(id=self.id, name=self.name, email=self.email,
             image_url=self.image_url, joined=datetime.utcnow())

        user = get_user(self.id)
        self.assertIsNotNone(user)
        self.assertEqual(self.name, user.name)
        self.assertEqual(self.email, user.email)
        self.assertEqual(self.image_url, user.image_url)


class GetUserByEmailTestCase(TestCase):

    def setUp(self):
        self.id = '123'
        self.name = 'Test User'
        self.email = 'test_user@test.com'
        self.image_url = 'http://test.com/test_img.jpg'

    def test_none_existing(self):
        self.assertIsNone(get_user_by_email(self.email))

    def test_existing(self):
        User(id=self.id, name=self.name, email=self.email,
             image_url=self.image_url, joined=datetime.utcnow())

        user = get_user_by_email(self.email)
        self.assertIsNotNone(user)
        self.assertEqual(self.name, user.name)
        self.assertEqual(self.email, user.email)
        self.assertEqual(self.image_url, user.image_url)
