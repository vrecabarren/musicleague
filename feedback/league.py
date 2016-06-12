from datetime import datetime

from feedback.errors import LeagueExistsError
from feedback.models import League
from feedback.notify import user_added_to_league_notification
from feedback.notify import user_removed_from_league_notification
from feedback.user import get_user_by_email


def add_user(league, user_email):
    user = get_user_by_email(user_email)
    if user and user not in league.users:
        league.users.append(user)
        league.save()
        user_added_to_league_notification(user, league)


def remove_user(league, user_id):
    remaining_users = []
    removed_user = None
    for user in league.users:
        if str(user.id) == user_id:
            removed_user = user
        else:
            remaining_users.append(user)
    league.save()

    if removed_user:
        user_removed_from_league_notification(removed_user, league)


def create_league(name, user):
    if get_league(name):
        raise LeagueExistsError('League with name %s already exists' % name)

    new_league = League(
        name=name, owner=user, users=[user], created=datetime.utcnow())
    new_league.save()
    return new_league


def get_league(name):
    try:
        league = League.objects.get(name=name)
        return league
    except League.DoesNotExist:
        return None


def get_leagues_for_owner(user):
    try:
        leagues = League.objects(owner=user).all().order_by('-created')
        return leagues
    except League.DoesNotExist:
        return []


def get_leagues_for_user(user):
    try:
        leagues = League.objects(users=user).all().order_by('-created')
        return leagues
    except League.DoesNotExist:
        return []
