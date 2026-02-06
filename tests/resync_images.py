"""
Script para re-sincronizar imágenes de productos desde WooCommerce
"""
import os
import sys

# Añadir el directorio raíz al path para poder importar la app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.product import Product
from app.services.woocommerce_service import WooCommerceService
from loguru import logger

app = create_app()

def resync_images():
    with app.app_context():
        print("--- INICIANDO RE-SINCRONIZACIÓN DE IMÁGENES ---")
        
        # Obtener productos sin imagen
        products_to_fix = Product.query.filter(
            (Product.image_url == None) | (Product.image_url == '')
        ).all()
        
        if not products_to_fix:
            print("No hay productos sin imagen para sincronizar.")
            return

        print(f"Se encontraron {len(products_to_fix)} productos sin imagen.")
        woo_service = WooCommerceService()
        
        fixed_count = 0
        for product in products_to_fix:
            print(f"Sincronizando: {product.name} (ID Woo: {product.woo_id})...")
            
            try:
                # Obtener datos frescos de WooCommerce
                # Nota: Si es una variación, el ID de Woo es el de la variación
                woo_data = woo_service.get_product(product.woo_id)
                
                if woo_data:
                    # Usar el nuevo método update_from_woo para actualizar imagen
                    product.update_from_woo(woo_data)
                    
                    if product.image_url:
                        print(f"  ✅ Imagen recuperada: {product.image_url[:60]}...")
                        fixed_count += 1
                    else:
                        print("  ⚠️ El producto no tiene imágenes en WooCommerce.")
                else:
                    print(f"  ❌ No se pudo obtener datos de WooCommerce para ID {product.woo_id}")
                    
            except Exception as e:
                print(f"  ❌ Error sincronizando {product.sku}: {str(e)}")
        
        db.session.commit()
        print(f"\n--- SINCRONIZACIÓN FINALIZADA ---")
        print(f"Total procesados: {len(products_to_fix)}")
        print(f"Imágenes recuperadas: {fixed_count}")

if __name__ == "__main__":
    resync_images()
