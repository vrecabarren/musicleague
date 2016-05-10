from datetime import datetime

from flask.ext.security import RoleMixin
from flask.ext.security import UserMixin

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentListField
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import ReferenceField
from mongoengine import StringField


class Submission(EmbeddedDocument):
    count = IntField(default=1)
    created = DateTimeField(default=datetime.now, required=True)
    tracks = ListField(default=[], required=True)
    user = StringField(required=True)


class Session(Document):
    created = DateTimeField(default=datetime.now, required=True)
    locked = BooleanField(default=False)
    name = StringField(primary_key=True, required=True)
    submissions = EmbeddedDocumentListField(Submission)

    def embed_url(self):
        if not self.submissions:
            return
        url = "https://embed.spotify.com/?uri=spotify:trackset:{title}:{guids}"
        guids = set()
        for submission in self.submissions:
            guids.update(submission.tracks)
            return url.format(title=self.name, guids=','.join(list(guids)))


class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)


class User(Document, UserMixin):
    name = StringField(max_length=255)
    email = StringField(max_length=255)
    active = BooleanField(default=True)
    confirmed_at = DateTimeField()
    roles = ListField(ReferenceField(Role), default=[])

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Connection(Document):
    id = IntField(primary_key=True)
    user_id = ReferenceField(User)
    provider_id = StringField()
    provider_user_id = StringField()
    access_token = StringField()
    secret = StringField()
    display_name = StringField()
    profile_url = StringField()
    image_url = StringField()
