class SessionExistsError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class SocialLoginError(Exception):
    def __init__(self, provider):
        self.provider = provider
