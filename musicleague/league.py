from datetime import datetime

from bson.objectid import ObjectId
from haikunator import Haikunator

from musicleague.notify import user_added_to_league_notification
from musicleague.notify import user_invited_to_league_notification
from musicleague.persistence.delete import delete_league
from musicleague.persistence.delete import delete_membership
from musicleague.persistence.insert import insert_league, insert_invited_user
from musicleague.persistence.insert import insert_membership
from musicleague.persistence.models import InvitedUser
from musicleague.persistence.models import League
from musicleague.persistence.models import LeagueStatus
from musicleague.persistence.select import select_league
from musicleague.scoring import EntrySortKey
from musicleague.submission_period import remove_submission_period
from musicleague.user import get_user_by_email


def add_user(league, user_email, notify=True):
    user = get_user_by_email(user_email)
    if user and user not in league.users:
        league.users.append(user)
        insert_membership(league, user)

        if notify:
            user_added_to_league_notification(user, league)

    elif user is None:
        invited_user = InvitedUser(id=str(ObjectId()), email=user_email, league_id=league.id)
        insert_invited_user(invited_user)
        league.invited_users.append(invited_user)

        if notify:
            user_invited_to_league_notification(invited_user, league)


def remove_user(league, user_id):
    remaining_users = []
    for user in league.users:
        if str(user.id) != user_id:
            remaining_users.append(user)
        else:
            delete_membership(league, user)
    league.users = remaining_users


def create_league(user, name=None, users=None):
    if name is None:
        haikunator = Haikunator()
        name = haikunator.haikunate(token_length=0)

    new_league = League(id=str(ObjectId()), created=datetime.utcnow(), name=name,
                        owner_id=user.id, status=LeagueStatus.CREATED)
    new_league.owner = user

    insert_league(new_league)

    members = [user]
    if users is not None:
        members = list(set(members + users))

    for member in members:
        insert_membership(new_league, member)

    return new_league


def remove_league(league_id, league=None):
    if league is None:
        league = select_league(league_id)

    if not league or str(league.id) != str(league_id):
        return

    for submission_period in league.submission_periods:
        remove_submission_period(submission_period.id,
                                 submission_period=submission_period)

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
