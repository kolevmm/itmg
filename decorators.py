# decorators.py
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # Проверка за автентикация и роля
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Нямате права за достъп до тази страница!', 'danger')
                return redirect(url_for('dashboard'))  # Или друг маршрут
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper