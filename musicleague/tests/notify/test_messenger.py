import unittest

from mock import call
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
        self.user.messenger = MessengerContext(id="3210", user=self.user)
        self.user.save()

        self.league.users.append(self.user)
        self.league.save()

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
        self.vote.delete()

    def test_owner_user_submitted(self, send_message):
        from musicleague.notify.messenger import owner_user_submitted_messenger

        owner_user_submitted_messenger(self.league.owner, self.submission)

        send_message.assert_called_once_with(
            self.league.owner.messenger.id,
            "{} just submitted for {}".format(self.user.name,
                                              self.submission_period.name))

    def test_owner_user_voted(self, send_message):
        from musicleague.notify.messenger import owner_user_voted_messenger

        owner_user_voted_messenger(self.league.owner, self.vote)

        send_message.assert_called_once_with(
            self.league.owner.messenger.id,
            "{} just voted for {}".format(self.user.name,
                                          self.submission_period.name))

    @patch('musicleague.notify.messenger.url_for')
    def test_user_added_to_league(self, url_for, send_message):
        from musicleague.notify.messenger import user_added_to_league_messenger

        user_added_to_league_messenger(self.user, self.league)

        self.assertEqual(1, send_message.call_count)
        url_for.assert_called_once_with(
            'view_league', league_id=self.league.id, _external=True)

    @patch('musicleague.notify.messenger.url_for')
    def test_user_last_to_submit(self, url_for, send_message):
        from musicleague.notify.messenger import user_last_to_submit_messenger

        user_last_to_submit_messenger(self.user, self.submission_period)

        self.assertEqual(1, send_message.call_count)
        url_for.assert_called_once_with(
            'view_submit', league_id=self.league.id,
            submission_period_id=self.submission_period.id, _external=True)

    @patch('musicleague.notify.messenger.url_for')
    def test_user_last_to_vote(self, url_for, send_message):
        from musicleague.notify.messenger import user_last_to_vote_messenger

        user_last_to_vote_messenger(self.user, self.submission_period)

        self.assertEqual(1, send_message.call_count)
        url_for.assert_called_once_with(
            'view_vote', league_id=self.league.id,
            submission_period_id=self.submission_period.id, _external=True)

    def test_user_playlist_created(self, send_message):
        from musicleague.notify.messenger import user_playlist_created_messenger  # noqa

        url = 'https://open.spotify.com/user/billboard.com/playlist/6UeSakyzhiEt4NB3UAd6NQ'  # noqa
        self.submission_period.playlist_url = url
        self.submission_period.save()

        user_playlist_created_messenger(self.submission_period)

        send_message.assert_has_calls([
            call(self.owner.messenger.id,
                 "A new playlist has been created for {}.\n"
                 "Listen to it here: {}".format(
                     self.submission_period.name, url)),
            call(self.user.messenger.id,
                 "A new playlist has been created for {}.\n"
                 "Listen to it here: {}".format(
                     self.submission_period.name, url))
        ])

    def test_user_removed_from_league(self, send_message):
        from musicleague.notify.messenger import user_removed_from_league_messenger  # noqa

        user_removed_from_league_messenger(self.user, self.league)

        send_message.assert_called_once_with(
            self.user.messenger.id,
            "You've been removed from the league {}".format(self.league.name))

    @patch('musicleague.notify.messenger.url_for')
    def test_user_submit_reminder(self, url_for, send_message):
        from musicleague.notify.messenger import user_submit_reminder_messenger

        user_submit_reminder_messenger(self.user, self.submission_period)

        self.assertEqual(1, send_message.call_count)
        url_for.assert_called_once_with(
            'view_submit', league_id=self.league.id,
            submission_period_id=self.submission_period.id,
            _external=True)

    @patch('musicleague.notify.messenger.url_for')
    def test_user_vote_reminder(self, url_for, send_message):
        from musicleague.notify.messenger import user_vote_reminder_messenger

        user_vote_reminder_messenger(self.user, self.submission_period)

        self.assertEqual(1, send_message.call_count)
        url_for.assert_called_once_with(
            'view_vote', league_id=self.league.id,
            submission_period_id=self.submission_period.id,
            _external=True)
