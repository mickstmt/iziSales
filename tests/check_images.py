"""
Script para verificar el estado de las imágenes de productos en la base de datos
"""
import os
import sys

# Añadir el directorio raíz al path para poder importar la app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.product import Product

app = create_app()

with app.app_context():
    print("--- VERIFICANDO IMÁGENES DE PRODUCTOS ---")
    
    total_products = Product.query.count()
    products_with_image = Product.query.filter(Product.image_url != None, Product.image_url != '').count()
    products_without_image = total_products - products_with_image
    
    print(f"Total productos: {total_products}")
    print(f"Productos con imagen: {products_with_image}")
    print(f"Productos sin imagen: {products_without_image}")
    
    if products_without_image > 0:
        print("\nEjemplos de productos sin imagen:")
        no_image_samples = Product.query.filter((Product.image_url == None) | (Product.image_url == '')).limit(5).all()
        for p in no_image_samples:
            print(f"- {p.sku}: {p.name}")
            
    if products_with_image > 0:
        print("\nEjemplos de productos con imagen:")
        image_samples = Product.query.filter(Product.image_url != None, Product.image_url != '').limit(3).all()
        for p in image_samples:
            print(f"- {p.sku}: {p.name} -> {p.image_url}")
