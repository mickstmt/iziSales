"""
Modelo Customer - Clientes
Gestiona los clientes a quienes se emiten boletas
"""
from app import db
from datetime import datetime


class Customer(db.Model):
    """Modelo de Cliente"""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(
        db.Enum('DNI', 'RUC', 'CE', 'PASAPORTE', name='document_types'),
        nullable=False
    )
    document_number = db.Column(db.String(11), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_business = db.Column(db.Boolean, default=False, nullable=False)  # True si es RUC 20
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    sales = db.relationship('Sale', backref='customer', lazy='dynamic')

    def __repr__(self):
        return f'<Customer {self.document_number} - {self.name}>'

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'name': self.name,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'is_business': self.is_business,
            'created_at': self.created_at.isoformat()
        }

    @property
    def document_display(self):
        """Formato de visualización del documento"""
        return f"{self.document_type}: {self.document_number}"

    @staticmethod
    def get_or_create(document_type, document_number, name, **kwargs):
        """Obtener o crear cliente"""
        customer = Customer.query.filter_by(document_number=document_number).first()

        if not customer:
            customer = Customer(
                document_type=document_type,
                document_number=document_number,
                name=name,
                **kwargs
            )
            db.session.add(customer)
            db.session.commit()

        return customer
