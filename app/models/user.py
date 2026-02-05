"""
Modelo User - Usuarios del Sistema
Gestiona los usuarios que pueden acceder al sistema (vendedores, admin)
"""
from app import db, bcrypt
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    """Modelo de Usuario del Sistema"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Enum('admin', 'seller', 'viewer', name='user_roles'), default='seller', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    sales = db.relationship('Sale', backref='seller', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Hashear contraseña usando bcrypt"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verificar contraseña"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Verificar si el usuario es administrador"""
        return self.role == 'admin'

    def can_sell(self):
        """Verificar si el usuario puede vender"""
        return self.role in ['admin', 'seller'] and self.is_active

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convertir a diccionario (sin password_hash)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }
