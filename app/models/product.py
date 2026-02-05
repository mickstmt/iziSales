"""
Modelo Product - Cache Local de Productos
Cache local de productos sincronizados desde WooCommerce
"""
from app import db
from datetime import datetime


class Product(db.Model):
    """Cache local de productos de WooCommerce"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    woo_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    sale_items = db.relationship('SaleItem', backref='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.sku} - {self.name}>'

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'woo_id': self.woo_id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'last_sync': self.last_sync.isoformat(),
            'created_at': self.created_at.isoformat()
        }

    @property
    def in_stock(self):
        """Verificar si hay stock disponible"""
        return self.stock_quantity > 0

    @staticmethod
    def search_by_sku_or_name(query):
        """Buscar productos por SKU o nombre"""
        search = f"%{query}%"
        return Product.query.filter(
            db.and_(
                Product.is_active == True,
                db.or_(
                    Product.sku.like(search),
                    Product.name.like(search)
                )
            )
        ).all()

    def update_from_woo(self, woo_data):
        """Actualizar datos desde WooCommerce"""
        self.name = woo_data.get('name', self.name)
        self.description = woo_data.get('short_description', self.description)
        self.price = float(woo_data.get('price', 0))
        self.stock_quantity = woo_data.get('stock_quantity', 0)
        self.is_active = woo_data.get('status') == 'publish'
        self.last_sync = datetime.utcnow()
        db.session.commit()
