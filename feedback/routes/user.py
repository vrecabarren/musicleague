import json

from flask import g
from flask import render_template
from flask import request

from feedback import app
from feedback.models import User
from feedback.routes import urls
from feedback.routes.decorators import login_required
from feedback.season import get_seasons_for_user
from feedback.user import get_user


@app.route(urls.AUTOCOMPLETE)
@login_required
def autocomplete():
    term = request.args.get('term')
    results = User.objects(name__istartswith=term).all()
    results = [{'label': user.name, 'value': user.email} for user in results]
    return json.dumps(results)


@app.route(urls.PROFILE_URL)
@login_required
def profile():
    seasons = get_seasons_for_user(g.user)
    kwargs = {
        'user': g.user,
        'seasons': seasons
    }
    return render_template("profile.html", **kwargs)


@app.route(urls.VIEW_USER_URL)
@login_required
def view_user(user_id):
    kwargs = {
        'user': g.user,
        'page_user': get_user(user_id),
        'user_image': g.spotify.user(user_id).get('images')[0]
    }
    return render_template("user.html", **kwargs)
