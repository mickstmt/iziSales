"""
Servicio de integración con WooCommerce
"""
from woocommerce import API
from flask import current_app
from app import db, cache
from app.models.product import Product
from datetime import datetime
from loguru import logger


class WooCommerceService:
    """Servicio para interactuar con la API de WooCommerce"""

    def __init__(self):
        """Inicializar conexión con WooCommerce"""
        self.wcapi = API(
            url=current_app.config['WOO_URL'],
            consumer_key=current_app.config['WOO_CONSUMER_KEY'],
            consumer_secret=current_app.config['WOO_CONSUMER_SECRET'],
            version="wc/v3",
            timeout=30
        )

    def get_products(self, per_page=100, page=1):
        """
        Obtener productos desde WooCommerce

        Args:
            per_page: Productos por página (máx 100)
            page: Número de página

        Returns:
            list: Lista de productos
        """
        try:
            response = self.wcapi.get("products", params={
                "per_page": per_page,
                "page": page,
                "status": "publish"
            })

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error WooCommerce API: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error obteniendo productos: {str(e)}")
            return []

    def search_products(self, query):
        """
        Buscar productos por nombre o SKU

        Args:
            query: Término de búsqueda

        Returns:
            list: Lista de productos que coinciden
        """
        try:
            response = self.wcapi.get("products", params={
                "search": query,
                "per_page": 20,
                "status": "publish"
            })

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except Exception as e:
            logger.error(f"Error buscando productos: {str(e)}")
            return []

    def get_product(self, product_id):
        """
        Obtener un producto específico

        Args:
            product_id: ID del producto en WooCommerce

        Returns:
            dict: Datos del producto
        """
        try:
            response = self.wcapi.get(f"products/{product_id}")

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
            return None

    def sync_products_to_local(self):
        """
        Sincronizar productos de WooCommerce a base de datos local

        Returns:
            int: Cantidad de productos sincronizados
        """
        try:
            page = 1
            total_synced = 0

            while True:
                products = self.get_products(per_page=100, page=page)

                if not products:
                    break

                for woo_product in products:
                    # Buscar o crear producto local
                    product = Product.query.filter_by(
                        woo_product_id=woo_product['id']
                    ).first()

                    if not product:
                        product = Product(woo_product_id=woo_product['id'])

                    # Actualizar datos
                    product.sku = woo_product.get('sku', '')
                    product.name = woo_product['name']
                    product.price = float(woo_product.get('price', 0))
                    product.stock = woo_product.get('stock_quantity', 0)
                    product.description = woo_product.get('description', '')
                    product.image_url = woo_product['images'][0]['src'] if woo_product.get('images') else None
                    product.is_active = woo_product['status'] == 'publish'
                    product.last_sync = datetime.utcnow()

                    db.session.add(product)
                    total_synced += 1

                # Si hay menos de 100 productos, es la última página
                if len(products) < 100:
                    break

                page += 1

            db.session.commit()
            logger.info(f"Sincronizados {total_synced} productos desde WooCommerce")

            # Limpiar cache
            cache.clear()

            return total_synced

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando productos: {str(e)}")
            return 0

    @cache.memoize(timeout=300)  # Cache por 5 minutos
    def get_local_products(self, search=None, limit=50):
        """
        Obtener productos de la base de datos local

        Args:
            search: Término de búsqueda (opcional)
            limit: Límite de resultados

        Returns:
            list: Lista de productos
        """
        query = Product.query.filter_by(is_active=True)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )

        products = query.order_by(Product.name).limit(limit).all()

        return [product.to_dict() for product in products]
