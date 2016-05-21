from functools import wraps

from flask import redirect
from flask import session
from flask import url_for

from feedback.user import get_user


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'current_user' not in session:
            return redirect(url_for('hello'))
        kwargs['user'] = get_user(session['current_user'])
        return func(*args, **kwargs)
    return wrapper
