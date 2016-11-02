from os import environ


def set_environment_state(key, value=None, remove=False):
    if not remove:
        environ[key] = value
        return

    if key in environ:
        del environ[key]
