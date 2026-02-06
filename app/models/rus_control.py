"""
Modelo RUSControl - Control de Límites RUS
Control mensual de límites del Régimen Único Simplificado
"""
from app import db
from datetime import datetime


class RUSControl(db.Model):
    """Control mensual de límites RUS"""
    __tablename__ = 'rus_control'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_invoiced = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    transaction_count = db.Column(db.Integer, default=0, nullable=False)
    alert_level = db.Column(
        db.Enum('GREEN', 'YELLOW', 'RED', name='alert_levels'),
        default='GREEN',
        nullable=False
    )
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)  # Bloqueo al superar S/ 8,000
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('year', 'month', name='unique_year_month'),
    )

    def update_total(self, amount, limit_cat1=5000.00, limit_cat2=8000.00):
        """
        Actualiza el total y el nivel de alerta

        Args:
            amount: Monto a agregar
            limit_cat1: Límite categoría 1 (S/ 5,000)
            limit_cat2: Límite categoría 2 (S/ 8,000)
        """
        from decimal import Decimal
        # Asegurar que amount sea Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        self.total_invoiced += amount
        self.transaction_count += 1

        # Convertir límites a Decimal para comparación segura
        d_limit_cat1 = Decimal(str(limit_cat1))
        d_limit_cat2 = Decimal(str(limit_cat2))

        # Actualizar nivel de alerta
        if self.total_invoiced >= d_limit_cat2:
            self.alert_level = 'RED'
            self.is_blocked = True
        elif self.total_invoiced >= d_limit_cat1:
            self.alert_level = 'YELLOW'
        else:
            self.alert_level = 'GREEN'

        self.updated_at = datetime.utcnow()
        db.session.commit()

    def can_add_amount(self, amount, limit=8000.00):
        """Verificar si se puede agregar un monto sin superar el límite"""
        from decimal import Decimal
        d_amount = Decimal(str(amount))
        d_limit = Decimal(str(limit))
        projected = self.total_invoiced + d_amount
        return projected <= d_limit

    def remaining_amount(self, limit=8000.00):
        """Cantidad restante antes de llegar al límite"""
        from decimal import Decimal
        return float(Decimal(str(limit)) - self.total_invoiced)

    def usage_percentage(self, limit=8000.00):
        """Porcentaje de uso del límite"""
        from decimal import Decimal
        total = float(self.total_invoiced)
        return (total / float(limit)) * 100

    def __repr__(self):
        return f'<RUSControl {self.year}-{self.month}: S/ {self.total_invoiced}>'

    def to_dict(self, limit_cat1=5000.00, limit_cat2=8000.00):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'total_invoiced': float(self.total_invoiced),
            'transaction_count': self.transaction_count,
            'alert_level': self.alert_level,
            'is_blocked': self.is_blocked,
            'remaining': self.remaining_amount(limit_cat2),
            'percentage': round(self.usage_percentage(limit_cat2), 2),
            'category_1_limit': limit_cat1,
            'category_2_limit': limit_cat2,
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_or_create_current():
        """Obtener o crear el control del mes actual"""
        now = datetime.utcnow()
        control = RUSControl.query.filter_by(
            year=now.year,
            month=now.month
        ).first()

        if not control:
            control = RUSControl(
                year=now.year,
                month=now.month
            )
            db.session.add(control)
            db.session.commit()

        return control

    @staticmethod
    def get_month_status(year=None, month=None):
        """Obtener estado de un mes específico"""
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month

        control = RUSControl.query.filter_by(year=year, month=month).first()

        if not control:
            control = RUSControl(year=year, month=month)
            db.session.add(control)
            db.session.commit()

        return control
