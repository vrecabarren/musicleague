from functools import wraps
import urlparse

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from musicleague.environment import is_deployed
from musicleague.notify.flash import flash_error
from musicleague.notify.flash import flash_warning


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'current_user' not in session:
            # Store the url that the user was attempting to reach and redirect
            url = request.url
            parsed_url = urlparse.urlsplit(url)
            next_url = '%s?%s' % (parsed_url.path, parsed_url.query)
            session['next_url'] = next_url.encode('base64', 'strict')
            flash_warning('You must be logged in to reach that page')
            return redirect(url_for('hello', next_url=next_url))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user.is_admin and is_deployed():
            flash_error('You must be an admin to access that page')
            return redirect(url_for('hello'))
        return func(*args, **kwargs)
    return wrapper


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator
