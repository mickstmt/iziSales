"""
Modelo AuditLog - Auditoría de Operaciones
Log de todas las operaciones críticas del sistema
"""
from app import db
from datetime import datetime
import json


class AuditLog(db.Model):
    """Log de auditoría de todas las operaciones críticas"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Puede ser null para acciones del sistema
    action = db.Column(db.String(100), nullable=False, index=True)  # 'CREATE_SALE', 'CANCEL_SALE', 'LOGIN', etc.
    entity_type = db.Column(db.String(50), index=True)  # 'Sale', 'Customer', 'User', etc.
    entity_id = db.Column(db.Integer)  # ID de la entidad afectada
    details = db.Column(db.Text)  # JSON con detalles adicionales
    ip_address = db.Column(db.String(45))  # IPv4 o IPv6
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': json.loads(self.details) if self.details else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def log_action(action, user_id=None, entity_type=None, entity_id=None,
                   details=None, ip_address=None, user_agent=None):
        """
        Registrar una acción en el log de auditoría

        Args:
            action: Acción realizada (ej: 'CREATE_SALE', 'LOGIN', 'CANCEL_SALE')
            user_id: ID del usuario que realizó la acción
            entity_type: Tipo de entidad afectada (ej: 'Sale', 'Customer')
            entity_id: ID de la entidad afectada
            details: Diccionario con detalles adicionales
            ip_address: Dirección IP del usuario
            user_agent: User agent del navegador
        """
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_user_activity(user_id, limit=50):
        """Obtener actividad reciente de un usuario"""
        return AuditLog.query.filter_by(user_id=user_id).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_entity_history(entity_type, entity_id):
        """Obtener historial de una entidad específica"""
        return AuditLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(AuditLog.created_at.desc()).all()

    @staticmethod
    def get_recent_logs(limit=100):
        """Obtener logs recientes del sistema"""
        return AuditLog.query.order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
