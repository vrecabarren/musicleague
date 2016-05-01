from unittest import TestCase

from feedback.environment import DEBUG_ENV_VAR
from feedback.environment import get_port
from feedback.environment import is_debug
from feedback.environment import is_deployed
from feedback.environment import MONGODB_URI_ENV_VAR
from feedback.environment import parse_mongolab_uri
from feedback.environment import PORT_ENV_VAR
from feedback.environment import PORT_ENV_VAR_DEFAULT

from feedback.tests.utils import decorators as dec
from feedback.tests.utils.environment import set_environment_state


class GetPortTestCase(TestCase):

    def test_env_var(self):
        set_environment_state(PORT_ENV_VAR, '1111')
        self.assertEqual(1111, get_port())

    def test_no_env_var(self):
        set_environment_state(PORT_ENV_VAR, remove=True)
        self.assertEqual(PORT_ENV_VAR_DEFAULT, get_port())


class IsDebugTestCase(TestCase):

    @dec.env_local
    def test_not_deployed(self):
        self.assertTrue(is_debug())

    @dec.env_deployed
    def test_deployed_no_env_var(self):
        set_environment_state(DEBUG_ENV_VAR, remove=True)
        self.assertFalse(is_debug())

    @dec.env_deployed
    def test_deployed_false_env_var(self):
        set_environment_state(DEBUG_ENV_VAR, 'False')
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

    @dec.env_deployed
    def test_happy_path(self):
        set_environment_state(MONGODB_URI_ENV_VAR, self.uri)

        self.assertEqual(
            (self.host, int(self.port), self.username, self.password, self.db),
            parse_mongolab_uri())
