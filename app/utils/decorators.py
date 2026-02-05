"""
Decoradores de seguridad y control de acceso
"""
from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def login_required(f):
    """
    Decorador para requerir autenticación

    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return 'Protected content'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorador para requerir roles específicos

    Args:
        *roles: Roles permitidos ('admin', 'seller', 'viewer')

    Usage:
        @app.route('/admin')
        @role_required('admin')
        def admin_page():
            return 'Admin only'

        @app.route('/sales')
        @role_required('admin', 'seller')
        def sales_page():
            return 'Admin or Seller'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                flash('No tienes permisos para acceder a esta página.', 'danger')
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorador para requerir rol de administrador

    Usage:
        @app.route('/admin/settings')
        @admin_required
        def admin_settings():
            return 'Admin settings'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))

        if current_user.role != 'admin':
            flash('Solo administradores pueden acceder a esta página.', 'danger')
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def active_user_required(f):
    """
    Decorador para requerir usuario activo

    Usage:
        @app.route('/dashboard')
        @active_user_required
        def dashboard():
            return 'Dashboard'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_active:
            flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'danger')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function
