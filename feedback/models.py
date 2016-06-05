from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import PULL
from mongoengine import ReferenceField
from mongoengine import StringField


class UserPreferences(EmbeddedDocument):
    owner_user_submitted_notifications = BooleanField(default=False)


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
    is_current = BooleanField(default=True)
    league = ReferenceField('League')
    name = StringField(max_length=255)
    playlist_id = StringField()
    playlist_url = StringField(default='')
    submissions = ListField(
        ReferenceField(Submission, reverse_delete_rule=PULL))

    @property
    def playlist_created(self):
        return self.playlist_url != ''


class League(Document):
    created = DateTimeField(required=True)
    due_date = DateTimeField()
    locked = BooleanField(default=False)
    name = StringField(primary_key=True, required=True)
    owner = ReferenceField(User)
    submission_periods = ListField(
        ReferenceField(SubmissionPeriod, reverse_delete_rule=PULL))
    users = ListField(ReferenceField(User, reverse_delete_rule=PULL))

    @property
    def current_submission_period(self):
        for submission_period in self.submission_periods:
            if submission_period.is_current:
                return submission_period
        return None
