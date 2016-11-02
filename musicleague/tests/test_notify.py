from unittest import TestCase

from mock import patch

from musicleague.environment.variables import MAILGUN_API_BASE_URL
from musicleague.environment.variables import MAILGUN_API_KEY
from musicleague.environment.variables import NOTIFICATION_SENDER
from musicleague.notify import HTML_PATH
from musicleague.notify import TXT_PATH
from musicleague.notify import _html_email
from musicleague.notify import _send_email
from musicleague.notify import _txt_email
from musicleague.tests.utils.decorators import env_deployed
from musicleague.tests.utils.decorators import env_local
from musicleague.tests.utils.environment import set_environment_state


PATH = 'musicleague.notify.%s'


class SendEmailTestCase(TestCase):

    def setUp(self):
        self.to = 'test@test.com'
        self.subject = 'Test Subject'
        self.text = 'Text'
        self.html = 'HTML'

    @env_local
    @patch(PATH % 'requests.post')
    def test_send_email_not_deployed(self, post_request):
        _send_email(self.to, self.subject, self.text, self.html)

        self.assertFalse(post_request.called)

    @env_deployed
    @patch(PATH % 'requests.post')
    def test_send_email(self, post_request):
        api_key = 'api_key'
        base_url = 'http://base-url.com'
        sender = 'sender@test.com'
        set_environment_state(MAILGUN_API_KEY.key, api_key)
        set_environment_state(MAILGUN_API_BASE_URL.key, base_url)
        set_environment_state(NOTIFICATION_SENDER.key, sender)

        _send_email(self.to, self.subject, self.text, self.html)

        post_request.assert_called_once_with(
            base_url + '/messages', auth=("api", api_key),
            data={"from": sender, "to": self.to, "subject": self.subject,
                  "text": self.text, "html": self.html})


class HtmlTxtEmailTestCase(TestCase):

    def setUp(self):
        self.html_template = "submitted.html"
        self.txt_template = "submitted.txt"

    @patch(PATH % 'render_template')
    def test_html_email(self, render_template):
        _html_email(self.html_template, submission=None)

        render_template.assert_called_once_with(
            HTML_PATH % self.html_template, submission=None)

    @patch(PATH % 'render_template')
    def test_txt_email(self, render_template):
        _txt_email(self.txt_template, submission=None)

        render_template.assert_called_once_with(
            TXT_PATH % self.txt_template, submission=None)
