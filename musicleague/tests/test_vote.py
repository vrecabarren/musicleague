from unittest import TestCase

from mock import patch

from musicleague.league import create_league
from musicleague.models import SubmissionPeriod
from musicleague.models import Vote
from musicleague.submission import create_submission
from musicleague.submission_period import create_submission_period
from musicleague.user import create_user
from musicleague.vote import create_or_update_vote
from musicleague.vote import create_vote


class CreateOrUpdateVoteTestCase(TestCase):

    def setUp(self):
        self.user = create_user('id', 'Test User', 'test@user.com', '')
        self.league = create_league(self.user)
        self.submission_period = create_submission_period(
            self.league, 'Test League', 'Description')

        self.votes = {'spotify:track:6Fha6tXHkL3r9m9nNqQG8p': 1,
                      'spotify:track:6K4t31amVTZDgR3sKmwUJJ': 0}

    def tearDown(self):
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()

    @patch.object(SubmissionPeriod, 'save')
    @patch.object(Vote, 'save')
    def test_no_user_submission(self, vote_save, period_save):
        self.submission_period.votes = []

        create_submission([], self.submission_period, self.user, self.league)

        self.assertEqual([], self.submission_period.have_voted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_not_voted)

        vote = create_or_update_vote(
            self.votes, self.submission_period, self.league, self.user)

        self.assertEqual([], self.submission_period.have_not_voted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_voted)

        vote.save.assert_called_once()
        self.assertEqual(1, vote.count)
        self.assertEqual(self.votes, vote.votes)
        self.assertEqual(self.user, vote.user)

        self.assertTrue(vote in self.submission_period.votes)

    @patch.object(SubmissionPeriod, 'save')
    @patch.object(Vote, 'save')
    def test_existing_submission(self, vote_save, period_save):
        self.submission_period.votes = [
            create_vote(
                self.votes, self.submission_period, self.user, self.league)]

        period_save.reset_mock()
        vote_save.reset_mock()

        new_votes = {'spotify:track:6Fha6tXHkL3r9m9nNqQG8p': 3,
                     'spotify:track:6K4t31amVTZDgR3sKmwUJJ': 2}

        self.assertEqual([], self.submission_period.have_not_voted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_voted)

        vote = create_or_update_vote(
            new_votes, self.submission_period, self.league, self.user)

        self.assertEqual([], self.submission_period.have_not_voted)
        self.assertEqual(self.league.users,
                         self.submission_period.have_voted)

        vote.save.assert_called_once()
        self.assertEqual(2, vote.count)
        self.assertEqual(new_votes, vote.votes)
        self.assertEqual(self.user, vote.user)

        self.submission_period.save.assert_not_called()
