import unittest

from mock import patch

from musicleague.league import create_league
from musicleague.notify import owner_all_users_submitted_notification
from musicleague.notify import owner_all_users_voted_notification
from musicleague.notify import owner_user_submitted_notification
from musicleague.submission import create_submission
from musicleague.submission_period import create_submission_period
from musicleague.user import create_user


PATCH_PATH = 'musicleague.notify.'


class OwnerAllUsersSubmittedNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = owner_all_users_submitted_notification(None)
        self.assertFalse(sent)

    def test_no_owner(self):
        self.league.owner = None
        self.league.save()

        sent = owner_all_users_submitted_notification(self.submission_period)
        self.assertFalse(sent)

    def test_disabled(self):
        owner = self.league.owner
        owner.preferences.owner_all_users_submitted_notifications = False
        owner.save()

        sent = owner_all_users_submitted_notification(self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'owner_all_users_submitted_email')
    @patch(PATCH_PATH + 'owner_all_users_submitted_messenger')
    def test_send(self, email, messenger):
        sent = owner_all_users_submitted_notification(self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)
        messenger.assert_called_once_with(self.user, self.submission_period)


class OwnerUserSubmittedNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.owner = create_user('owner_id', 'Test Owner', 'test@user.com', '')
        self.league = create_league(self.owner)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.submission = create_submission(
            [], self.submission_period, self.user, self.league)

    def tearDown(self):
        self.owner.delete()
        self.league.delete()
        self.submission_period.delete()
        self.user.delete()
        self.submission.delete()

    def test_no_submission(self):
        sent = owner_user_submitted_notification(None)
        self.assertFalse(sent)

    def test_no_owner(self):
        self.league.owner = None
        self.league.save()

        sent = owner_user_submitted_notification(self.submission)
        self.assertFalse(sent)

    def test_disabled(self):
        owner = self.league.owner
        owner.preferences.owner_user_submitted_notifications = False
        owner.save()

        sent = owner_user_submitted_notification(self.submission)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'owner_user_submitted_email')
    @patch(PATCH_PATH + 'owner_user_submitted_messenger')
    def test_send(self, email, messenger):
        sent = owner_user_submitted_notification(self.submission)

        self.assertTrue(sent)
        email.assert_called_once_with(self.owner, self.submission)
        messenger.assert_called_once_with(self.owner, self.submission)


class OwnerAllUsersVotedNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = owner_all_users_voted_notification(None)
        self.assertFalse(sent)

    def test_no_owner(self):
        self.league.owner = None
        self.league.save()

        sent = owner_all_users_voted_notification(self.submission_period)
        self.assertFalse(sent)

    def test_disabled(self):
        owner = self.league.owner
        owner.preferences.owner_all_users_voted_notifications = False
        owner.save()

        sent = owner_all_users_voted_notification(self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'owner_all_users_voted_email')
    @patch(PATCH_PATH + 'owner_all_users_voted_messenger')
    def test_send(self, email, messenger):
        sent = owner_all_users_voted_notification(self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)
        messenger.assert_called_once_with(self.user, self.submission_period)
