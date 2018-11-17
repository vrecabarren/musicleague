import datetime
import mock
from unittest import TestCase

from musicleague.persistence.models import Round
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.models import Submission
from musicleague.persistence.models import Vote

from musicleague.breakdown.charts import build_voting_chart_datasets


class RoundVotingChartTestCase(TestCase):

    def setUp(self):
        self.round = Round("round-id", "league-id", "created", "name", "description", "playlist-url", RoundStatus.COMPLETE, "submissions-due", "votes-due")

        self.round.submissions = [
            Submission(mock.Mock(), ['uri', 'uri-2', 'uri-3'], 'created'),
        ]

        self.round.votes = [
            Vote(mock.Mock(), {'uri': 1, 'uri-2': 5}, {}, datetime.datetime(2018, 11, 20, 1, 0, 0)),
            Vote(mock.Mock(), {'uri': 3}, {}, datetime.datetime(2018, 11, 20, 2, 0, 0)),
            Vote(mock.Mock(), {'uri': -1}, {}, datetime.datetime(2018, 11, 20, 3, 0, 0)),
            Vote(mock.Mock(), {'uri': 2, 'uri-2': -3}, {}, datetime.datetime(2018, 11, 20, 4, 0, 0)),
        ]

    def test_report(self):
        report = build_voting_chart_datasets(self.round)

        self.assertIn('uri', report)
        self.assertEqual([0, 1, 4, 3, 5], report['uri'])
        self.assertIn('uri-2', report)
        self.assertEqual([0, 5, 5, 5, 2], report['uri-2'])
        self.assertIn('uri-3', report)
        self.assertEqual([0, 0, 0, 0, 0], report['uri-3'])

    def test_empty_if_round_not_complete(self):
        incomplete_round = self.round
        incomplete_round.status = RoundStatus.ACCEPTING_VOTES

        self.assertEqual({}, build_voting_chart_datasets(incomplete_round))

