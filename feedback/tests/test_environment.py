from os import environ
from unittest import TestCase

from feedback.environment import DEPLOYED_ENV_VAR
from feedback.environment import get_port
from feedback.environment import is_deployed
from feedback.environment import MONGOLAB_URI_ENV_VAR
from feedback.environment import parse_mongolab_uri
from feedback.environment import PORT_ENV_VAR
from feedback.environment import PORT_ENV_VAR_DEFAULT


class GetPortTestCase(TestCase):

    def test_get_port_set(self):
        environ[PORT_ENV_VAR] = '1111'
        self.assertEqual(1111, get_port())

    def test_get_port_not_set(self):
        if PORT_ENV_VAR in environ:
            del environ[PORT_ENV_VAR]
        self.assertEqual(PORT_ENV_VAR_DEFAULT, get_port())


class IsDeployedTestCase(TestCase):

    def test_deployed(self):
        environ[DEPLOYED_ENV_VAR] = 'True'
        self.assertTrue(is_deployed())

    def test_not_deployed(self):
        if DEPLOYED_ENV_VAR in environ:
            del environ[DEPLOYED_ENV_VAR]
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
        environ[DEPLOYED_ENV_VAR] = 'True'
        environ[MONGOLAB_URI_ENV_VAR] = self.uri

        self.assertEqual(
            (self.host, int(self.port), self.username, self.password, self.db),
            parse_mongolab_uri())
