"""
Script de prueba para el flujo de SUNAT en Modo Sandbox
"""
import os
import sys
from decimal import Decimal

# Añadir el directorio raíz al path para poder importar la app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.config import config
from app.models.sale import Sale, SaleItem
from app.models.customer import Customer
from app.models.user import User
from app.services.pse_service import PSEService

app = create_app(config['testing'])
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' # In-memory
app.config['PSE_SANDBOX_MODE'] = True

with app.app_context():
    print("--- INICIANDO PRUEBA DE FLUJO SUNAT (MODO SANDBOX) ---")
    
    # Crear tablas en SQLite in-memory para la prueba
    db.create_all()
    
    # 1. Buscar o crear una venta de prueba
    sale = Sale.query.filter_by(correlative='B001-TEST0001').first()
    if not sale:
        print("Creando venta de prueba...")
        customer = Customer.query.first()
        if not customer:
            customer = Customer(document_type='DNI', document_number='12345678', name='Cliente Prueba')
            db.session.add(customer)
        
        user = User.query.first()
        if not user:
            user = User(username='testadmin', email='test@example.com', full_name='Vendedor Prueba')
            user.set_password('password')
            db.session.add(user)
            db.session.flush()
        
        sale = Sale(
            correlative='B001-TEST0001',
            document_type='BOLETA',
            customer=customer,
            seller=user,
            subtotal=Decimal('84.75'),
            tax=Decimal('15.25'),
            total=Decimal('100.00'),
            sunat_status='PENDING'
        )
        db.session.add(sale)
        db.session.flush()
        
        item = SaleItem(
            sale_id=sale.id,
            product_id=1, # Asumiendo que existe
            quantity=1,
            unit_price=Decimal('84.75'),
            subtotal=Decimal('84.75'),
            product_name='Producto Prueba',
            product_sku='PROD-TEST'
        )
        db.session.add(item)
        db.session.commit()

    print(f"Venta seleccionada: {sale.correlative} (ID: {sale.id})")
    print(f"Estado inicial: {sale.sunat_status}")

    # 2. Ejecutar envío a SUNAT (PSEService)
    pse_service = PSEService()
    print("\nEjecutando send_sale_to_sunat...")
    result = pse_service.send_sale_to_sunat(sale.id)

    print("\n--- RESULTADO ---")
    print(f"Éxito: {result['success']}")
    print(f"Mensaje: {result['message']}")
    print(f"Nuevo Estado: {result.get('sunat_status')}")
    
    # Verificar si se generó el XML (aunque sea mock)
    sale_updated = Sale.query.get(sale.id)
    if sale_updated.xml_path:
        print(f"XML generado en: {sale_updated.xml_path}")
        if os.path.exists(sale_updated.xml_path):
            print("CONFIRMADO: El archivo XML existe en el disco.")
        else:
            print("ERROR: La ruta del XML está guardada pero el archivo no existe.")
    
    if result['success'] and result.get('sunat_status') == 'ACCEPTED':
        print("\n✅ PRUEBA EXITOSA: El flujo funciona correctamente en Modo Sandbox.")
    else:
        print("\n❌ PRUEBA FALLIDA.")
