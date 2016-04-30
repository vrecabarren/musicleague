from os import environ
from unittest import TestCase

from feedback.environment import DEBUG_ENV_VAR
from feedback.environment import DEPLOYED_ENV_VAR
from feedback.environment import get_port
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import MONGODB_URI_ENV_VAR
from feedback.environment import parse_mongolab_uri
from feedback.environment import PORT_ENV_VAR
from feedback.environment import PORT_ENV_VAR_DEFAULT


class GetPortTestCase(TestCase):

    def test_env_var(self):
        _set_environment_state(PORT_ENV_VAR, '1111')
        self.assertEqual(1111, get_port())

    def test_no_env_var(self):
        _set_environment_state(PORT_ENV_VAR, remove=True)
        self.assertEqual(PORT_ENV_VAR_DEFAULT, get_port())


class IsDebugTestCase(TestCase):

    def test_not_deployed(self):
        _set_environment_state(DEPLOYED_ENV_VAR, remove=True)
        self.assertTrue(is_debug())

    def test_deployed_no_env_var(self):
        _set_environment_state(DEPLOYED_ENV_VAR, 'True')
        _set_environment_state(DEBUG_ENV_VAR, remove=True)
        self.assertFalse(is_debug())

    def test_deployed_env_var(self):
        _set_environment_state(DEPLOYED_ENV_VAR, 'True')
        _set_environment_state(DEBUG_ENV_VAR, 'True')
        self.assertTrue(is_debug())


class IsDeployedTestCase(TestCase):

    def test_deployed(self):
        _set_environment_state(DEPLOYED_ENV_VAR, 'True')
        self.assertTrue(is_deployed())

    def test_not_deployed(self):
        _set_environment_state(DEPLOYED_ENV_VAR, remove=True)
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

    def test_happy_path(self):
        _set_environment_state(DEPLOYED_ENV_VAR, 'True')
        _set_environment_state(MONGODB_URI_ENV_VAR, self.uri)

        self.assertEqual(
            (self.host, int(self.port), self.username, self.password, self.db),
            parse_mongolab_uri())


# TODO Add decorators for various environment states - @env_local, @env_debug
def _set_environment_state(key, value=None, remove=False):
    if not remove:
        environ[key] = value
        return

    if key in environ:
        del environ[key]
