from flask import redirect
from flask import request

from musicleague import app
from musicleague.models import User
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required
from musicleague.user import get_user


MAKE_USER_ADMIN_URL = '/admin/users/<user_id>/make_admin/'


@app.route(MAKE_USER_ADMIN_URL)
@login_required
@admin_required
def admin_make_user_admin(user_id):
    if not user_id:
        return

    user = get_user(user_id)
    if not user:
        return

    user.roles = list(set(user.roles + [User.ADMIN]))
    user.save()

    return redirect(request.referrer)
