from datetime import datetime

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import DictField
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import PULL
from mongoengine import ReferenceField
from mongoengine import StringField


class UserPreferences(EmbeddedDocument):
    OWNER_PREFERENCE_ROLE = 'owner'
    USER_PREFERENCE_ROLE = 'user'

    owner_all_users_submitted_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when all users have submitted')
    owner_all_users_voted_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when all users have voted')
    owner_user_left_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when a user leaves')
    owner_user_submitted_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when a user submits')
    owner_user_voted_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when a user votes')

    user_added_to_league_notifications = BooleanField(
        default=True, role=USER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when added to a new league')
    user_playlist_created_notifications = BooleanField(
        default=True, role=USER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when a new playlist is created')
    user_removed_from_league_notifications = BooleanField(
        default=True, role=USER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when removed from a league')
    user_submit_reminder_notifications = BooleanField(
        default=True, role=USER_PREFERENCE_ROLE,
        verbose_name='Receive a reminder before the submission due date')
    user_vote_reminder_notifications = BooleanField(
        default=True, role=USER_PREFERENCE_ROLE,
        verbose_name='Receive a reminder before the vote due date')


class MessengerContext(Document):
    id = StringField(primary_key=True, required=True)
    status = IntField(required=False, default=0)
    user = ReferenceField('User')


class User(Document):
    ADMIN = 'admin'

    id = StringField(primary_key=True, required=True)
    email = StringField(required=True)
    image_url = StringField(required=False, default='')
    joined = DateTimeField(required=True)
    messenger = ReferenceField(MessengerContext)
    name = StringField(required=False, default='')
    preferences = EmbeddedDocumentField(UserPreferences)
    profile_background = StringField(required=False, default='')
    roles = ListField(required=False, default=[])

    @property
    def first_name(self):
        return self.name.split(' ')[0]

    @property
    def is_admin(self):
        return self.ADMIN in self.roles


class Bot(Document):
    id = StringField(primary_key=True, required=True)
    access_token = StringField(required=True)
    refresh_token = StringField(required=True)
    expires_at = IntField(required=True)


class InvitedUser(Document):
    email = StringField(required=True)


class Submission(Document):
    confirmed = BooleanField(default=False)
    count = IntField(default=1)
    created = DateTimeField(required=True)
    league = ReferenceField('League')
    submission_period = ReferenceField('SubmissionPeriod')
    tracks = ListField(default=[])
    updated = DateTimeField()
    user = ReferenceField(User)


class Vote(Document):
    count = IntField(default=1)
    created = DateTimeField(required=True)
    league = ReferenceField('League')
    submission_period = ReferenceField('SubmissionPeriod')
    updated = DateTimeField()
    user = ReferenceField(User)
    votes = DictField()


class ScoreboardEntry(EmbeddedDocument):
    uri = StringField(required=True)
    submission = ReferenceField(Submission)
    votes = ListField(ReferenceField(Vote))

    @property
    def points(self):
        points = 0
        for vote in self.votes:
            points += vote.votes.get(self.uri, 0)
        return points


class Scoreboard(EmbeddedDocument):
    _rankings = DictField()

    @property
    def rankings(self):
        rankings = {}
        int_keys = sorted([int(key) for key in self._rankings])
        for key in int_keys:
            rankings[key] = self._rankings[str(key)]
        return rankings


class SubmissionPeriod(Document):
    created = DateTimeField()
    complete = BooleanField(default=False)
    description = StringField(max_length=255)
    submission_due_date = DateTimeField()
    vote_due_date = DateTimeField()
    is_current = BooleanField(default=True)
    league = ReferenceField('League')
    name = StringField(max_length=255)
    pending_tasks = DictField()
    playlist_id = StringField()
    playlist_url = StringField(default='')
    scoreboard = EmbeddedDocumentField(Scoreboard)
    submissions = ListField(ReferenceField(Submission,
                                           reverse_delete_rule=PULL))
    votes = ListField(ReferenceField(Vote, reverse_delete_rule=PULL))

    @property
    def playlist_created(self):
        return self.playlist_url != ''

    @property
    def accepting_submissions(self):
        return ((len(self.submissions) < len(self.league.users)) and
                (self.submission_due_date > datetime.utcnow()))

    @property
    def accepting_late_submissions(self):
        return (self.league.preferences.late_submissions and
                (len(self.submissions) < len(self.league.users)) and
                (self.vote_due_date > datetime.utcnow()))

    @property
    def have_submitted(self):
        return [submission.user for submission in self.submissions]

    @property
    def have_not_submitted(self):
        return list(set(self.league.users) - set(self.have_submitted))

    @property
    def accepting_votes(self):
        return ((not self.accepting_submissions) and
                (len(self.votes) < len(self.league.users)) and
                (self.vote_due_date > datetime.utcnow()))

    @property
    def have_voted(self):
        return [vote.user for vote in self.votes]

    @property
    def have_not_voted(self):
        return list(set(self.league.users) - set(self.have_voted))

    @property
    def all_tracks(self):
        all_tracks = []
        for submission in self.submissions:
            all_tracks.extend(filter(len, submission.tracks))
        return all_tracks

    @property
    def is_complete(self):
        if self.vote_due_date < datetime.utcnow():
            return True
        return not (self.accepting_submissions or self.accepting_votes)

    @property
    def is_current_v2(self):
        return self == self.league.current_submission_period


class LeaguePreferences(EmbeddedDocument):
    CHECKBOX = "checkbox"
    NUMBER = "number"
    POINT_BANK = "pb"

    name = StringField()

    auto_playlist_creation = BooleanField(
        default=True, display_name='Auto Playlist Creation', new=True,
        input_type=CHECKBOX,
        verbose_name='When submitting ends, the playlist will be created.')
    auto_submission_periods = BooleanField(
        default=True, display_name='Auto Submission Periods', new=True,
        input_type=CHECKBOX,
        verbose_name='When voting ends, the next period will be created.')
    late_submissions = BooleanField(
        default=True, display_name='Late Submissions', input_type=CHECKBOX,
        verbose_name='Allow submissions after the deadline has passed.')
    locked = BooleanField(
        default=False, display_name='Locked', new=True, input_type=CHECKBOX,
        verbose_name='Submitting and voting are disabled.')
    submission_reminder_time = IntField(
        default=2, display_name='Submission Reminder Time', input_type=NUMBER,
        verbose_name=('How many hours prior to the due date should submission '
                      'reminders be sent?'), new=True)
    vote_reminder_time = IntField(
        default=2, display_name='Vote Reminder Time', input_type=NUMBER,
        verbose_name=('How many hours prior to the due data should vote '
                      'reminders be sent?'), new=True)
    track_count = IntField(
        default=2, display_name='# Tracks', input_type=NUMBER,
        verbose_name='How many songs should each submission include?')
    voting_style = StringField(choices=(POINT_BANK,))
    point_bank_size = IntField(
        default=8, display_name='Point Bank Size', input_type=NUMBER,
        verbose_name='How many points should each user have to vote with?')


class League(Document):
    created = DateTimeField(required=True)
    owner = ReferenceField(User)
    submission_periods = ListField(
        ReferenceField(SubmissionPeriod, reverse_delete_rule=PULL))
    users = ListField(ReferenceField(User, reverse_delete_rule=PULL))
    invited_users = ListField(ReferenceField(InvitedUser,
                                             reverse_delete_rule=PULL))
    preferences = EmbeddedDocumentField(LeaguePreferences)
    scoreboard = EmbeddedDocumentField(Scoreboard)

    @property
    def name(self):
        return self.preferences.name

    @property
    def current_submission_period(self):
        return next(
            (sp for sp in self.submission_periods if not sp.is_complete), None)

    @property
    def is_inactive(self):
        return len(self.submission_periods) == 0

    @property
    def is_complete(self):
        return (not self.is_inactive and
                all((sp.is_complete for sp in self.submission_periods)))

    def has_owner(self, user):
        return self.owner == user

    def has_user(self, user):
        return user in self.users


ALL_MODELS = [UserPreferences, User, InvitedUser, Submission, Vote,
              SubmissionPeriod, LeaguePreferences, League, MessengerContext]
