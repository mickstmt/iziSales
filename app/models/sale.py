"""
Modelo Sale y SaleItem - Ventas y Detalles
Gestiona las ventas y sus items
"""
from app import db
from datetime import datetime


class Sale(db.Model):
    """Venta principal"""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    correlative = db.Column(db.String(20), unique=True, nullable=False, index=True)  # B001-00000002
    document_type = db.Column(
        db.Enum('BOLETA', 'FACTURA', name='sale_document_types'),
        default='BOLETA',
        nullable=False
    )

    # Relaciones FK
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Montos
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)  # Sin IGV
    tax = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)  # IGV
    total = db.Column(db.Numeric(10, 2), nullable=False)  # Total a pagar

    # Control SUNAT
    xml_path = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    cdr_path = db.Column(db.String(255))
    qr_code = db.Column(db.Text)
    hash = db.Column(db.String(255))

    # Estados
    sunat_status = db.Column(
        db.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'ERROR', name='sunat_statuses'),
        default='PENDING',
        nullable=False
    )
    sunat_response = db.Column(db.Text)
    sunat_sent_at = db.Column(db.DateTime)

    # Cancelación
    is_cancelled = db.Column(db.Boolean, default=False, nullable=False)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.String(255))

    # Notas
    notes = db.Column(db.Text)

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sale {self.correlative}>'

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'correlative': self.correlative,
            'document_type': self.document_type,
            'customer': self.customer.to_dict() if self.customer else None,
            'seller': self.seller.to_dict() if self.seller else None,
            'subtotal': float(self.subtotal),
            'tax': float(self.tax),
            'total': float(self.total),
            'sunat_status': self.sunat_status,
            'is_cancelled': self.is_cancelled,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }

    @property
    def status_display(self):
        """Estado legible"""
        status_map = {
            'PENDING': 'Pendiente',
            'ACCEPTED': 'Aceptado',
            'REJECTED': 'Rechazado',
            'ERROR': 'Error'
        }
        return status_map.get(self.sunat_status, self.sunat_status)

    def calculate_totals(self):
        """Calcular totales basado en items"""
        total = sum(item.subtotal for item in self.items)
        self.total = total
        # Para RUS: El IGV está incluido en el precio
        self.subtotal = total / 1.18
        self.tax = total - self.subtotal

    def cancel(self, reason=None):
        """Cancelar venta"""
        self.is_cancelled = True
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        db.session.commit()


class SaleItem(db.Model):
    """Detalle de items de la venta"""
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    # Información adicional del producto (snapshot al momento de la venta)
    product_name = db.Column(db.String(255), nullable=False)
    product_sku = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<SaleItem {self.product_sku} x{self.quantity}>'

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_sku': self.product_sku,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal)
        }

    def calculate_subtotal(self):
        """Calcular subtotal del item"""
        self.subtotal = self.quantity * self.unit_price
