"""
Modelo Correlative - Control de Correlativos
Control de numeración secuencial de documentos electrónicos
Evita saltos de numeración y duplicados
"""
from app import db
from datetime import datetime


class Correlative(db.Model):
    """Control de correlativos para evitar saltos"""
    __tablename__ = 'correlatives'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(
        db.Enum('BOLETA', 'FACTURA', 'NOTA_CREDITO', 'NOTA_DEBITO', name='document_types_corr'),
        nullable=False
    )
    series = db.Column(db.String(4), nullable=False)  # B001, F001, etc.
    current_number = db.Column(db.Integer, default=0, nullable=False)
    last_issued = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('document_type', 'series', name='unique_doc_series'),
    )

    def get_next_correlative(self):
        """
        Obtiene el siguiente correlativo SIN avanzar el contador
        Formato: B001-00000002
        """
        next_number = self.current_number + 1
        return f"{self.series}-{str(next_number).zfill(8)}"

    def advance_correlative(self):
        """
        Avanza el correlativo (solo después de éxito en SUNAT)
        CRÍTICO: Solo llamar cuando SUNAT confirme la aceptación
        """
        self.current_number += 1
        self.last_issued = datetime.utcnow()
        db.session.commit()

    def peek_next_number(self):
        """Ver el siguiente número sin avanzar"""
        return self.current_number + 1

    def __repr__(self):
        return f'<Correlative {self.document_type} {self.series}-{str(self.current_number).zfill(8)}>'

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'document_type': self.document_type,
            'series': self.series,
            'current_number': self.current_number,
            'next_correlative': self.get_next_correlative(),
            'last_issued': self.last_issued.isoformat() if self.last_issued else None,
            'is_active': self.is_active
        }

    @staticmethod
    def get_active_for_boleta():
        """Obtener correlativo activo para boletas"""
        return Correlative.query.filter_by(
            document_type='BOLETA',
            is_active=True
        ).first()

    @staticmethod
    def initialize_default():
        """Inicializar correlativo por defecto (B001)"""
        existing = Correlative.query.filter_by(
            document_type='BOLETA',
            series='B001'
        ).first()

        if not existing:
            boleta = Correlative(
                document_type='BOLETA',
                series='B001',
                current_number=1,
                is_active=True
            )
            db.session.add(boleta)
            db.session.commit()
            return boleta

        return existing
