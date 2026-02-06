"""
Rutas del Punto de Venta (POS)
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
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
# from app.services.pse_service import PSEService  # Comentado temporalmente
# from app.services.pdf_service import PDFService  # Comentado temporalmente
from app.utils.validators import is_business_ruc, validate_ruc, validate_dni
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import os

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
                Customer.name.ilike(f"%{query}%")
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

        # Calcular totales (precio ya incluye IGV)
        total = sum(Decimal(str(item['price'])) * Decimal(str(item['quantity'])) for item in items_data)
        
        # Calcular IGV (usando el total que ya lo incluye)
        # total = subtotal + subtotal * 0.18 => total = subtotal * 1.18 => subtotal = total / 1.18
        subtotal = (total / Decimal('1.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax = total - subtotal

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
                name=customer_data.get('full_name'),
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
            # Obtener producto para guardar snapshot
            product = Product.query.get(item_data.get('product_id'))

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data.get('product_id'),
                product_name=item_data.get('name'),
                product_sku=product.sku if product else 'N/A',
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


# ==========================================
# ENDPOINTS SUNAT/PSE
# ==========================================

@pos_bp.route('/send-to-sunat/<int:sale_id>', methods=['POST'])
@login_required
@role_required('admin', 'seller')
def send_to_sunat(sale_id):
    """
    Enviar boleta a SUNAT vía PSE

    Returns:
        JSON con resultado del envío
    """
    try:
        sale = Sale.query.get_or_404(sale_id)

        # Verificar permisos (solo el vendedor o admin)
        if sale.seller_id != current_user.id and not current_user.has_role('admin'):
            return jsonify({
                'success': False,
                'message': 'No tiene permisos para enviar esta boleta'
            }), 403

        # Enviar a SUNAT vía PSE
        # pse_service = PSEService()
        # result = pse_service.send_sale_to_sunat(sale_id)
        result = {'success': True, 'sunat_status': 'ACCEPTED', 'message': 'Simulado (Pruebas)'} # Simulado para pruebas

        if result['success']:
            # Si fue aceptado, generar PDF automáticamente
            if result.get('sunat_status') == 'ACCEPTED':
                try:
                    # pdf_service = PDFService()
                    # pdf_path = pdf_service.generate_invoice_pdf(sale)
                    result['pdf_url'] = '#' # url_for('pos.download_pdf', sale_id=sale_id)
                    
                    # Actualizar path en DB para pruebas
                    # sale.pdf_path = pdf_path
                    # db.session.commit()
                except Exception as pdf_error:
                    # No fallar si el PDF falla, solo loguear
                    from loguru import logger
                    logger.error(f"Error generando PDF para venta {sale_id}: {pdf_error}")

            # Registrar en audit log
            AuditLog.log_action(
                user_id=current_user.id,
                action='sunat_send',
                entity_type='sale',
                entity_id=sale_id,
                details=f"Boleta {sale.correlative} enviada a SUNAT: {result.get('sunat_status')}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )

        return jsonify(result)

    except Exception as e:
        from loguru import logger
        logger.error(f"Error enviando venta {sale_id} a SUNAT: {e}")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        }), 500


@pos_bp.route('/check-sunat-status/<int:sale_id>', methods=['GET'])
@login_required
def check_sunat_status(sale_id):
    """
    Verificar estado de envío a SUNAT

    Returns:
        JSON con estado actual
    """
    try:
        # pse_service = PSEService()
        # result = pse_service.check_sunat_status(sale_id)
        result = {'success': True, 'sunat_status': 'ACCEPTED'} # Simulado

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        from loguru import logger
        logger.error(f"Error verificando estado SUNAT de venta {sale_id}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pos_bp.route('/download-pdf/<int:sale_id>', methods=['GET'])
@login_required
def download_pdf(sale_id):
    """
    Descargar PDF de boleta

    Si no existe, lo genera automáticamente (solo si está aceptado por SUNAT)
    """
    try:
        sale = Sale.query.get_or_404(sale_id)

        # Verificar que esté aceptado por SUNAT
        if sale.sunat_status != 'ACCEPTED':
            return jsonify({
                'error': 'La boleta debe estar aceptada por SUNAT para descargar el PDF'
            }), 400

        # Generar PDF si no existe
        if not sale.pdf_path or not os.path.exists(sale.pdf_path):
            from loguru import logger
            logger.info(f"Generando PDF para venta {sale_id} (Simulado)")

            # pdf_service = PDFService()
            # pdf_path = pdf_service.generate_invoice_pdf(sale)
            # sale.pdf_path = pdf_path
            # db.session.commit()
            return jsonify({'error': 'PDF no disponible en modo prueba'}), 404

        # Verificar que el archivo existe
        if not os.path.exists(sale.pdf_path):
            return jsonify({
                'error': 'PDF no encontrado'
            }), 404

        # Enviar archivo
        return send_file(
            sale.pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Boleta_{sale.correlative}.pdf"
        )

    except Exception as e:
        from loguru import logger
        logger.error(f"Error descargando PDF de venta {sale_id}: {e}")
        return jsonify({
            'error': f'Error al descargar PDF: {str(e)}'
        }), 500


@pos_bp.route('/resend-to-sunat/<int:sale_id>', methods=['POST'])
@login_required
@role_required('admin', 'seller')
def resend_to_sunat(sale_id):
    """
    Reenviar boleta con error o rechazada

    Solo permite reenvío de estados ERROR o REJECTED
    """
    try:
        sale = Sale.query.get_or_404(sale_id)

        # Verificar permisos
        if sale.seller_id != current_user.id and not current_user.has_role('admin'):
            return jsonify({
                'success': False,
                'message': 'No tiene permisos para reenviar esta boleta'
            }), 403

        # Verificar que pueda reenviarse
        if sale.sunat_status not in ['ERROR', 'REJECTED']:
            return jsonify({
                'success': False,
                'message': f'No se puede reenviar boletas con estado {sale.sunat_status}'
            }), 400

        # Reenviar
        pse_service = PSEService()
        result = pse_service.resend_to_sunat(sale_id)

        if result['success']:
            # Registrar en audit log
            AuditLog.log_action(
                user_id=current_user.id,
                action='sunat_resend',
                entity_type='sale',
                entity_id=sale_id,
                details=f"Boleta {sale.correlative} reenviada a SUNAT: {result.get('sunat_status')}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )

        return jsonify(result)

    except Exception as e:
        from loguru import logger
        logger.error(f"Error reenviando venta {sale_id} a SUNAT: {e}")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        }), 500
