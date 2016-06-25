from datetime import datetime

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import IntField
from mongoengine import DictField
from mongoengine import ListField
from mongoengine import PULL
from mongoengine import ReferenceField
from mongoengine import StringField


class UserPreferences(EmbeddedDocument):
    OWNER_PREFERENCE_ROLE = 'owner'
    USER_PREFERENCE_ROLE = 'user'

    owner_user_left_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when a contributor leaves')
    owner_user_submitted_notifications = BooleanField(
        default=True, role=OWNER_PREFERENCE_ROLE,
        verbose_name='Receive a notification when a contributor submits')

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


class User(Document):
    id = IntField(primary_key=True, required=True)
    email = StringField(required=True)
    image_url = StringField(required=True)
    joined = DateTimeField(required=True)
    name = StringField(required=True)
    preferences = EmbeddedDocumentField(UserPreferences)


class Submission(Document):
    confirmed = BooleanField(default=False)
    count = IntField(default=1)
    created = DateTimeField(required=True)
    league = ReferenceField('League')
    submission_period = ReferenceField('SubmissionPeriod')
    tracks = ListField(default=[])
    updated = DateTimeField()
    user = ReferenceField(User)


class SubmissionPeriod(Document):
    complete = BooleanField(default=False)
    submission_due_date = DateTimeField()
    vote_due_date = DateTimeField()
    is_current = BooleanField(default=True)
    league = ReferenceField('League')
    name = StringField(max_length=255)
    pending_tasks = DictField()
    playlist_id = StringField()
    playlist_url = StringField(default='')
    submissions = ListField(
        ReferenceField(Submission, reverse_delete_rule=PULL))

    @property
    def playlist_created(self):
        return self.playlist_url != ''

    @property
    def accepting_submissions(self):
        return self.submission_due_date > datetime.utcnow()

    @property
    def accepting_votes(self):
        return (
            self.vote_due_date > datetime.utcnow() > self.submission_due_date)

    @property
    def all_tracks(self):
        all_tracks = []
        for submission in self.submissions:
            all_tracks.extend(submission.tracks)
        return all_tracks


class LeaguePreferences(EmbeddedDocument):
    CHECKBOX = "checkbox"
    NUMBER = "number"

    name = StringField()

    auto_playlist_creation = BooleanField(
        default=True, display_name='Auto Playlist Creation', new=True,
        input_type=CHECKBOX,
        verbose_name='When submitting ends, the playlist will be created.')
    auto_submission_periods = BooleanField(
        default=True, display_name='Auto Submission Periods', new=True,
        input_type=CHECKBOX,
        verbose_name='When voting ends, the next period will be created.')
    locked = BooleanField(
        default=False, display_name='Locked', input_type=CHECKBOX,
        verbose_name='Submitting and voting are disabled.')
    track_count = IntField(
        default=2, display_name='# Tracks', input_type=NUMBER,
        verbose_name='How many songs should each submission include?')

    checkbox_display_order = ['auto_playlist_creation',
                              'locked']


class League(Document):
    created = DateTimeField(required=True)
    owner = ReferenceField(User)
    submission_periods = ListField(
        ReferenceField(SubmissionPeriod, reverse_delete_rule=PULL))
    users = ListField(ReferenceField(User, reverse_delete_rule=PULL))
    preferences = EmbeddedDocumentField(LeaguePreferences)

    @property
    def name(self):
        return self.preferences.name

    @property
    def current_submission_period(self):
        for submission_period in self.submission_periods:
            if submission_period.is_current:
                return submission_period
        return None

    def has_owner(self, user):
        return self.owner == user
