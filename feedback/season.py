from feedback.errors import SeasonExistsError

from feedback.models import Season


def create_season(name):
    if get_season(name):
        raise SeasonExistsError('Season with name %s already exists' % name)

    new_season = Season(name=name)
    new_season.save()
    return new_season


def get_season(name):
    try:
        season = Season.objects.get(name=name)
        return season
    except Season.DoesNotExist:
        return None
