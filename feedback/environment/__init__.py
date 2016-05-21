import logging
import os
import re

from feedback.environment.variables import DEBUG
from feedback.environment.variables import DEPLOYED
from feedback.environment.variables import MONGODB_URI
from feedback.environment.variables import PORT
from feedback.environment.variables import SECRET_KEY


def get_setting(env_setting):
    if env_setting.key == DEPLOYED.key:
        return get_environment_setting(DEPLOYED)

    getter = get_environment_setting if is_deployed() else get_local_setting
    return getter(env_setting)


def get_environment_setting(env_setting):
    """Any value retrieved from the environment will be typecast to match
    env_setting.default
    """
    if env_setting.key == DEPLOYED.key:
        setting = os.environ.get(DEPLOYED.key, DEPLOYED.default)

    elif not is_deployed():
        setting = env_setting.default

    else:
        setting = os.environ.get(env_setting.key, env_setting.default)

    typecast = type(env_setting.default)
    return typecast(setting)


def get_local_setting(env_setting):
    """Any value retrieved from the environment will be typecast to match
    env_setting.default
    """
    try:
        import settingslocal
        setting = getattr(settingslocal, env_setting.key)
        typecast = type(env_setting.default)
        return typecast(setting)
    except AttributeError:
        logging.warning('Attempt to get local setting %s failed because we '
                        'could not find it in settingslocal.py. Default is %s',
                        env_setting.key, env_setting.default)
    except ImportError:
        logging.warning('Attempt to get local setting %s failed because we '
                        'could not find settingslocal.py. Default is %s',
                        env_setting.key, env_setting.default)
    return env_setting.default


def is_debug():
    if not is_deployed():
        return True
    if DEBUG.key not in os.environ:
        return DEBUG.default
    return os.environ.get(DEBUG.key).lower() == 'true'


def is_deployed():
    return get_setting(DEPLOYED)


def get_port():
    return get_setting(PORT)


def get_secret_key():
    return get_setting(SECRET_KEY)


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
