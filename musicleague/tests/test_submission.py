from unittest import TestCase

from mock import patch

from musicleague.models import League
from musicleague.models import Submission
from musicleague.models import SubmissionPeriod
from musicleague.models import User
from musicleague.submission import create_or_update_submission
from musicleague.submission import create_submission


class CreateOrUpdateSubmissionTestCase(TestCase):

    def setUp(self):
        self.submission_period = SubmissionPeriod()

        self.user = User()
        self.user.name = 'Old Gregg'
        self.user.email = 'old.gregg@test.com'

        self.league = League()
        self.league.submission_periods = self.league
        self.league.users.append(self.user)

        self.submission_period.league = self.league

        self.tracks = ['spotify:track:6Fha6tXHkL3r9m9nNqQG8p',
                       'spotify:track:6K4t31amVTZDgR3sKmwUJJ']

    @patch.object(SubmissionPeriod, 'save')
    @patch.object(Submission, 'save')
    def test_no_user_submission(self, submission_save, period_save):
        self.submission_period.submissions = []

        self.assertEqual([], self.submission_period.have_submitted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_not_submitted)

        submission = create_or_update_submission(
            self.tracks, self.submission_period, self.league, self.user)

        self.assertEqual([], self.submission_period.have_not_submitted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_submitted)

        submission.save.assert_called_once()
        self.assertEqual(1, submission.count)
        self.assertEqual(self.tracks, submission.tracks)
        self.assertEqual(self.user, submission.user)

        self.submission_period.save.assert_called_once()
        self.assertTrue(submission in self.submission_period.submissions)

    @patch.object(SubmissionPeriod, 'save')
    @patch.object(Submission, 'save')
    def test_existing_submission(self, submission_save, period_save):
        create_submission(self.tracks, self.submission_period, self.user, self.league)

        period_save.reset_mock()
        submission_save.reset_mock()

        new_tracks = ['spotify:track:6Fha6tXHkL3r9m9nNqQG8p',
                      'spotify:track:3ktdzyFa6N1ePp8T63DAik']

        self.assertEqual([], self.submission_period.have_not_submitted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_submitted)

        submission = create_or_update_submission(
            new_tracks, self.submission_period, self.league, self.user)

        self.assertEqual([], self.submission_period.have_not_submitted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_submitted)

        submission.save.assert_called_once()
        self.assertEqual(2, submission.count)
        self.assertEqual(new_tracks, submission.tracks)
        self.assertEqual(self.user, submission.user)

        self.submission_period.save.assert_not_called()
