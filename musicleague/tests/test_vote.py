from unittest import TestCase

from mock import patch

from musicleague.models import League
from musicleague.models import SubmissionPeriod
from musicleague.models import User
from musicleague.models import Vote
from musicleague.vote import create_or_update_vote
from musicleague.vote import create_vote


class CreateOrUpdateVoteTestCase(TestCase):

    def setUp(self):
        self.submission_period = SubmissionPeriod()

        self.user = User()
        self.user.name = 'Old Gregg'
        self.user.email = 'old.gregg@test.com'

        self.league = League()
        self.league.submission_periods = self.league
        self.league.users.append(self.user)

        self.submission_period.league = self.league

        self.votes = {'spotify:track:6Fha6tXHkL3r9m9nNqQG8p': 1,
                      'spotify:track:6K4t31amVTZDgR3sKmwUJJ': 0}

    @patch.object(SubmissionPeriod, 'save')
    @patch.object(Vote, 'save')
    def test_no_user_submission(self, vote_save, period_save):
        self.submission_period.submissions = []

        vote = create_or_update_vote(
            self.votes, self.submission_period, self.league, self.user)

        vote.save.assert_called_once()
        self.assertEqual(1, vote.count)
        self.assertEqual(self.votes, vote.votes)
        self.assertEqual(self.user, vote.user)

        self.submission_period.save.assert_called_once()
        self.assertTrue(vote in self.submission_period.votes)

    @patch.object(SubmissionPeriod, 'save')
    @patch.object(Vote, 'save')
    def test_existing_submission(self, submission_save, period_save):
        self.submission_period.votes = [
            create_vote(
                self.votes, self.submission_period, self.user, self.league)]

        period_save.reset_mock()
        submission_save.reset_mock()

        new_votes = {'spotify:track:6Fha6tXHkL3r9m9nNqQG8p': 3,
                     'spotify:track:6K4t31amVTZDgR3sKmwUJJ': 2}

        vote = create_or_update_vote(
            new_votes, self.submission_period, self.league, self.user)

        vote.save.assert_called_once()
        self.assertEqual(2, vote.count)
        self.assertEqual(new_votes, vote.votes)
        self.assertEqual(self.user, vote.user)

        self.submission_period.save.assert_not_called()
