from datetime import datetime

from haikunator import Haikunator

from musicleague import app
from musicleague.models import InvitedUser
from musicleague.models import League
from musicleague.models import LeaguePreferences
from musicleague.notify import user_added_to_league_notification
from musicleague.notify import user_invited_to_league_notification
from musicleague.persistence.statements import DELETE_LEAGUE
from musicleague.scoring import EntrySortKey
from musicleague.submission_period import remove_submission_period
from musicleague.user import get_user_by_email


def add_user(league, user_email, notify=True):
    user = get_user_by_email(user_email)
    if user and user not in league.users:
        league.users.append(user)
        league.save()

        from musicleague.persistence.insert import insert_membership
        insert_membership(league, user)

        if notify:
            user_added_to_league_notification(user, league)

    elif user is None:
        invited_user = InvitedUser(email=user_email)
        invited_user.save()
        league.invited_users.append(invited_user)
        league.save()

        if notify:
            user_invited_to_league_notification(invited_user, league)


def remove_user(league, user_id):
    remaining_users = []
    removed_user = None
    for user in league.users:
        if str(user.id) == user_id:
            removed_user = user
        else:
            remaining_users.append(user)
    league.users = remaining_users
    league.save()


def create_league(user, name=None, users=None):
    if name is None:
        haikunator = Haikunator()
        name = haikunator.haikunate(token_length=0)

    members = [user]
    if users is not None:
        members = list(set(members + users))

    new_league = League(owner=user, users=members, created=datetime.utcnow())
    new_league.preferences = LeaguePreferences(name=name)
    new_league.save()

    from musicleague.persistence.insert import insert_league
    insert_league(new_league)

    return new_league


def remove_league(league_id, league=None):
    if league is None:
        league = get_league(league_id)

    if not league or str(league.id) != str(league_id):
        return

    for submission_period in league.submission_periods:
        remove_submission_period(submission_period.id,
                                 submission_period=submission_period)

    league.delete()

    from musicleague.persistence.delete import delete_league
    delete_league(league)

    return league


def get_league(league_id):
    try:
        league = League.objects.get(id=league_id)
        return league
    except League.DoesNotExist:
        return None


def get_leagues_for_user(user):
    # TODO Page results for user profile page
    try:
        leagues = League.objects(users=user).all().order_by('-created')
        leagues = sorted(leagues, key=LeagueSortKey)
        return leagues
    except League.DoesNotExist:
        return []


class LeagueSortKey(EntrySortKey):

    def _ordered_cmp(self, other):
        _cmp_order = [
            self._cmp_status,
            self._cmp_created,
        ]

        for _cmp in _cmp_order:
            diff = _cmp(other)
            if diff != 0:
                return diff

        return 0

    def _cmp_created(self, other):
        if self.obj.created > other.created:
            return -1
        elif self.obj.created < other.created:
            return 1
        return 0

    def _cmp_status(self, other):
        if self.obj.is_active and not other.is_active:
            return -1
        elif other.is_active and not self.obj.is_active:
            return 1
        elif self.obj.is_inactive and not other.is_inactive:
            return -1
        elif other.is_inactive and not self.obj.is_inactive:
            return 1
        return 0
