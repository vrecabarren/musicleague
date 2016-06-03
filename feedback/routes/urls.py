# flake8: noqa


LEAGUE_URL = '/l/<league_name>/'


ADD_USER_FOR_LEAGUE_URL = LEAGUE_URL + 'users/add/'
AUTOCOMPLETE = '/autocomplete/'
CONFIRM_SUBMIT_URL = LEAGUE_URL + 'submit/<submission_id>/confirm/'
CREATE_PLAYLIST_URL = LEAGUE_URL + 'playlist/create/'
CREATE_LEAGUE_URL = '/l/create/'
CREATE_SUBMISSION_PERIOD_URL = LEAGUE_URL + 'submission_period/create/'
HELLO_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
PROFILE_URL = '/profile/'
REMOVE_LEAGUE_URL = LEAGUE_URL + 'remove/'
REMOVE_SUBMISSION_URL = LEAGUE_URL + '<submission_period_id>/<submission_id>/remove/'
REMOVE_SUBMISSION_PERIOD_URL = LEAGUE_URL + '<submission_period_id>/remove/'
REMOVE_USER_FOR_LEAGUE_URL = LEAGUE_URL + 'users/remove/<user_id>/'
VIEW_LEAGUE_URL = LEAGUE_URL
VIEW_PLAYLIST_URL = LEAGUE_URL + 'playlist/'
VIEW_SUBMISSION_PERIOD_URL = LEAGUE_URL + '<submission_period_id>/'
VIEW_SUBMIT_URL = LEAGUE_URL + 'submit/'
VIEW_USER_URL = '/user/<user_id>/'
