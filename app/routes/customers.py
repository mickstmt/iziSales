"""
Rutas de Clientes
CRUD completo para gestión de clientes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from app import db
from app.utils.decorators import login_required, role_required
from app.models.customer import Customer
from app.utils.validators import validate_dni, validate_ruc
from datetime import datetime

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')


@customers_bp.route('/')
@login_required
def index():
    """Lista de clientes con paginación y búsqueda"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()

    query = Customer.query

    # Filtro de búsqueda
    if search:
        query = query.filter(
            db.or_(
                Customer.document_number.like(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
        )

    # Ordenar por más reciente
    query = query.order_by(Customer.created_at.desc())

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    customers = pagination.items

    context = {
        'customers': customers,
        'pagination': pagination,
        'search': search,
        'total': query.count()
    }

    return render_template('customers/index.html', **context)


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'seller')
def create():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        try:
            document_type = request.form.get('document_type')
            document_number = request.form.get('document_number', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()

            # Validaciones
            if not document_type or not document_number or not name:
                flash('Tipo de documento, número y nombre son requeridos', 'error')
                return redirect(url_for('customers.create'))

            # Validar formato de documento
            if document_type == 'DNI' and not validate_dni(document_number):
                flash('DNI inválido. Debe tener 8 dígitos', 'error')
                return redirect(url_for('customers.create'))

            if document_type == 'RUC' and not validate_ruc(document_number):
                flash('RUC inválido. Debe tener 11 dígitos', 'error')
                return redirect(url_for('customers.create'))

            # Verificar si ya existe
            existing = Customer.query.filter_by(document_number=document_number).first()
            if existing:
                flash(f'Ya existe un cliente con el documento {document_number}', 'error')
                return redirect(url_for('customers.create'))

            # Crear cliente
            customer = Customer(
                document_type=document_type,
                document_number=document_number,
                name=name,
                email=email if email else None,
                phone=phone if phone else None,
                address=address if address else None,
                is_business=(document_type == 'RUC' and document_number.startswith('20'))
            )

            db.session.add(customer)
            db.session.commit()

            flash(f'Cliente {name} creado exitosamente', 'success')
            return redirect(url_for('customers.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cliente: {str(e)}', 'error')
            return redirect(url_for('customers.create'))

    return render_template('customers/create.html')


@customers_bp.route('/<int:customer_id>')
@login_required
def view(customer_id):
    """Ver detalle de cliente"""
    customer = Customer.query.get_or_404(customer_id)

    # Obtener ventas del cliente
    sales = customer.sales.order_by(db.desc('created_at')).limit(10).all()

    context = {
        'customer': customer,
        'recent_sales': sales,
        'total_sales': customer.sales.count(),
        'total_amount': sum(sale.total for sale in customer.sales.all())
    }

    return render_template('customers/view.html', **context)


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'seller')
def edit(customer_id):
    """Editar cliente existente"""
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()

            # Validaciones
            if not name:
                flash('El nombre es requerido', 'error')
                return redirect(url_for('customers.edit', customer_id=customer_id))

            # Actualizar datos
            customer.name = name
            customer.email = email if email else None
            customer.phone = phone if phone else None
            customer.address = address if address else None

            db.session.commit()

            flash(f'Cliente {name} actualizado exitosamente', 'success')
            return redirect(url_for('customers.view', customer_id=customer_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cliente: {str(e)}', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

    return render_template('customers/edit.html', customer=customer)


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete(customer_id):
    """Eliminar cliente (solo admin y si no tiene ventas)"""
    try:
        customer = Customer.query.get_or_404(customer_id)

        # Verificar que no tenga ventas
        if customer.sales.count() > 0:
            flash('No se puede eliminar un cliente con ventas registradas', 'error')
            return redirect(url_for('customers.view', customer_id=customer_id))

        name = customer.name
        db.session.delete(customer)
        db.session.commit()

        flash(f'Cliente {name} eliminado exitosamente', 'success')
        return redirect(url_for('customers.index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar cliente: {str(e)}', 'error')
        return redirect(url_for('customers.view', customer_id=customer_id))


# API endpoints para autocomplete
@customers_bp.route('/api/search', methods=['GET'])
@login_required
def api_search():
    """Búsqueda de clientes para autocomplete (usado en POS)"""
    query = request.args.get('q', '').strip()

    if len(query) < 3:
        return jsonify([])

    customers = Customer.query.filter(
        db.or_(
            Customer.document_number.like(f"%{query}%"),
            Customer.name.ilike(f"%{query}%")
        )
    ).limit(10).all()

    return jsonify([customer.to_dict() for customer in customers])


@customers_bp.route('/api/consultar-documento', methods=['GET'])
@login_required
def consultar_documento():
    """
    Consultar datos de RUC/DNI en SUNAT vía APIs externas

    Params:
        tipo: 'RUC' o 'DNI'
        numero: Número de documento

    Returns:
        JSON con datos del documento o error
    """
    try:
        from app.services.sunat_api_service import SunatAPIService

        tipo = request.args.get('tipo', '').upper()
        numero = request.args.get('numero', '').strip()

        if not tipo or not numero:
            return jsonify({'error': 'Tipo y número de documento requeridos'}), 400

        service = SunatAPIService()

        if tipo == 'RUC':
            if len(numero) != 11:
                return jsonify({'error': 'RUC debe tener 11 dígitos'}), 400

            datos = service.consultar_ruc(numero)

            if datos:
                return jsonify({
                    'success': True,
                    'data': {
                        'nombre': datos.get('razon_social'),
                        'direccion': datos.get('direccion'),
                        'estado': datos.get('estado'),
                        'condicion': datos.get('condicion'),
                        'tipo_contribuyente': datos.get('tipo_contribuyente'),
                        'ubigeo': datos.get('ubigeo'),
                        'departamento': datos.get('departamento'),
                        'provincia': datos.get('provincia'),
                        'distrito': datos.get('distrito')
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No se encontró información del RUC en SUNAT'
                }), 404

        elif tipo == 'DNI':
            if len(numero) != 8:
                return jsonify({'error': 'DNI debe tener 8 dígitos'}), 400

            datos = service.consultar_dni(numero)

            if datos:
                return jsonify({
                    'success': True,
                    'data': {
                        'nombre': datos.get('nombre_completo'),
                        'nombres': datos.get('nombres'),
                        'apellido_paterno': datos.get('apellido_paterno'),
                        'apellido_materno': datos.get('apellido_materno')
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No se encontró información del DNI en RENIEC'
                }), 404

        else:
            return jsonify({'error': 'Tipo de documento no válido (solo RUC o DNI)'}), 400

    except Exception as e:
        from loguru import logger
        logger.error(f"Error consultando documento: {e}")
        return jsonify({'error': f'Error al consultar documento: {str(e)}'}), 500
