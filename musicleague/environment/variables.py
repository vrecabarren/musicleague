from collections import namedtuple


EnvironmentVariable = namedtuple('EnvironmentVariable', 'key, default')


ADD_BOT_REDIRECT_URI = EnvironmentVariable(key='ADD_BOT_REDIRECT_URI', default='')  # noqa
DATABASE_URL = EnvironmentVariable(key='DATABASE_URL', default='')
DEBUG = EnvironmentVariable(key='DEBUG', default=False)
DEPLOYED = EnvironmentVariable(key='ON_HEROKU', default=False)
EVENTSTORE_HOST = EnvironmentVariable(key='EVENTSTORE_HOST', default='')
LOGENTRIES_TOKEN = EnvironmentVariable(key='LOGENTRIES_TOKEN', default='')
MAILGUN_API_BASE_URL = EnvironmentVariable(key='MAILGUN_API_BASE_URL', default='')  # noqa
MAILGUN_API_KEY = EnvironmentVariable(key='MAILGUN_API_KEY', default='')
MESSENGER_PAGE_ACCESS_TOKEN = EnvironmentVariable(key='MESSENGER_PAGE_ACCESS_TOKEN', default='')  # noqa
MESSENGER_VERIFY_TOKEN = EnvironmentVariable(key='MESSENGER_VERIFY_TOKEN', default='')  # noqa
MIXPANEL_TOKEN = EnvironmentVariable(key='MIXPANEL_TOKEN', default='')
NOTIFICATION_SENDER = EnvironmentVariable(key="NOTIFICATION_SENDER", default='')  # noqa
PORT = EnvironmentVariable(key='PORT', default=5000)
PRODUCTION = EnvironmentVariable(key='IS_PRODUCTION', default=False)
REDISCLOUD_URL = EnvironmentVariable(key='REDISCLOUD_URL', default='redis://127.0.0.1')  # noqa
SECRET_KEY = EnvironmentVariable(key='SECRET_KEY', default='')
SERVER_NAME = EnvironmentVariable(key='SERVER_NAME', default='localhost:5000')
SPOTIFY_BOT_USERNAME = EnvironmentVariable(key='SPOTIFY_BOT_USERNAME', default='')  # noqa
SPOTIFY_CLIENT_ID = EnvironmentVariable(key='SPOTIFY_CLIENT_ID', default='')
SPOTIFY_CLIENT_SECRET = EnvironmentVariable(key='SPOTIFY_CLIENT_SECRET', default='')  # noqa
SPOTIFY_REDIRECT_URI = EnvironmentVariable(key='SPOTIFY_REDIRECT_URI', default='')  # noqa
