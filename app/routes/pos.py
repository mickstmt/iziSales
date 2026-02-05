"""
Rutas del Punto de Venta (POS)
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from app import db
from app.utils.decorators import login_required, role_required
from app.models.sale import Sale, SaleItem
from app.models.customer import Customer
from app.models.product import Product
from app.models.correlative import Correlative
from app.models.rus_control import RUSControl
from app.models.audit_log import AuditLog
from app.services.woocommerce_service import WooCommerceService
from app.utils.validators import is_business_ruc, validate_ruc, validate_dni
from datetime import datetime

pos_bp = Blueprint('pos', __name__, url_prefix='/pos')


@pos_bp.route('/')
@login_required
@role_required('admin', 'seller')
def index():
    """Vista principal del punto de venta"""
    # Verificar estado RUS
    rus_control = RUSControl.get_or_create_current()

    context = {
        'rus_control': rus_control,
        'user': current_user
    }

    return render_template('pos/index.html', **context)


@pos_bp.route('/search-products', methods=['GET'])
@login_required
def search_products():
    """Buscar productos para el POS"""
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify([])

    try:
        # Buscar en base de datos local primero
        woo_service = WooCommerceService()
        products = woo_service.get_local_products(search=query, limit=20)

        return jsonify(products)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pos_bp.route('/search-customers', methods=['GET'])
@login_required
def search_customers():
    """Buscar clientes por documento"""
    query = request.args.get('q', '').strip()

    if len(query) < 3:
        return jsonify([])

    try:
        customers = Customer.query.filter(
            db.or_(
                Customer.document_number.like(f"%{query}%"),
                Customer.full_name.ilike(f"%{query}%")
            )
        ).limit(10).all()

        return jsonify([customer.to_dict() for customer in customers])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pos_bp.route('/create-sale', methods=['POST'])
@login_required
@role_required('admin', 'seller')
def create_sale():
    """Crear una nueva venta desde el POS"""
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data.get('customer'):
            return jsonify({'error': 'Cliente requerido'}), 400

        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'Debe agregar al menos un producto'}), 400

        customer_data = data['customer']
        items_data = data['items']

        # Validar tipo de documento
        document_type = customer_data.get('document_type')
        document_number = customer_data.get('document_number')

        # Validar RUC 20 (no se puede emitir boleta a empresas)
        if document_type == 'RUC' and document_number:
            is_business, _ = is_business_ruc(document_number)
            if is_business:
                return jsonify({
                    'error': 'No se puede emitir boleta a empresas (RUC 20). El RUS solo permite emitir a consumidores finales.'
                }), 400

        # Calcular totales
        subtotal = sum(float(item['price']) * int(item['quantity']) for item in items_data)
        tax = subtotal * 0.18  # IGV 18%
        total = subtotal + tax

        # Verificar límite RUS
        rus_control = RUSControl.get_or_create_current()

        if not rus_control.can_add_amount(total):
            return jsonify({
                'error': f'Límite RUS excedido. Disponible: S/ {rus_control.remaining_amount():.2f}'
            }), 400

        # Buscar o crear cliente
        customer = Customer.query.filter_by(
            document_number=document_number
        ).first()

        if not customer:
            customer = Customer(
                document_type=document_type,
                document_number=document_number,
                full_name=customer_data.get('full_name'),
                email=customer_data.get('email'),
                phone=customer_data.get('phone'),
                address=customer_data.get('address')
            )
            db.session.add(customer)
            db.session.flush()  # Para obtener el ID

        # Obtener correlativo
        correlative_obj = Correlative.query.filter_by(
            document_type='BOLETA',
            is_active=True
        ).first()

        if not correlative_obj:
            return jsonify({'error': 'No hay correlativo activo para boletas'}), 400

        correlative = correlative_obj.get_next_correlative()

        # Crear venta
        sale = Sale(
            correlative=correlative,
            document_type='BOLETA',
            customer_id=customer.id,
            seller_id=current_user.id,
            subtotal=subtotal,
            tax=tax,
            total=total,
            sunat_status='PENDING'
        )
        db.session.add(sale)
        db.session.flush()

        # Crear items de venta
        for item_data in items_data:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data.get('product_id'),
                description=item_data.get('name'),
                quantity=int(item_data['quantity']),
                unit_price=float(item_data['price']),
                subtotal=float(item_data['price']) * int(item_data['quantity'])
            )
            db.session.add(sale_item)

        # Avanzar correlativo
        correlative_obj.advance_correlative()

        # Actualizar control RUS
        rus_control.update_total(total)

        # Commit de todas las operaciones
        db.session.commit()

        # Registrar en audit log
        AuditLog.log_action(
            user_id=current_user.id,
            action='sale_created',
            entity_type='sale',
            entity_id=sale.id,
            details=f'Venta {correlative} - Total: S/ {total:.2f}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )

        return jsonify({
            'success': True,
            'sale_id': sale.id,
            'correlative': correlative,
            'total': float(total),
            'message': f'Venta {correlative} registrada exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear venta: {str(e)}'}), 500
