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


class Season(Document):
    created = DateTimeField(default=datetime.now, required=True)
    owner = ReferenceField(User)
    users = ListField(ReferenceField(User))
    locked = BooleanField(default=False)
    name = StringField(primary_key=True, required=True)

    @property
    def current_submission_period(self):
        try:
            return SubmissionPeriod.objects(is_latest=True, season=self).get()
        except SubmissionPeriod.DoesNotExist:
            latest = SubmissionPeriod(is_latest=True, season=self)
            latest.save()
            return latest


class SubmissionPeriod(Document):
    complete = BooleanField(default=False)
    is_latest = BooleanField(default=True)
    playlist_created = BooleanField(default=False)
    playlist_url = StringField()
    season = ReferenceField(Season)
    submissions = ListField(ReferenceField(Submission))
