import os
import re


DEBUG_ENV_VAR = 'DEBUG'
DEBUG_ENV_VAR_DEFAULT = False
DEPLOYED_ENV_VAR = 'ON_HEROKU'
DEPLOYED_ENV_VAR_DEFAULT = False
MONGODB_URI_ENV_VAR = 'MONGODB_URI'
PORT_ENV_VAR = 'PORT'
PORT_ENV_VAR_DEFAULT = 33507


def is_debug():
    if not is_deployed():
        return True
    if DEBUG_ENV_VAR not in os.environ:
        return DEBUG_ENV_VAR_DEFAULT
    return os.environ[DEBUG_ENV_VAR].lower() == 'true'


def is_deployed():
    return bool(os.environ.get(DEPLOYED_ENV_VAR, DEPLOYED_ENV_VAR_DEFAULT))


def get_port():
    return int(os.environ.get(PORT_ENV_VAR, PORT_ENV_VAR_DEFAULT))


def parse_mongolab_uri():
    if not is_deployed():
        return

    r = (r'^mongodb\:\/\/(?P<username>[_\w]+):(?P<password>[\w]+)@(?P<host>'
         r'[\.\w]+):(?P<port>\d+)/(?P<database>[_\w]+)$')
    regex = re.compile(r)
    mongolab_url = os.environ.get(MONGODB_URI_ENV_VAR)
    match = regex.search(mongolab_url)
    data = match.groupdict()

    return (data['host'], int(data['port']), data['username'],
            data['password'], data['database'])
