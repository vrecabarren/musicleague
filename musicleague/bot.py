from musicleague.environment import get_setting
from musicleague.environment.variables import SPOTIFY_BOT_USERNAME
from musicleague.errors import BotDoesNotExistError
from musicleague.errors import BotExistsError
from musicleague.models import Bot


def is_bot(user_id):
    return user_id == get_setting(SPOTIFY_BOT_USERNAME)


def create_bot(id, access_token, refresh_token, expires_at):
    if get_bot(id):
        raise BotExistsError('Bot with id %s already exists' % id)

    new_bot = Bot(id=id, access_token=access_token,
                  refresh_token=refresh_token, expires_at=expires_at)
    new_bot.save()
    return new_bot


def update_bot(id, access_token, refresh_token, expires_at):
    bot = get_bot(id)

    if not bot:
        raise BotDoesNotExistError('Bot with id %s does not exist' % id)

    bot.id = id if id else bot.id
    bot.access_token = access_token if access_token else bot.access_token
    bot.refresh_token = refresh_token if refresh_token else bot.refresh_token
    bot.expires_at = expires_at if expires_at else bot.expires_at
    bot.save()
    return bot


def create_or_update_bot(id, access_token, refresh_token, expires_at):
    bot = get_bot(id)

    if not bot:
        bot = create_bot(id, access_token, refresh_token, expires_at)
    else:
        bot = update_bot(id, access_token, refresh_token, expires_at)

    return bot


def get_bot(id):
    try:
        bot = Bot.objects.get(id=id)
        return bot
    except Bot.DoesNotExist:
        return None
