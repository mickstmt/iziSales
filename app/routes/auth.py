"""
Rutas de Autenticación
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User
from app.models.audit_log import AuditLog

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        # Validar campos
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña.', 'danger')
            return render_template('auth/login.html')

        # Buscar usuario
        user = User.query.filter_by(username=username).first()

        # Verificar usuario y contraseña
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'danger')
                # Log failed login attempt
                AuditLog.log_action(
                    user_id=user.id,
                    action='login_failed',
                    details='Cuenta desactivada',
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                return render_template('auth/login.html')

            # Login exitoso
            login_user(user, remember=remember)
            flash(f'¡Bienvenido, {user.full_name}!', 'success')

            # Log successful login
            AuditLog.log_action(
                user_id=user.id,
                action='login',
                details='Inicio de sesión exitoso',
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )

            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            # Log failed login attempt
            if user:
                AuditLog.log_action(
                    user_id=user.id,
                    action='login_failed',
                    details='Contraseña incorrecta',
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    if current_user.is_authenticated:
        # Log logout
        AuditLog.log_action(
            user_id=current_user.id,
            action='logout',
            details='Cierre de sesión',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )

        logout_user()
        flash('Sesión cerrada exitosamente.', 'success')

    return redirect(url_for('auth.login'))
