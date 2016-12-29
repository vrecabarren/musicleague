import unittest

from mock import patch

from musicleague.league import create_league
from musicleague.models import MessengerContext
from musicleague.submission import create_submission
from musicleague.submission_period import create_submission_period
from musicleague.user import create_user
from musicleague.vote import create_vote


@patch('musicleague.notify.messenger.send_message')
class MessengerTestCase(unittest.TestCase):

    def setUp(self):
        self.owner = create_user('0123', 'Test Owner', 'owner@test.com', '')
        self.owner.messenger = MessengerContext(id="4321", user=self.owner)
        self.owner.save()

        self.league = create_league(self.owner)
        self.submission_period = create_submission_period(self.league)

        self.user = create_user('1234', 'Test User', 'user@test.com', '')

        self.tracks = ['spotify:track:4AqWZBWggL2op869E4EdR7']
        self.submission = create_submission(
            self.tracks, self.submission_period, self.user, self.league)

        self.votes = {uri: 1 for uri in self.tracks}
        self.vote = create_vote(
            self.votes, self.submission_period, self.user, self.league)

    def tearDown(self):
        self.owner.delete()
        self.user.delete()
        self.league.delete()
        self.submission_period.delete()
        self.submission.delete()

    def test_owner_all_users_submitted(self, send_message):
        from musicleague.notify.messenger import owner_all_users_submitted_messenger  # noqa

        owner_all_users_submitted_messenger(self.league.owner,
                                            self.submission_period)

        send_message.assert_called_once_with(
            self.league.owner.messenger.id,
            "All users have submitted for {}".format(
                self.submission_period.name))

    def test_owner_user_submitted(self, send_message):
        from musicleague.notify.messenger import owner_user_submitted_messenger

        owner_user_submitted_messenger(self.league.owner, self.submission)

        send_message.assert_called_once_with(
            self.league.owner.messenger.id,
            "{} just submitted for {}".format(self.user.name,
                                              self.submission_period.name))

    def test_owner_all_users_voted(self, send_message):
        from musicleague.notify.messenger import owner_all_users_voted_messenger  # noqa

        owner_all_users_voted_messenger(self.league.owner,
                                        self.submission_period)

        send_message.assert_called_once_with(
            self.league.owner.messenger.id,
            "All users have voted for {}".format(self.submission_period.name))

    def test_owner_user_voted(self, send_message):
        from musicleague.notify.messenger import owner_user_voted_messenger

        owner_user_voted_messenger(self.league.owner, self.vote)

        send_message.assert_called_once_with(
            self.league.owner.messenger.id,
            "{} just voted for {}".format(self.user.name,
                                          self.submission_period.name))
