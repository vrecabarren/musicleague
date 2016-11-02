from functools import wraps

from musicleague.environment.variables import DEBUG
from musicleague.environment.variables import DEPLOYED

from musicleague.tests.utils.environment import set_environment_state


def env_debug(func):
    return _get_env_wrapper(func, DEBUG.key, 'True')


def env_deployed(func):
    return _get_env_wrapper(func, DEPLOYED.key, 'True')


def env_local(func):
    return _get_env_wrapper(func, DEPLOYED.key, remove=True)


def _get_env_wrapper(func, key, value=None, remove=False):
    @wraps(func)
    def env_wrapper(*args, **kwargs):
        set_environment_state(key, value, remove)
        return func(*args, **kwargs)
    return env_wrapper
