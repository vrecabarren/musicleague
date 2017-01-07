import unittest

from mock import ANY
from mock import patch

from musicleague.league import create_league
from musicleague.submission_period import create_submission_period
from musicleague.submission_period.tasks import send_submission_reminders
from musicleague.user import create_user


PATCH_PATH = 'musicleague.submission_period.tasks.'


class SendSubmissionRemindersTestCase(unittest.TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test Period', 'Description')

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    @patch(PATCH_PATH + 'logging.error')
    def test_no_period_id(self, log_error):

        result = send_submission_reminders(None)

        self.assertFalse(result)
        log_error.assert_called_once_with(
            'No submission period id for submission reminders!')

    @patch(PATCH_PATH + 'logging.exception')
    def test_exception(self, log_exc):

        self.submission_period.league = None
        self.submission_period.save()

        result = send_submission_reminders(self.submission_period.id)

        self.assertFalse(result)
        log_exc.assert_called_once_with(
            'Error while sending submission reminders: %s', ANY)
        self.assertIsInstance(log_exc.call_args[0][1], AttributeError)

    @patch(PATCH_PATH + 'user_submit_reminder_notification')
    def test_success(self, notify):

        result = send_submission_reminders(self.submission_period.id)

        self.assertTrue(result)
        notify.assert_called_once_with(self.user, self.submission_period)
