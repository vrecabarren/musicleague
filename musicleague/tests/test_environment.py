from unittest import TestCase
from uuid import uuid4

from musicleague.environment import get_port
from musicleague.environment import get_secret_key
from musicleague.environment import is_debug
from musicleague.environment import is_deployed

from musicleague.environment.variables import DEBUG
from musicleague.environment.variables import PORT
from musicleague.environment.variables import SECRET_KEY

from musicleague.tests.utils import decorators as dec
from musicleague.tests.utils.environment import set_environment_state


class GetPortTestCase(TestCase):

    @dec.env_deployed
    def test_env_var(self):
        set_environment_state(PORT.key, '1111')
        self.assertEqual(1111, get_port())

    def test_no_env_var(self):
        set_environment_state(PORT.key, remove=True)
        self.assertEqual(PORT.default, get_port())


class GetSecretKeyTestCase(TestCase):

    def setUp(self):
        self.secret_key = uuid4().hex

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
