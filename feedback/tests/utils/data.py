from mongoengine import Document

from feedback.models import ALL_MODELS


def clean_data():
    for model in ALL_MODELS:
        if issubclass(model, Document):
            model.objects.delete()
