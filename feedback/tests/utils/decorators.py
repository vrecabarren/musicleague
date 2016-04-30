from functools import wraps

from feedback.environment import DEBUG_ENV_VAR
from feedback.environment import DEPLOYED_ENV_VAR

from feedback.tests.utils.environment import set_environment_state


def env_debug(func):
    return _get_env_wrapper(func, DEBUG_ENV_VAR, 'True')


def env_deployed(func):
    return _get_env_wrapper(func, DEPLOYED_ENV_VAR, 'True')


def env_local(func):
    return _get_env_wrapper(func, DEPLOYED_ENV_VAR, remove=True)


def _get_env_wrapper(func, key, value=None, remove=False):
    @wraps(func)
    def env_wrapper(*args, **kwargs):
        set_environment_state(key, value, remove)
        return func(*args, **kwargs)
    return env_wrapper
