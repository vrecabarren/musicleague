from datetime import datetime

from feedback.errors import UserExistsError
from feedback.models import User
from feedback.models import UserPreferences


def create_user(id, name, email, image_url):
    if get_user(id):
        raise UserExistsError('User with id %s already exists' % name)

    new_user = User(
        id=id, name=name, email=email, joined=datetime.utcnow(),
        image_url=image_url, preferences=UserPreferences())
    new_user.save()
    return new_user


def create_or_update_user(id, name, email, image_url):
    user = get_user(id)

    if not user:
        user = create_user(id, name, email, image_url)
    else:
        user.id = id if id else user.id
        user.name = name if name else user.name
        user.email = email if email else user.email
        user.image_url = image_url if image_url else user.image_url

    user.save()
    return user


def get_user(id):
    try:
        user = User.objects.get(id=id)
        return user
    except User.DoesNotExist:
        return None


def get_user_by_email(email):
    try:
        user = User.objects(email=email).get()
        return user
    except User.DoesNotExist:
        return None
