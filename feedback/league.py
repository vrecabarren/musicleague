from feedback.errors import LeagueExistsError

from feedback.models import League


def create_league(name, user):
    if get_league(name):
        raise LeagueExistsError('League with name %s already exists' % name)

    new_league = League(name=name, owner=user, users=[user])
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
