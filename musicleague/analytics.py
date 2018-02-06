from mixpanel import Mixpanel

from musicleague.environment import get_mixpanel_token
from musicleague.environment import is_production


_mp = None


def get_mixpanel():
    global _mp

    if _mp is not None:
        return _mp

    _mp = NoopMixpanel()
    if is_production():
        _mp = Mixpanel(get_mixpanel_token())

    return _mp


def track_new_user(user_id):
    get_mixpanel().track(user_id, 'Created An Account')


def track_user_login(user_id):
    get_mixpanel().track(user_id, 'Logged In')


def track_user_logout(user_id):
    get_mixpanel().track(user_id, 'Logged Out')


def track_user_created_league(user_id, league):
    league_data = {'League Name': league.name,
                   '# Users': len(league.users),
                   '# Rounds': len(league.submission_periods)}
    get_mixpanel().track(user_id, 'Created A League', league_data)


def track_user_deleted_league(user_id, league):
    league_data = {'League Name': league.name,
                   '# Users': len(league.users),
                   '# Rounds': len(league.submission_periods)}
    get_mixpanel().track(user_id, 'Deleted A League', league_data)


def track_user_joined_league(user_id, league):
    league_data = {'League Name': league.name,
                   '# Users': len(league.users)}
    get_mixpanel().track(user_id, 'Joined A League', league_data)


def track_user_submitted(user_id, round):
    round_data = {'Round Name': round.name}
    get_mixpanel().track(user_id, 'Submitted', round_data)


def track_user_voted(user_id, round):
    round_data = {'Round Name': round.name}
    get_mixpanel().track(user_id, 'Voted', round_data)


class NoopMixpanel:

    def track(self, unique_id, action, additional_data=None):
        return
