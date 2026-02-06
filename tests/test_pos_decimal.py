
from decimal import Decimal
from app import db, create_app
from app.models.rus_control import RUSControl

app = create_app()
with app.app_context():
    print("Iniciando prueba de cálculo Decimal en RUSControl...")
    
    # Obtener control actual
    rus = RUSControl.get_or_create_current()
    original_total = rus.total_invoiced
    print(f"Total actual: {original_total} (Tipo: {type(original_total)})")
    
    # Monto de prueba como float (simulando entrada de frontend)
    test_amount_float = 100.50
    
    try:
        print(f"Intentando actualizar con: {test_amount_float} (float)")
        rus.update_total(test_amount_float)
        new_total = rus.total_invoiced
        print(f"Nuevo total: {new_total} (Tipo: {type(new_total)})")
        
        if new_total == original_total + Decimal(str(test_amount_float)):
            print("SUCCESS: La actualización funcionó correctamente con float.")
        else:
            print("FAILURE: El total no coincide.")
            
        # Probar can_add_amount
        can_add = rus.can_add_amount(50.25)
        print(f"¿Puede agregar 50.25?: {can_add}")
        
        # Revertir cambio para no ensuciar la data real
        rus.total_invoiced -= Decimal(str(test_amount_float))
        rus.transaction_count -= 1
        db.session.commit()
        print("Cambio de prueba revertido.")
        
    except Exception as e:
        print(f"ERROR durante la prueba: {e}")
        db.session.rollback()
