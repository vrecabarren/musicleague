from functools import wraps
import urlparse

from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from feedback.league import get_league


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'current_user' not in session:
            # Store the url that the user was attempting to reach and redirect
            url = request.url
            parsed_url = urlparse.urlsplit(url)
            next_url = '%s?%s' % (parsed_url.path, parsed_url.query)
            session['next_url'] = next_url.encode('base64', 'strict')
            return redirect(url_for('hello', next_url=next_url))
        return func(*args, **kwargs)
    return wrapper


def league_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'league_id' not in kwargs:
            return redirect(url_for('hello'))
        league = get_league(kwargs.get('league_id'))
        if not league:
            return redirect(url_for('hello'))
        kwargs['league'] = league
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
