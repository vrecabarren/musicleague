from feedback.errors import UserExistsError
from feedback.models import User


def create_user(id, name, email):
    if get_user(id):
        raise UserExistsError('User with id %s already exists' % name)

    new_user = User(id=id, name=name, email=email)
    new_user.save()
    return new_user


def get_user(id):
    try:
        user = User.objects.get(id=id)
        return user
    except User.DoesNotExist:
        return None
