from datetime import datetime

from musicleague.errors import UserDoesNotExistError
from musicleague.errors import UserExistsError
from musicleague.models import User
from musicleague.models import UserPreferences


def create_user(id, name, email, image_url):
    if get_user(id):
        raise UserExistsError('User with id %s already exists' % id)

    new_user = User(
        id=id, name=name, email=email, joined=datetime.utcnow(),
        image_url=image_url, preferences=UserPreferences())
    new_user.save()
    return new_user


def update_user(id, name, email, image_url):
    user = get_user(id)

    if not user:
        raise UserDoesNotExistError('User with id %s does not exist' % id)

    user.id = id if id else user.id
    user.name = name if name else user.name
    user.email = email if email else user.email
    user.image_url = image_url if image_url else user.image_url
    user.save()
    return user


def create_or_update_user(id, name, email, image_url):
    user = get_user(id)

    if not user:
        user = create_user(id, name, email, image_url)
    else:
        user = update_user(id, name, email, image_url)

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
