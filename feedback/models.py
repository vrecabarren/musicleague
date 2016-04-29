from datetime import datetime

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import EmbeddedDocument
from mongoengine import EmbeddedDocumentListField
from mongoengine import IntField
from mongoengine import ListField
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
