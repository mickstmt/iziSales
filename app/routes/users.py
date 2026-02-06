"""
Rutas de Gestión de Usuarios
CRUD completo para administradores
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, bcrypt
from app.utils.decorators import role_required
from app.models.user import User
from app.models.audit_log import AuditLog
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@role_required('admin')
def index():
    """Lista de usuarios del sistema"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'seller')

        if not username or not email or not full_name or not password:
            flash('Todos los campos son obligatorios', 'error')
            return render_template('users/create.html')

        # Verificar si existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return render_template('users/create.html')
        
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya existe', 'error')
            return render_template('users/create.html')

        try:
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            AuditLog.log_action(
                user_id=current_user.id,
                action='user_created',
                entity_type='user',
                entity_id=new_user.id,
                details=f"Usuario creado: {username} ({role})"
            )

            flash(f'Usuario {username} creado con éxito', 'success')
            return redirect(url_for('users.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')

    return render_template('users/create.html')

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit(user_id):
    """Editar usuario existente"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        user.email = request.form.get('email', '').strip()
        user.role = request.form.get('role', user.role)
        
        # Un admin no debería poder quitarse su propio rol de admin accidentalmente 
        # o desactivarse a sí mismo si es el único
        if user.id == current_user.id and user.role != 'admin':
            user.role = 'admin'
            flash('No puedes quitarte el rol de administrador a ti mismo', 'warning')

        try:
            db.session.commit()
            AuditLog.log_action(
                user_id=current_user.id,
                action='user_updated',
                entity_type='user',
                entity_id=user.id,
                details=f"Usuario actualizado: {user.username}"
            )
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('users.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'error')

    return render_template('users/edit.html', user=user)

@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_status(user_id):
    """Activar/Desactivar usuario"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'No puedes desactivar tu propia cuenta'}), 400

    user.is_active = not user.is_active
    db.session.commit()

    action = 'user_activated' if user.is_active else 'user_deactivated'
    AuditLog.log_action(
        user_id=current_user.id,
        action=action,
        entity_type='user',
        entity_id=user.id,
        details=f"Estado de {user.username} cambiado a: {user.is_active}"
    )

    return jsonify({
        'success': True, 
        'is_active': user.is_active,
        'message': f"Usuario {'activado' if user.is_active else 'desactivado'} correctamente"
    })

@users_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@login_required
@role_required('admin')
def reset_password(user_id):
    """Resetear contraseña de usuario"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')

    if not new_password:
        return jsonify({'success': False, 'message': 'La nueva contraseña es requerida'}), 400

    user.set_password(new_password)
    db.session.commit()

    AuditLog.log_action(
        user_id=current_user.id,
        action='password_reset',
        entity_type='user',
        entity_id=user.id,
        details=f"Contraseña reseteada para: {user.username}"
    )

    return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})
