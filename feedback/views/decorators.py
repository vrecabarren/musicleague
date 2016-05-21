from functools import wraps

from flask import redirect
from flask import session
from flask import url_for


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'current_user' not in session:
            return redirect(url_for('hello'))
        return func(*args, **kwargs)
    return wrapper
