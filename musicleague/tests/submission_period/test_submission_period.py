from datetime import datetime
from unittest import TestCase

from mock import patch

from musicleague.league import create_league
from musicleague.submission_period import create_submission_period
from musicleague.submission_period import get_submission_period
from musicleague.submission_period import remove_submission_period
from musicleague.submission_period import update_submission_period
from musicleague.tests.utils.data import clean_data
from musicleague.user import create_user


class CreateSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

        create_submission_period(self.league)

    def tearDown(self):
        clean_data()

    @patch('musicleague.submission_period.schedule_vote_reminders')
    @patch('musicleague.submission_period.schedule_submission_reminders')
    @patch('musicleague.submission_period.schedule_playlist_creation')
    def test_create(self, schedule_playlist, schedule_submission_reminders,
                    schedule_vote_reminders):
        created = create_submission_period(self.league)

        self.assertEqual('Submission Period 2', created.name)
        self.assertEqual(self.league, created.league)

        saved = get_submission_period(created.id)
        self.assertIsNotNone(saved)
        self.assertEqual(created.name, saved.name)
        self.assertEqual(created.league, saved.league)

        self.assertTrue(saved in self.league.submission_periods)

        schedule_playlist.assert_called_once_with(created)
        schedule_submission_reminders.assert_called_once_with(created)
        schedule_vote_reminders.assert_called_once_with(created)


class GetSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

    def tearDown(self):
        clean_data()

    def test_none_existing(self):
        sp = create_submission_period(self.league)
        id = sp.id
        sp.delete()
        self.assertIsNone(get_submission_period(id))

    def test_existing(self):
        id = create_submission_period(self.league).id

        sp = get_submission_period(id)
        self.assertIsNotNone(sp)
        self.assertEqual(id, sp.id)
        self.assertEqual('Submission Period 1', sp.name)


class RemoveSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

    def tearDown(self):
        clean_data()

    @patch('musicleague.submission_period._cancel_pending_task')
    def test_none_existing(self, cancel_task):
        sp = create_submission_period(self.league)
        id = sp.id
        sp.delete()
        remove_submission_period(id)

        self.assertFalse(cancel_task.called)

    @patch('musicleague.submission_period._cancel_pending_task')
    def test_remove_existing(self, cancel_task):
        cancel_task.reset_mock()

        sp2 = create_submission_period(self.league)
        remove_submission_period(sp2.id)

        self.assertEqual(len(sp2.pending_tasks), cancel_task.call_count)
        self.assertIsNone(get_submission_period(sp2.id))


class UpdateSubmissionPeriodTestCase(TestCase):

    def setUp(self):
        self.user = create_user('123', 'Test User', 'test_user@test.com', '')
        self.league = create_league(self.user)

    def tearDown(self):
        clean_data()

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

        saved = get_submission_period(updated.id)
        self.assertIsNotNone(saved)
        self.assertEqual(updated.name, saved.name)
        self.assertEqual(updated.description, saved.description)
