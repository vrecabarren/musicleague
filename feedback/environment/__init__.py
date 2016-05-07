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
    if DEBUG.key not in os.environ:
        return DEBUG.default
    return os.environ[DEBUG.key].lower() == 'true'


def is_deployed():
    return bool(os.environ.get(DEPLOYED.key, DEPLOYED.default))


def get_port():
    return int(os.environ.get(PORT.key, PORT.default))


def get_secret_key():
    secret_key = SECRET_KEY.default

    if not is_deployed():
        return get_local_setting(SECRET_KEY.key, secret_key)

    return os.environ.get(SECRET_KEY.key, secret_key)


def get_facebook_config():
    consumer_key = FB_CONSUMER_KEY.default
    consumer_secret = FB_CONSUMER_SECRET.default

    if not is_deployed():
        consumer_key = get_local_setting(FB_CONSUMER_KEY.key, consumer_key)
        consumer_secret = get_local_setting(FB_CONSUMER_SECRET.key,
                                            consumer_secret)
    else:
        consumer_key = os.environ.get(FB_CONSUMER_KEY.key, consumer_key)
        consumer_secret = os.environ.get(FB_CONSUMER_SECRET.key,
                                         consumer_secret)

    return {'consumer_key': consumer_key, 'consumer_secret': consumer_secret}


def get_local_setting(name, default=None):
    if is_deployed():
        return default

    try:
        import settingslocal
        setting = getattr(settingslocal, name)
        return setting
    except AttributeError:
        logging.warning('Attempt to get local setting %s failed because we '
                        'could not find it in settingslocal.py', name)
    except ImportError:
        logging.warning('Attempt to get local setting %s failed because we '
                        'could not find settingslocal.py', name)
    return default


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
