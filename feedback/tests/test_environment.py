from unittest import TestCase
from uuid import uuid4

from feedback.environment import get_facebook_config
from feedback.environment import get_local_setting
from feedback.environment import get_port
from feedback.environment import get_secret_key
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import parse_mongolab_uri

from feedback.environment.variables import DEBUG
from feedback.environment.variables import FB_CONSUMER_KEY
from feedback.environment.variables import FB_CONSUMER_SECRET
from feedback.environment.variables import MONGODB_URI
from feedback.environment.variables import PORT
from feedback.environment.variables import SECRET_KEY

from feedback.tests.utils import decorators as dec
from feedback.tests.utils.environment import set_environment_state


class GetFacebookConfigTestCase(TestCase):

    def setUp(self):
        self.consumer_key = uuid4().hex
        self.consumer_secret = uuid4().hex

    @dec.env_local
    def test_env_local(self):
        config = get_facebook_config()
        local_key = get_local_setting(FB_CONSUMER_KEY)
        local_secret = get_local_setting(FB_CONSUMER_SECRET)

        self.assertEqual(local_key, config.get('consumer_key'))
        self.assertEqual(local_secret, config.get('consumer_secret'))

    @dec.env_deployed
    def test_no_env_var(self):
        set_environment_state(FB_CONSUMER_KEY.key, remove=True)
        set_environment_state(FB_CONSUMER_SECRET.key, remove=True)

        config = get_facebook_config()

        self.assertEqual(
            FB_CONSUMER_KEY.default, config.get('consumer_key'))
        self.assertEqual(
            FB_CONSUMER_SECRET.default, config.get('consumer_secret'))

    @dec.env_deployed
    def test_env_var(self):
        set_environment_state(FB_CONSUMER_KEY.key, self.consumer_key)
        set_environment_state(FB_CONSUMER_SECRET.key, self.consumer_secret)

        config = get_facebook_config()

        self.assertEqual(self.consumer_key, config.get('consumer_key'))
        self.assertEqual(self.consumer_secret, config.get('consumer_secret'))


class GetPortTestCase(TestCase):

    def test_env_var(self):
        set_environment_state(PORT.key, '1111')
        self.assertEqual(1111, get_port())

    def test_no_env_var(self):
        set_environment_state(PORT.key, remove=True)
        self.assertEqual(PORT.default, get_port())


class GetSecretKeyTestCase(TestCase):

    def setUp(self):
        self.secret_key = uuid4().hex

    @dec.env_local
    def test_env_local(self):
        set_environment_state(SECRET_KEY.key, remove=True)
        local_setting = get_local_setting(SECRET_KEY)
        self.assertEqual(local_setting, get_secret_key())

    @dec.env_deployed
    def test_no_env_var(self):
        set_environment_state(SECRET_KEY.key, remove=True)
        self.assertEqual(SECRET_KEY.default, get_secret_key())

    @dec.env_deployed
    def test_env_var(self):
        set_environment_state(SECRET_KEY.key, self.secret_key)
        self.assertEqual(self.secret_key, get_secret_key())


class IsDebugTestCase(TestCase):

    @dec.env_local
    def test_not_deployed(self):
        self.assertTrue(is_debug())

    @dec.env_deployed
    def test_deployed_no_env_var(self):
        set_environment_state(DEBUG.key, remove=True)
        self.assertFalse(is_debug())

    @dec.env_deployed
    def test_deployed_false_env_var(self):
        set_environment_state(DEBUG.key, 'False')
        self.assertFalse(is_debug())

    @dec.env_deployed
    @dec.env_debug
    def test_deployed_env_var(self):
        self.assertTrue(is_debug())


class IsDeployedTestCase(TestCase):

    @dec.env_deployed
    def test_deployed(self):
        self.assertTrue(is_deployed())

    @dec.env_local
    def test_not_deployed(self):
        self.assertFalse(is_deployed())


class ParseMongoLabURITestCase(TestCase):
    def setUp(self):
        self.host = 'db_host'
        self.port = '1111'
        self.username = 'db_username'
        self.password = 'db_password'
        self.db = 'db_name'
        self.uri = 'mongodb://{username}:{password}@{host}:{port}/{db}'
        self.uri = self.uri.format(
            username=self.username, password=self.password, host=self.host,
            port=self.port, db=self.db)

    @dec.env_local
    def test_env_local(self):
        set_environment_state(MONGODB_URI.key, self.uri)
        self.assertIsNone(parse_mongolab_uri())

    @dec.env_deployed
    def test_happy_path(self):
        set_environment_state(MONGODB_URI.key, self.uri)

        self.assertEqual(
            (self.host, int(self.port), self.username, self.password, self.db),
            parse_mongolab_uri())
