"""
Modelos de la Aplicación
Importación centralizada de todos los modelos
"""
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product
from app.models.correlative import Correlative
from app.models.sale import Sale, SaleItem
from app.models.rus_control import RUSControl
from app.models.audit_log import AuditLog

__all__ = [
    'User',
    'Customer',
    'Product',
    'Correlative',
    'Sale',
    'SaleItem',
    'RUSControl',
    'AuditLog'
]
