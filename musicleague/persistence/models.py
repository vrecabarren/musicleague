from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
from pytz import utc
from random import choice
from time import time
import urlparse


class UserPreferences:
    def __init__(self):
        self.owner_all_users_submitted_notifications = True
        self.owner_all_users_voted_notifications = True
        self.owner_user_left_notifications = True
        self.owner_user_submitted_notifications = True
        self.owner_user_voted_notifications = True

        self.user_added_to_league_notifications = True
        self.user_playlist_created_notifications = True
        self.user_removed_from_league_notifications = True
        self.user_submit_reminder_notifications = True
        self.user_vote_reminder_notifications = True

    def settings_keys(self):
        return self.owner_keys() + self.user_keys()

    def user_keys(self):
        return sorted([k for k in self.__dict__.keys() if k.startswith('user_')])

    def owner_keys(self):
        return sorted([k for k in self.__dict__.keys() if k.startswith('owner_')])


class User:
    def __init__(self, id, email, image_url, is_admin, joined, name, profile_bg):
        self.id = id
        self.email = email
        self.image_url = image_url
        self.is_admin = is_admin
        self.joined = joined
        self.name = name
        self.preferences = UserPreferences()
        self.profile_background = profile_bg

    @property
    def guaranteed_image_url(self):
        parsed_image_url = urlparse.urlparse(self.image_url)
        if 'fbcdn' not in parsed_image_url.netloc:
            return self.image_url

        parsed_qs = urlparse.parse_qs(parsed_image_url.query)
        if 'oe' in parsed_qs and len(parsed_qs['oe']) > 0:
            hex_expiry = parsed_qs['oe'][0]
            expiry = int(hex_expiry, 16)
            if expiry < int(time()):
                from musicleague.user import DEFAULT_AVATARS
                return choice(DEFAULT_AVATARS)
        return self.image_url


class ScoreboardEntry:
    def __init__(self, uri, submission, **kwargs):
        self.submission = submission
        self.place = kwargs.get('place', -1)
        self.uri = uri
        self.votes = []

    @property
    def points(self):
        return sum([vote.votes.get(self.uri, 0) for vote in self.votes])


class RankingEntry:
    def __init__(self, league, user, **kwargs):
        self.user = user
        self.place = kwargs.get('place', -1)
        self.league = league
        self.entries = []

    @property
    def points(self):
        return sum([entry.points for entry in self.entries])


class Scoreboard:
    def __init__(self):
        self._rankings = defaultdict(list)

    def add_entry(self, entry, rank):
        self._rankings[rank].append(entry)

    @property
    def rankings(self):
        rankings = OrderedDict()
        for key in sorted(self._rankings.keys()):
            rankings[key] = self._rankings[key]
        return rankings

    @property
    def top(self):
        top = []

        if 1 in self.rankings:
            top.extend(self.rankings[1])
            if len(top) >= 3:
                return top[:3]

        if 2 in self.rankings:
            top.extend(self.rankings[2])
            if len(top) >= 3:
                return top[:3]

        if 3 in self.rankings:
            top.extend(self.rankings[3])
            if len(top) >= 3:
                return top[:3]

        return top


class LeaguePreferences:
    # TODO Not persisted/modifiable
    def __init__(self):
        self.track_count = 2
        self.point_bank_size = 6
        self.max_points_per_song = 0
        self.downvote_bank_size = 0
        self.max_downvotes_per_song = 0
        self.submission_reminder_time = 2
        self.vote_reminder_time = 2


class LeagueStatus:
    CREATED = 0
    IN_PROGRESS = 10
    COMPLETE = 20


class League:
    def __init__(self, id, created, name, owner_id, status):
        self.id = id
        self.created = created
        self.is_public = True
        self.name = name
        self.owner = None
        self.owner_id = owner_id
        self.preferences = LeaguePreferences()
        self.scoreboard = Scoreboard()
        self.status = status
        self.submission_periods = []
        self.users = []

    @property
    def current_submission_period(self):
        return next(
            (sp for sp in self.submission_periods if not sp.is_complete), None)

    @property
    def is_active(self):
        return not (self.is_inactive or self.is_complete)

    @property
    def is_inactive(self):
        return len(self.submission_periods) == 0

    @property
    def is_complete(self):
        return (not self.is_inactive and
                all((sp.is_complete for sp in self.submission_periods)))

    def has_owner(self, user):
        return self.owner and self.owner.id == user.id

    def has_user(self, user):
        return any((u for u in self.users if u.id == user.id))


class RoundStatus:
    CREATED = 0
    COMPLETE = 20


class Round:
    def __init__(self, id, league_id, created, name, description, playlist_url, submissions_due, votes_due):
        self.id = id
        self.created = created
        self.name = name
        self.description = description
        self.league_id = league_id
        self.playlist_url = playlist_url
        self.scoreboard = Scoreboard()
        self.submissions = []
        self.submission_due_date = submissions_due
        self.votes = []
        self.vote_due_date = votes_due

        # TODO Remove this
        # By populating the league_id attribute above, we can fetch league when needed
        self.league = None

        # TODO Remove this
        # This shouldn't need to be loaded/persisted every time the round is
        self.pending_tasks = {}

    @property
    def playlist_created(self):
        return self.playlist_url != ''

    @property
    def accepting_late_submissions(self):
        """ Return True if the league owner chose to accept late
        submissions and the vote due date for this round has not
        yet passed. Return False if all users have already submitted.

        NOTE: Currently hardcoded to return False
        """
        return (False and
                self.have_not_submitted and
                (self.vote_due_date > utc.localize(datetime.utcnow())))

    @property
    def accepting_submissions(self):
        """ Return True if the submission due date has not yet passed
        for this round and not all submissions have been received.
        """
        return (self.have_not_submitted and
                (self.submission_due_date > utc.localize(datetime.utcnow())))

    @property
    def accepting_votes(self):
        """ Return True if the submission due date has passed or all
        submissions have been received and the vote due date has not
        yet passed.
        """
        return ((not self.accepting_submissions) and
                self.have_not_voted and
                (self.vote_due_date > utc.localize(datetime.utcnow())))

    @property
    def all_tracks(self):
        """ Return the chain all submitted tracks together into a single list.
        This is useful for limiting the number of Spotify API calls.
        """
        all_tracks = []
        for submission in self.submissions:
            all_tracks.extend(filter(len, submission.tracks))
        return all_tracks

    @property
    def have_not_submitted(self):
        """ Return the list of users who have not submitted yet. """
        return list(set(self.league.users) - set(self.have_submitted))

    @property
    def have_not_voted(self):
        """ Return the list of users who have not voted yet.
        The potential list of users only includes those who
        submitted for this round.
        """
        return list(set(self.have_submitted) - set(self.have_voted))

    @property
    def have_submitted(self):
        """ Return the list of users who have submitted. """
        return [submission.user for submission in self.submissions]

    @property
    def have_voted(self):
        """ Return the list of users who have voted.
        The potential list of users only includes those who
        submitted for this round.
        """
        return [vote.user for vote in self.votes]

    @property
    def is_complete(self):
        """ Return True if voting due date for this round has
        passed or all submissions/votes are in.
        """
        if self.vote_due_date < utc.localize(datetime.utcnow()):
            return True
        return not (self.accepting_submissions or self.accepting_votes)

    @property
    def is_current_v2(self):
        """ Return True if this round is the one currently accepting
        submissions or votes.
        """
        return self == self.league.current_submission_period

    @property
    def is_future(self):
        """ Return True if this round is not complete and is not
        currently accepting submissions or votes.
        """
        return not (self.is_complete or self.is_current_v2)


class Submission:
    def __init__(self, user, tracks, created):
        self.user = user
        self.tracks = tracks
        self.created = created
        self.league = None
        self.submission_period = None
        self.count = 1


class Vote:
    def __init__(self, user, votes, created):
        self.user = user
        self.votes = votes
        self.created = created
        self.league = None
        self.submission_period = None
        self.count = 1
