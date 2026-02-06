"""
Rutas para la gestión y consulta de Ventas
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from app import db
from app.utils.decorators import login_required, role_required
from app.models.sale import Sale
from app.models.customer import Customer
from datetime import datetime

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')


@sales_bp.route('/')
@login_required
def index():
    """Listado de ventas"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    
    query = Sale.query

    # Búsqueda por correlativo o cliente
    if search:
        query = query.join(Customer).filter(
            db.or_(
                Sale.correlative.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                Customer.document_number.like(f"%{search}%")
            )
        )

    # Filtro por estado SUNAT
    if status:
        query = query.filter(Sale.sunat_status == status)

    # Ordenar por fecha descendente
    query = query.order_by(Sale.created_at.desc())

    # Paginación
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    sales = pagination.items

    return render_template('sales/index.html', sales=sales, pagination=pagination)


@sales_bp.route('/<int:sale_id>')
@login_required
def detail(sale_id):
    """Ver detalle de una venta"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sales/detail.html', sale=sale)
