from collections import namedtuple


EnvironmentVariable = namedtuple('EnvironmentVariable', 'key, default')


DEBUG = EnvironmentVariable(key='DEBUG', default=False)
DEPLOYED = EnvironmentVariable(key='ON_HEROKU', default=False)
MAILGUN_API_BASE_URL = EnvironmentVariable(key='MAILGUN_API_BASE_URL', default='')  # noqa
MAILGUN_API_KEY = EnvironmentVariable(key='MAILGUN_API_KEY', default='')
MONGODB_URI = EnvironmentVariable(key='MONGODB_URI', default='127.0.0.1')
NOTIFICATION_SENDER = EnvironmentVariable(key="NOTIFICATION_SENDER", default='')  # noqa
PORT = EnvironmentVariable(key='PORT', default=5000)
PRODUCTION = EnvironmentVariable(key='IS_PRODUCTION', default=False)
REDISCLOUD_URL = EnvironmentVariable(key='REDISCLOUD_URL', default='redis://127.0.0.1')  # noqa
SECRET_KEY = EnvironmentVariable(key='SECRET_KEY', default='')
SERVER_NAME = EnvironmentVariable(key='SERVER_NAME', default='')
SPOTIFY_BOT_USERNAME = EnvironmentVariable(key='SPOTIFY_BOT_USERNAME', default='')  # noqa
SPOTIFY_CLIENT_ID = EnvironmentVariable(key='SPOTIFY_CLIENT_ID', default='')
SPOTIFY_CLIENT_SECRET = EnvironmentVariable(key='SPOTIFY_CLIENT_SECRET', default='')  # noqa
SPOTIFY_REDIRECT_URI = EnvironmentVariable(key='SPOTIFY_REDIRECT_URI', default='')  # noqa
