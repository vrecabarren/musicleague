import unittest

from mock import patch

from musicleague.league import create_league
from musicleague.models import InvitedUser
from musicleague.notify import owner_all_users_submitted_notification
from musicleague.notify import owner_all_users_voted_notification
from musicleague.notify import owner_user_submitted_notification
from musicleague.notify import owner_user_voted_notification
from musicleague.notify import user_added_to_league_notification
from musicleague.notify import user_invited_to_league_notification
from musicleague.notify import user_last_to_submit_notification
from musicleague.notify import user_last_to_vote_notification
from musicleague.notify import user_playlist_created_notification
from musicleague.notify import user_removed_from_league_notification
from musicleague.notify import user_submit_reminder_notification
from musicleague.notify import user_vote_reminder_notification
from musicleague.submission import create_submission
from musicleague.submission_period import create_submission_period
from musicleague.user import create_user
from musicleague.vote import create_vote


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
    def test_send(self, messenger, email):
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
    def test_send(self, messenger, email):
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
    def test_send(self, messenger, email):
        sent = owner_all_users_voted_notification(self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)
        messenger.assert_called_once_with(self.user, self.submission_period)


class OwnerUserVotedNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.owner = create_user('owner_id', 'Test Owner', 'test@user.com', '')
        self.league = create_league(self.owner)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.vote = create_vote(
            {}, self.submission_period, self.user, self.league)

    def tearDown(self):
        self.owner.delete()
        self.league.delete()
        self.submission_period.delete()
        self.user.delete()
        self.vote.delete()

    def test_no_submission(self):
        sent = owner_user_voted_notification(None)
        self.assertFalse(sent)

    def test_no_owner(self):
        self.league.owner = None
        self.league.save()

        sent = owner_user_voted_notification(self.vote)
        self.assertFalse(sent)

    def test_disabled(self):
        owner = self.league.owner
        owner.preferences.owner_user_voted_notifications = False
        owner.save()

        sent = owner_user_voted_notification(self.vote)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'owner_user_voted_email')
    @patch(PATCH_PATH + 'owner_user_voted_messenger')
    def test_send(self, messenger, email):
        sent = owner_user_voted_notification(self.vote)

        self.assertTrue(sent)
        email.assert_called_once_with(self.owner, self.vote)
        messenger.assert_called_once_with(self.owner, self.vote)


class UserAddedToLeagueNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)

    def tearDown(self):
        self.user.delete()
        self.league.delete()

    def test_no_league(self):
        sent = user_added_to_league_notification(self.user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_added_to_league_notification(None, self.league)
        self.assertFalse(sent)

    def test_disabled(self):
        self.user.preferences.user_added_to_league_notifications = False
        self.user.save()

        sent = user_added_to_league_notification(self.user, self.league)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_added_to_league_email')
    @patch(PATCH_PATH + 'user_added_to_league_messenger')
    def test_send(self, messenger, email):
        sent = user_added_to_league_notification(self.user, self.league)

        self.assertTrue(sent)
        messenger.assert_called_once_with(self.user, self.league)
        email.assert_called_once_with(self.user, self.league)


class UserInvitedToLeagueNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.invited_user = InvitedUser(email='test@user.com')
        self.invited_user.save()
        self.user = create_user('id', 'Test User', 'user@test.com', '')
        self.league = create_league(self.user)

    def tearDown(self):
        self.invited_user.delete()
        self.user.delete()
        self.league.delete()

    def test_no_league(self):
        sent = user_invited_to_league_notification(self.invited_user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_invited_to_league_notification(None, self.league)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_invited_to_league_email')
    def test_send(self, email):
        sent = user_invited_to_league_notification(
            self.invited_user, self.league)

        self.assertTrue(sent)
        email.assert_called_once_with(self.invited_user, self.league)


class UserLastToSubmitNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'user@test.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(self.league)

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = user_last_to_submit_notification(self.user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_last_to_submit_notification(None, self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_last_to_submit_email')
    @patch(PATCH_PATH + 'user_last_to_submit_messenger')
    def test_send(self, messenger, email):
        sent = user_last_to_submit_notification(
            self.user, self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)


class UserLastToVoteNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'user@test.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(self.league)

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = user_last_to_vote_notification(self.user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_last_to_vote_notification(None, self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_last_to_vote_email')
    @patch(PATCH_PATH + 'user_last_to_vote_messenger')
    def test_send(self, messenger, email):
        sent = user_last_to_vote_notification(
            self.user, self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)


class UserPlaylistCreatedNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'user@test.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(self.league)

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = user_playlist_created_notification(None)
        self.assertFalse(sent)

    def test_no_users(self):
        self.league.users = []
        self.league.save()
        sent = user_playlist_created_notification(self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_playlist_created_email')
    @patch(PATCH_PATH + 'user_playlist_created_messenger')
    def test_send(self, messenger, email):
        sent = user_playlist_created_notification(self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.submission_period)


class UserRemovedFromLeagueNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)

    def tearDown(self):
        self.user.delete()
        self.league.delete()

    def test_no_league(self):
        sent = user_removed_from_league_notification(self.user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_removed_from_league_notification(None, self.league)
        self.assertFalse(sent)

    def test_disabled(self):
        self.user.preferences.user_removed_from_league_notifications = False
        self.user.save()

        sent = user_removed_from_league_notification(self.user, self.league)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_removed_from_league_email')
    @patch(PATCH_PATH + 'user_removed_from_league_messenger')
    def test_send(self, messenger, email):
        sent = user_removed_from_league_notification(self.user, self.league)

        self.assertTrue(sent)
        messenger.assert_called_once_with(self.user, self.league)
        email.assert_called_once_with(self.user, self.league)


class UserSubmitReminderNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'user@test.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(self.league)

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = user_submit_reminder_notification(self.user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_submit_reminder_notification(None, self.submission_period)
        self.assertFalse(sent)

    def test_disabled(self):
        self.user.preferences.user_submit_reminder_notifications = False
        self.user.save()

        sent = user_submit_reminder_notification(
            self.user, self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_submit_reminder_email')
    @patch(PATCH_PATH + 'user_submit_reminder_messenger')
    def test_send(self, messenger, email):
        sent = user_submit_reminder_notification(
            self.user, self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)


class UserVoteReminderNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'user@test.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(self.league)

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    def test_no_submission_period(self):
        sent = user_vote_reminder_notification(self.user, None)
        self.assertFalse(sent)

    def test_no_user(self):
        sent = user_vote_reminder_notification(None, self.submission_period)
        self.assertFalse(sent)

    def test_disabled(self):
        self.user.preferences.user_vote_reminder_notifications = False
        self.user.save()

        sent = user_vote_reminder_notification(
            self.user, self.submission_period)
        self.assertFalse(sent)

    @patch(PATCH_PATH + 'user_vote_reminder_email')
    @patch(PATCH_PATH + 'user_vote_reminder_messenger')
    def test_send(self, messenger, email):
        sent = user_vote_reminder_notification(
            self.user, self.submission_period)

        self.assertTrue(sent)
        email.assert_called_once_with(self.user, self.submission_period)
