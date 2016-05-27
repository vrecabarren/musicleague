from flask import g
from flask import render_template

from feedback import app
from feedback.spotify import get_spotify_oauth
from feedback.routes import urls
from feedback.routes.auth import before_request  # noqa
from feedback.routes.auth import login  # noqa
from feedback.routes.auth import logout  # noqa
from feedback.routes.season import add_user_for_season  # noqa
from feedback.routes.season import post_create_season  # noqa
from feedback.routes.season import post_create_submission_period  # noqa
from feedback.routes.season import remove_season  # noqa
from feedback.routes.season import remove_submission_period  # noqa
from feedback.routes.season import view_submission_period  # noqa
from feedback.routes.season import view_season  # noqa
from feedback.routes.spotify import create_spotify_playlist  # noqa
from feedback.routes.spotify import view_playlist  # noqa
from feedback.routes.submit import post_confirm_submit  # noqa
from feedback.routes.submit import post_submit  # noqa
from feedback.routes.submit import view_confirm_submit  # noqa
from feedback.routes.submit import view_submit  # noqa
from feedback.routes.user import profile  # noqa
from feedback.routes.user import view_user  # noqa


@app.route(urls.HELLO_URL)
def hello():
    kwargs = {
        'user': g.user,
        'oauth_url': get_spotify_oauth().get_authorize_url()
    }
    return render_template("hello.html", **kwargs)
