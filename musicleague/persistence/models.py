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
    def first_name(self):
        return self.name.split(' ')[0]

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


class InvitedUser:
    def __init__(self, id, email, league_id):
        self.id = id
        self.email = email
        self.league_id = league_id


class Bot:
    def __init__(self, id, access_token, refresh_token, expires_at):
        self.id = id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at


class ScoreboardEntry:
    def __init__(self, uri, submission, **kwargs):
        self.place = kwargs.get('place', -1)
        self.submission = submission
        self.uri = uri
        self.votes = []

    @property
    def round(self):
        return self.submission.submission_period

    @property
    def is_valid(self):
        is_valid_began = utc.localize(datetime(2018, 2, 5))
        if self.round.vote_due_date < is_valid_began:
            return True

        if not self.round.is_complete:
            return True

        # If submitter voted, then this entry is valid
        from musicleague.vote import get_my_vote
        if get_my_vote(self.submission.user, self.round) is None:
            return False

        return True

    @property
    def points(self):
        if not self.is_valid:
            return self.downvote_points
        return self.potential_points

    @property
    def num_voters(self):
        return sum((1 for vote in self.votes if vote.votes.get(self.uri, 0) != 0))

    @property
    def upvotes(self):
        return [vote for vote in self.votes if vote.votes.get(self.uri, 0) > 0]
    
    @property
    def num_upvoters(self):
        return sum((1 for vote in self.upvotes))

    @property
    def downvotes(self):
        return [vote for vote in self.votes if vote.votes.get(self.uri, 0) < 0]

    @property
    def num_downvoters(self):
        return sum((1 for vote in self.downvotes))

    @property
    def num_commenters(self):
        return sum((1 for vote in self.votes if vote.comments.get(self.uri, '') != ''))

    @property
    def downvote_points(self):
        return sum([min(0, vote.votes.get(self.uri, 0)) for vote in self.votes])

    @property
    def upvote_points(self):
        return sum([max(0, vote.votes.get(self.uri, 0)) for vote in self.votes])

    @property
    def potential_points(self):
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

        # TODO Make reminder times configurable
        self.submission_reminder_time = 24
        self.vote_reminder_time = 24


class LeagueStatus:
    CREATED = 0
    IN_PROGRESS = 10
    COMPLETE = 20


class League:
    def __init__(self, id, created, name, owner_id, status):
        self.id = id
        self.created = created
        self.invited_users = []
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
    def is_active_v2(self):
        return not (self.is_inactive_v2 or self.is_complete_v2)

    @property
    def is_inactive(self):
        return len(self.submission_periods) == 0

    @property
    def is_inactive_v2(self):
        return self.status == LeagueStatus.CREATED

    @property
    def is_complete(self):
        return (not self.is_inactive and
                all((sp.is_complete for sp in self.submission_periods)))

    @property
    def is_complete_v2(self):
        return self.status == LeagueStatus.COMPLETE

    def has_owner(self, user):
        return self.owner_id and self.owner_id == user.id

    def has_user(self, user):
        return any((u for u in self.users if u.id == user.id))


class RoundStatus:
    CREATED = 0
    ACCEPTING_VOTES = 10
    COMPLETE = 20


class Round:
    def __init__(self, id, league_id, created, name, description, playlist_url, status, submissions_due, votes_due):
        self.id = id
        self.created = created
        self.name = name
        self.description = description
        self.league_id = league_id
        self.playlist_url = playlist_url
        self.scoreboard = Scoreboard()
        self.status = status
        self.submissions = []
        self.submission_due_date = submissions_due
        self.votes = []
        self.vote_due_date = votes_due

        # TODO Remove this
        # By populating the league_id attribute above, we can fetch league when needed
        self.league = None

    @property
    def playlist_created(self):
        return self.playlist_url != ''

    @property
    def accepting_submissions(self):
        """ Return True if the submission due date has not yet passed
        for this round and not all submissions have been received.
        """
        return self.status == RoundStatus.CREATED

    @property
    def accepting_votes(self):
        """ Return True if the submission due date has passed or all
        submissions have been received and the vote due date has not
        yet passed.
        """
        return self.status == RoundStatus.ACCEPTING_VOTES

    @property
    def all_tracks(self):
        """ Return the chain all submitted tracks together into a single list.
        This is useful for limiting the number of Spotify API calls.
        """
        all_tracks = []
        for submission in self.submissions:
            all_tracks.extend(filter(len, submission.tracks))
        return sorted(all_tracks)

    @property
    def have_not_submitted(self):
        """ Return the list of users who have not submitted yet. """
        u_idx = {u.id: u for u in self.league.users + self.have_submitted}
        league_member_ids = set([u.id for u in self.league.users])
        have_submitted_ids = set([u.id for u in self.have_submitted])
        have_not_submitted_ids = league_member_ids - have_submitted_ids
        return [u_idx.get(u_id) for u_id in have_not_submitted_ids]

    @property
    def have_not_voted(self):
        """ Return the list of users who have not voted yet.
        The potential list of users only includes those who
        submitted for this round.
        """
        u_idx = {u.id: u for u in self.have_submitted + self.have_voted}
        have_submitted_ids = set([u.id for u in self.have_submitted])
        have_voted_ids = set([u.id for u in self.have_voted])
        have_not_voted_ids = have_submitted_ids - have_voted_ids
        return [u_idx.get(u_id) for u_id in have_not_voted_ids]

    def user_submission(self, user):
        return next((s for s in self.submissions if s.user.id == user.id), None)

    def user_vote(self, user):
        return next((v for v in self.votes if v.user.id == user.id), None)

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
        return self.status == RoundStatus.COMPLETE

    @property
    def is_current(self):
        """ Return True if this round is the one currently accepting
        submissions or votes.
        """
        return self == self.league.current_submission_period

    @property
    def is_future(self):
        """ Return True if this round is not complete and is not
        currently accepting submissions or votes.
        """
        return not (self.is_complete or self.is_current)


class Submission:
    def __init__(self, user, tracks, comments, created):
        self.user = user
        self.tracks = tracks
        self.comments = comments
        self.created = created
        self.league = None
        self.submission_period = None
        self.count = 1


class Vote:
    def __init__(self, user, votes, comments, created):
        self.user = user
        self.votes = votes
        self.comments = comments
        self.created = created
        self.league = None
        self.submission_period = None
        self.count = 1


# NOTE Not persisted or used
class MessengerContext:
    def __init__(self, id, user, status=0):
        self.id = id
        self.user = user
        self.status = status
