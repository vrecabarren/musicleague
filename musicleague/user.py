from datetime import datetime
from random import choice

from musicleague.errors import UserDoesNotExistError
from musicleague.errors import UserExistsError
from musicleague.persistence.models import User
from musicleague.persistence.select import select_user
from musicleague.persistence.select import select_user_by_email
from musicleague.persistence.update import upsert_user


DEFAULT_AVATARS = [
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/bowie_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/daft_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/dmc_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/elvis_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/hendrix_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/madonna_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/marley_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/morrison_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/prince_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/punk_avatar.svg',
    'https://s3.amazonaws.com/musicleague-static-assets/avatars/siouxie_avatar.svg',
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
    if user_display_name is None:
        user_display_name = user_id

    user_images = spotify_user.get('images')
    user_image_url = ''
    if user_images:
        user_image_url = user_images[0].get('url', user_image_url)

    return create_user(
        id=user_id, email=user_email, name=user_display_name, image_url=user_image_url)


def update_user_from_spotify_user(user, spotify_user):
    user_images = spotify_user.get('images')
    user_image_url = ''
    if user_images:
        user.image_url = user_images[0].get('url', user_image_url)
        upsert_user(user)

    return user


def create_user(id, name, email, image_url):
    if get_user(id):
        raise UserExistsError('User with id %s already exists' % id)

    if not image_url:
        image_url = choice(DEFAULT_AVATARS)

    profile_background = choice(PROFILE_BACKGROUNDS)

    new_user = User(
        id=id, email=email, image_url=image_url, is_admin=False,
        joined=datetime.utcnow(), name=name, profile_bg=profile_background)

    upsert_user(new_user)

    return new_user


def update_user(id, name, email, image_url):
    user = get_user(id)

    if not user:
        raise UserDoesNotExistError('User with id %s does not exist' % id)

    user.id = id if id else user.id
    user.name = name if name else user.name
    user.email = email if email else user.email
    user.image_url = image_url if image_url else user.image_url

    upsert_user(user)

    return user


def create_or_update_user(id, name, email, image_url):
    user = get_user(id)

    if not user:
        user = create_user(id, name, email, image_url)
    else:
        user = update_user(id, name, email, image_url)

    return user


def get_user(id):
    user = select_user(id)
    if user is None:
        return None

    updated = False

    if not user.image_url:
        user.image_url = choice(DEFAULT_AVATARS)
        updated = True

    if not user.profile_background:
        user.profile_background = choice(PROFILE_BACKGROUNDS)
        updated = True

    if updated:
        upsert_user(user)

    return user


def get_user_by_email(email):
    # TODO No need for this function
    return select_user_by_email(email)
