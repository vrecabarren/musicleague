import logging
import os
import re

from feedback.environment.variables import DEBUG
from feedback.environment.variables import DEPLOYED
from feedback.environment.variables import FB_CONSUMER_KEY
from feedback.environment.variables import FB_CONSUMER_SECRET
from feedback.environment.variables import MONGODB_URI
from feedback.environment.variables import PORT
from feedback.environment.variables import SECRET_KEY


def is_debug():
    if not is_deployed():
        return True
    setting = get_environment_setting(DEBUG)
    return (setting.lower() == 'true' if isinstance(setting, basestring)
            else DEBUG.default)


def is_deployed():
    return get_environment_setting(DEPLOYED, typecast=bool)


def get_port():
    return get_environment_setting(PORT, typecast=int)


def get_secret_key():
    return get_environment_setting(SECRET_KEY)


def get_facebook_config():
    if not is_deployed():
        consumer_key = get_local_setting(FB_CONSUMER_KEY)
        consumer_secret = get_local_setting(FB_CONSUMER_SECRET)
    else:
        consumer_key = get_environment_setting(FB_CONSUMER_KEY)
        consumer_secret = get_environment_setting(FB_CONSUMER_SECRET)

    return {'consumer_key': consumer_key, 'consumer_secret': consumer_secret}


def get_environment_setting(env_setting, typecast=str):
    if env_setting.key == DEPLOYED.key:
        setting = os.environ.get(DEPLOYED.key, DEPLOYED.default)

    elif not is_deployed():
        setting = get_local_setting(env_setting)

    else:
        setting = os.environ.get(env_setting.key, env_setting.default)

    return typecast(setting)


def get_local_setting(env_setting, typecast=str):
    if is_deployed():
        return env_setting.default

    try:
        import settingslocal
        setting = getattr(settingslocal, env_setting.key)
        return typecast(setting)
    except AttributeError:
        logging.warning('Attempt to get local setting %s failed because we '
                        'could not find it in settingslocal.py',
                        env_setting.key)
    except ImportError:
        logging.warning('Attempt to get local setting %s failed because we '
                        'could not find settingslocal.py', env_setting.key)
    return env_setting.default


def parse_mongolab_uri():
    if not is_deployed():
        return

    r = (r'^mongodb\:\/\/(?P<username>[_\w]+):(?P<password>[\w]+)@(?P<host>'
         r'[\.\w]+):(?P<port>\d+)/(?P<database>[_\w]+)$')
    regex = re.compile(r)
    mongolab_url = os.environ.get(MONGODB_URI.key)
    match = regex.search(mongolab_url)
    data = match.groupdict()

    return (data['host'], int(data['port']), data['username'],
            data['password'], data['database'])
