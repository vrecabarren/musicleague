from datetime import datetime

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import ReferenceField
from mongoengine import StringField


class User(Document):
    id = IntField(primary_key=True)
    name = StringField(max_length=255)
    email = StringField(max_length=255)
    joined = DateTimeField(default=datetime.now())


class Submission(Document):
    confirmed = BooleanField(default=False)
    count = IntField(default=1)
    created = DateTimeField(default=datetime.now, required=True)
    tracks = ListField(default=[])
    user = ReferenceField(User)


class SubmissionPeriod(Document):
    complete = BooleanField(default=False)
    is_current = BooleanField(default=True)
    name = StringField(max_length=255)
    playlist_url = StringField(default='')
    submissions = ListField(ReferenceField(Submission))

    @property
    def playlist_created(self):
        return self.playlist_url != ''


class Season(Document):
    created = DateTimeField(default=datetime.now, required=True)
    locked = BooleanField(default=False)
    name = StringField(primary_key=True, required=True)
    owner = ReferenceField(User)
    submission_periods = ListField(ReferenceField(SubmissionPeriod))
    users = ListField(ReferenceField(User))

    @property
    def current_submission_period(self):
        for submission_period in self.submission_periods:
            if submission_period.is_current:
                return submission_period
        return None
