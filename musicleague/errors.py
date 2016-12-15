class BotExistsError(Exception):
    """ Error to indicate that Bot being created with id already exists. """


class LeagueExistsError(Exception):
    """ Error to indicate that League being created with id already exists. """


class UserDoesNotExistError(Exception):
    """ Error to indicate that User being fetched with id does not exist. """


class UserExistsError(Exception):
    """ Error to indicate that User being created with id already exists. """
