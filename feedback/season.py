from feedback.errors import SeasonExistsError

from feedback.models import Season


def create_season(name, user):
    if get_season(name):
        raise SeasonExistsError('Season with name %s already exists' % name)

    new_season = Season(name=name, owner=user)
    new_season.save()
    return new_season


def get_season(name):
    try:
        season = Season.objects.get(name=name)
        return season
    except Season.DoesNotExist:
        return None


def get_seasons_for_user(user):
    try:
        seasons = Season.objects(owner=user).all().order_by('-created')
        return seasons
    except Season.DoesNotExist:
        return []
