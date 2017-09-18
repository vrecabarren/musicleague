import os
import re

from musicleague.environment.variables import DEBUG
from musicleague.environment.variables import DEPLOYED
from musicleague.environment.variables import MONGODB_URI
from musicleague.environment.variables import PORT
from musicleague.environment.variables import PRODUCTION
from musicleague.environment.variables import REDISCLOUD_URL
from musicleague.environment.variables import SECRET_KEY
from musicleague.environment.variables import SERVER_NAME


def get_setting(env_setting):
    if env_setting.key == DEPLOYED.key:
        return get_environment_setting(DEPLOYED)

    return get_environment_setting(env_setting)


def get_environment_setting(env_setting):
    """Any value retrieved from the environment will be typecast to match
    env_setting.default
    """
    setting = os.environ.get(env_setting.key, env_setting.default)
    return _cast_value(env_setting, setting)


def _cast_value(env_setting, value):
    if isinstance(env_setting.default, bool) and isinstance(value, basestring):
        return value.lower() == 'true'

    desired_type = type(env_setting.default)
    return desired_type(value)


def is_debug():
    if not is_deployed():
        return True
    if DEBUG.key not in os.environ:
        return DEBUG.default
    return os.environ.get(DEBUG.key).lower() == 'true'


def is_deployed():
    return get_setting(DEPLOYED)


def is_production():
    return is_deployed() and get_setting(PRODUCTION)


def get_port():
    return get_setting(PORT)


def get_redis_url():
    return get_setting(REDISCLOUD_URL)


def get_secret_key():
    return get_setting(SECRET_KEY)


def get_server_name():
    return get_setting(SERVER_NAME)


def parse_mongolab_uri():
    if not is_deployed():
        return

    r = (r'^mongodb\:\/\/(?P<username>[_\w]+):(?P<password>[\w]+)@(?P<host>'
         r'[\.\w]+):(?P<port>\d+)/(?P<database>[_\w]+)$')
    regex = re.compile(r)
    mongolab_url = os.environ.get(MONGODB_URI.key)
    match = regex.search(mongolab_url)
    if not match:
        return

    data = match.groupdict()
    return (data['host'], int(data['port']), data['username'],
            data['password'], data['database'])
