from musicleague import mp


def track_new_user(user_id):
    mp.track(user_id, 'Created An Account')


def track_user_login(user_id):
    mp.track(user_id, 'Logged In')


def track_user_logout(user_id):
    mp.track(user_id, 'Logged Out')


def track_user_created_league(user_id, league):
    league_data = {'League Name': league.name,
                   '# Users': len(league.users),
                   '# Rounds': len(league.submission_periods)}
    mp.track(user_id, 'Created A League', league_data)


def track_user_deleted_league(user_id, league):
    league_data = {'League Name': league.name,
                   '# Users': len(league.users),
                   '# Rounds': len(league.submission_periods)}
    mp.track(user_id, 'Deleted A League', league_data)


def track_user_joined_league(user_id, league):
    league_data = {'League Name': league.name,
                   '# Users': len(league.users)}
    mp.track(user_id, 'Joined A League', league_data)


def track_user_submitted(user_id, round):
    round_data = {'Round Name': round.name}
    mp.track(user_id, 'Submitted', round_data)


def track_user_voted(user_id, round):
    round_data = {'Round Name': round.name}
    mp.track(user_id, 'Voted', round_data)
