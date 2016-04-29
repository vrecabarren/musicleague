from feedback.errors import SessionExistsError

from feedback.models import Session


def create_session(name):
    if get_session(name):
        raise SessionExistsError('Session with name %s already exists' % name)
    new_session = Session(name=name)
    new_session.save()
    return new_session


def get_session(name):
    session = Session.objects.get(name=name)
    return session
