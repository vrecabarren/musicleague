from collections import namedtuple


EnvironmentVariable = namedtuple('EnvironmentVariable', 'key, default')


DEBUG = EnvironmentVariable(key='DEBUG', default=False)
DEPLOYED = EnvironmentVariable(key='ON_HEROKU', default=False)
FB_CONSUMER_KEY = EnvironmentVariable(key='FB_CONSUMER_KEY', default='')
FB_CONSUMER_SECRET = EnvironmentVariable(key='FB_CONSUMER_SECRET', default='')
MONGODB_URI = EnvironmentVariable(key='MONGODB_URI', default='')
PORT = EnvironmentVariable(key='PORT', default=5000)
SECRET_KEY = EnvironmentVariable(key='SECRET_KEY', default='')
SPOTIFY_CLIENT_ID = EnvironmentVariable(key='SPOTIFY_CLIENT_ID', default='')
SPOTIFY_CLIENT_SECRET = EnvironmentVariable(key='SPOTIFY_CLIENT_SECRET', default='')  # noqa
SPOTIFY_REDIRECT_URI = EnvironmentVariable(key='SPOTIFY_REDIRECT_URI', default='')  # noqa
