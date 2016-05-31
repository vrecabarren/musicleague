from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import PULL
from mongoengine import ReferenceField
from mongoengine import StringField


class User(Document):
    id = IntField(primary_key=True, required=True)
    name = StringField(required=True)
    email = StringField(required=True)
    image_url = StringField(required=True)
    joined = DateTimeField(required=True)


class Submission(Document):
    confirmed = BooleanField(default=False)
    count = IntField(default=1)
    created = DateTimeField(required=True)
    tracks = ListField(default=[])
    user = ReferenceField(User)


class SubmissionPeriod(Document):
    complete = BooleanField(default=False)
    is_current = BooleanField(default=True)
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
    users = ListField(ReferenceField(User))

    @property
    def current_submission_period(self):
        for submission_period in self.submission_periods:
            if submission_period.is_current:
                return submission_period
        return None
