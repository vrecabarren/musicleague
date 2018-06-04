from datetime import datetime
from unittest import TestCase

from mock import patch

from musicleague.league import create_league
from musicleague.persistence.select import select_round
from musicleague.submission_period import create_submission_period
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period import update_submission_period
from musicleague.user import create_user


class CreateSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

        create_submission_period(self.league)

    @patch('musicleague.submission_period.schedule_vote_reminders')
    @patch('musicleague.submission_period.schedule_submission_reminders')
    @patch('musicleague.submission_period.schedule_round_completion')
    @patch('musicleague.submission_period.schedule_playlist_creation')
    def test_create(self, schedule_playlist, schedule_round_completion,
                    schedule_submission_reminders, schedule_vote_reminders):
        created = create_submission_period(self.league)

        self.assertEqual('Round 2', created.name)
        self.assertEqual(self.league, created.league)

        saved = select_round(created.id)
        self.assertIsNotNone(saved)
        self.assertEqual(created.name, saved.name)
        self.assertEqual(created.league, saved.league)

        self.assertTrue(saved in self.league.submission_periods)

        schedule_playlist.assert_called_once_with(created)
        schedule_round_completion.assert_called_once_with(created)
        schedule_submission_reminders.assert_called_once_with(created)
        schedule_vote_reminders.assert_called_once_with(created)


class GetSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

    def test_none_existing(self):
        sp = create_submission_period(self.league)
        id = sp.id
        sp.delete()
        self.assertIsNone(select_round(id))

    def test_existing(self):
        id = create_submission_period(self.league).id

        sp = select_round(id)
        self.assertIsNotNone(sp)
        self.assertEqual(id, sp.id)
        self.assertEqual('Round 1', sp.name)


class RemoveSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

    @patch('musicleague.submission_period.cancel_pending_task')
    def test_none_existing(self, cancel_task):
        sp = create_submission_period(self.league)
        id = sp.id
        sp.delete()
        remove_submission_period(id)

        self.assertFalse(cancel_task.called)

    @patch('musicleague.submission_period.cancel_pending_task')
    def test_remove_existing(self, cancel_task):
        cancel_task.reset_mock()

        sp2 = create_submission_period(self.league)
        remove_submission_period(sp2.id)

        self.assertIsNone(select_round(sp2.id))


class UpdateSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

    def test_none_existing(self):
        sp = create_submission_period(self.league)
        id = sp.id
        sp.delete()

        sp = update_submission_period(id, 'New Name', 'New Description',
                                      datetime.utcnow(), datetime.utcnow())

        self.assertIsNone(sp)

    def test_update_existing(self):
        created = create_submission_period(self.league)

        updated = update_submission_period(
            created.id, 'New Name', 'New Description', datetime.utcnow(),
            datetime.utcnow())

        self.assertEqual('New Name', updated.name)

        saved = select_round(updated.id)
        self.assertIsNotNone(saved)
        self.assertEqual(updated.name, saved.name)
        self.assertEqual(updated.description, saved.description)
