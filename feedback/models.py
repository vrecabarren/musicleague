from datetime import datetime

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentListField
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import ReferenceField
from mongoengine import StringField


class User(Document):
    id = IntField(primary_key=True)
    name = StringField(max_length=255)
    email = StringField(max_length=255)
    joined = DateTimeField(default=datetime.now())


class Submission(EmbeddedDocument):
    count = IntField(default=1)
    created = DateTimeField(default=datetime.now, required=True)
    tracks = ListField(default=[], required=True)
    user = StringField(required=True)


class Season(Document):
    created = DateTimeField(default=datetime.now, required=True)
    owner = ReferenceField(User)
    users = ListField(ReferenceField(User))
    locked = BooleanField(default=False)
    name = StringField(primary_key=True, required=True)
    playlist_url = StringField()
    submissions = EmbeddedDocumentListField(Submission)

    def embed_url(self):
        if not self.submissions:
            return
        url = "https://embed.spotify.com/?uri=spotify:trackset:{title}:{guids}"
        guids = set()
        for submission in self.submissions:
            guids.update(submission.tracks)
            return url.format(title=self.name, guids=','.join(list(guids)))
