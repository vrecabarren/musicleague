from feedback.errors import UserExistsError
from feedback.models import User


def create_user(id, name, email):
    if get_user(id):
        raise UserExistsError('User with id %s already exists' % name)

    new_user = User(id=id, name=name, email=email)
    new_user.save()
    return new_user


def create_or_update_user(id, name, email):
    user = get_user(id)

    if not user:
        user = create_user(id, name, email)
    else:
        user.id = id
        user.name = name
        user.email = email

    user.save()
    return user


def get_user(id):
    try:
        user = User.objects.get(id=id)
        return user
    except User.DoesNotExist:
        return None
