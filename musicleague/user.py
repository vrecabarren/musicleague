from datetime import datetime
from random import choice

from musicleague.errors import UserDoesNotExistError
from musicleague.errors import UserExistsError
from musicleague.models import User
from musicleague.models import UserPreferences
from musicleague.persistence.statements import INSERT_USER
from musicleague.persistence.statements import UPDATE_USER


DEFAULT_AVATARS = [
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/bowie_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/daft_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/elvis_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/prince_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/punk_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/supremes_avatar.svg'
]

PROFILE_BACKGROUNDS = [
    'ml_header01.jpg', 'ml_header02.jpg', 'ml_header03.jpg', 'ml_header04.jpg',
    'ml_header05.jpg', 'ml_header06.jpg', 'ml_header07.jpg', 'ml_header08.jpg',
    'ml_header09.jpg', 'ml_header10.jpg', 'ml_header11.jpg', 'ml_header12.jpg',
    'ml_header13.jpg', 'ml_header14.jpg', 'ml_header15.jpg', 'ml_header16.jpg',
    'ml_header17.jpg', 'ml_header18.jpg', 'ml_header19.jpg', 'ml_header20.jpg',
    'ml_header21.jpg', 'ml_header22.jpg', 'ml_header23.jpg', 'ml_header24.jpg'
]


def create_user_from_spotify_user(spotify_user):
    user_id = spotify_user.get('id')
    user_email = spotify_user.get('email')
    user_display_name = spotify_user.get('display_name')
    user_images = spotify_user.get('images')
    user_image_url = ''
    if user_images:
        user_image_url = user_images[0].get('url', user_image_url)

    return create_user(
        id=user_id, email=user_email, name=(user_display_name or user_id),
        image_url=user_image_url)


def update_user_from_spotify_user(user, spotify_user):
    user_images = spotify_user.get('images')
    user_image_url = ''
    if user_images:
        user.image_url = user_images[0].get('url', user_image_url)
        user.save()

    return user


def create_user(id, name, email, image_url):
    if get_user(id):
        raise UserExistsError('User with id %s already exists' % id)

    if not image_url:
        image_url = choice(DEFAULT_AVATARS)

    profile_background = choice(PROFILE_BACKGROUNDS)

    new_user = User(
        id=id, name=name, email=email, joined=datetime.utcnow(),
        image_url=image_url, profile_background=profile_background,
        preferences=UserPreferences())
    new_user.save()

    from musicleague.persistence.insert import insert_user
    insert_user(new_user)

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

    try:
        from musicleague import postgres_conn

        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(INSERT_USER, (id, email, name))
                cur.execute(UPDATE_USER, (email, name, id))
    except:
        pass

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
        updated = False

        if not user.image_url:
            user.image_url = choice(DEFAULT_AVATARS)
            updated = True

        if not user.profile_background:
            user.profile_background = choice(PROFILE_BACKGROUNDS)
            updated = True

        if updated:
            user.save()

        return user

    except User.DoesNotExist:
        return None


def get_user_by_email(email):
    try:
        user = User.objects(email=email).get()
        return user
    except User.DoesNotExist:
        return None
