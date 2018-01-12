from flask import redirect
from flask import request

from musicleague import app
from musicleague.persistence.select import select_user
from musicleague.persistence.update import update_user
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required


MAKE_USER_ADMIN_URL = '/admin/users/<user_id>/make_admin/'


@app.route(MAKE_USER_ADMIN_URL)
@login_required
@admin_required
def admin_make_user_admin(user_id):
    if not user_id:
        return

    user = select_user(user_id)
    if not user:
        return

    user.is_admin = True
    update_user(user)

    return redirect(request.referrer)
