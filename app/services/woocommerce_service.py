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

    def get_product_variations(self, product_id):
        """
        Obtener variaciones de un producto variable

        Args:
            product_id: ID del producto en WooCommerce

        Returns:
            list: Lista de variaciones del producto
        """
        try:
            response = self.wcapi.get(f"products/{product_id}/variations")

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo variaciones del producto {product_id}: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error obteniendo variaciones del producto {product_id}: {str(e)}")
            return []

    def sync_products_to_local(self):
        """
        Sincronizar productos de WooCommerce a base de datos local
        Incluye productos simples y todas las variaciones de productos variables

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
                    product_type = woo_product.get('type', 'simple')

                    # Procesar productos simples normalmente
                    if product_type == 'simple':
                        synced = self._sync_simple_product(woo_product)
                        if synced:
                            total_synced += 1

                    # Procesar productos variables: importar cada variación
                    elif product_type == 'variable':
                        logger.info(f"Producto variable detectado: {woo_product['name']} (ID: {woo_product['id']})")
                        variations = self.get_product_variations(woo_product['id'])

                        if variations:
                            for variation in variations:
                                synced = self._sync_variation_product(woo_product, variation)
                                if synced:
                                    total_synced += 1
                        else:
                            # Si no tiene variaciones, sincronizar el producto padre
                            synced = self._sync_simple_product(woo_product)
                            if synced:
                                total_synced += 1

                # Si hay menos de 100 productos, es la última página
                if len(products) < 100:
                    break

                page += 1

            db.session.commit()
            logger.info(f"Sincronizados {total_synced} productos desde WooCommerce")

            # Limpiar cache (comentado: requiere Redis activo)
            # cache.clear()

            return total_synced

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando productos: {str(e)}")
            return 0

    def _sync_simple_product(self, woo_product):
        """
        Sincronizar un producto simple

        Args:
            woo_product: Datos del producto desde WooCommerce

        Returns:
            bool: True si se sincronizó correctamente
        """
        try:
            # Buscar o crear producto local
            product = Product.query.filter_by(
                woo_id=woo_product['id']
            ).first()

            # Generar SKU: usar el de WooCommerce o generar uno único
            sku = woo_product.get('sku') or f"WOO-{woo_product['id']}"

            if not product:
                product = Product(
                    woo_id=woo_product['id'],
                    sku=sku
                )
            else:
                # Actualizar SKU si estaba vacío
                if not product.sku or product.sku.strip() == '':
                    product.sku = sku

            # Actualizar datos
            product.name = woo_product['name']
            product.price = float(woo_product.get('price') or 0)
            product.stock_quantity = woo_product.get('stock_quantity') or 0
            product.description = woo_product.get('short_description', '')
            product.is_active = woo_product['status'] == 'publish'
            product.last_sync = datetime.utcnow()

            # Extraer URL de la primera imagen
            images = woo_product.get('images', [])
            product.image_url = images[0]['src'] if images else None

            db.session.add(product)
            return True

        except Exception as e:
            logger.error(f"Error sincronizando producto simple {woo_product['id']}: {str(e)}")
            return False

    def _sync_variation_product(self, parent_product, variation):
        """
        Sincronizar una variación de producto como producto independiente

        Args:
            parent_product: Producto padre desde WooCommerce
            variation: Datos de la variación desde WooCommerce

        Returns:
            bool: True si se sincronizó correctamente
        """
        try:
            # Buscar o crear producto local usando el ID de la variación
            product = Product.query.filter_by(
                woo_id=variation['id']
            ).first()

            # Generar SKU: usar el de la variación o generar uno único
            sku = variation.get('sku') or f"WOO-VAR-{variation['id']}"

            # Construir nombre combinando producto padre + atributos de variación
            variation_name = parent_product['name']
            if variation.get('attributes'):
                # Obtener los valores de los atributos (ej: "Negro", "Talla M")
                attr_values = [attr.get('option', '') for attr in variation['attributes'] if attr.get('option')]
                if attr_values:
                    variation_name = f"{parent_product['name']} - {' - '.join(attr_values)}"

            if not product:
                product = Product(
                    woo_id=variation['id'],
                    sku=sku
                )
            else:
                # Actualizar SKU si estaba vacío
                if not product.sku or product.sku.strip() == '':
                    product.sku = sku

            # Actualizar datos de la variación
            product.name = variation_name
            product.price = float(variation.get('price') or 0)
            product.stock_quantity = variation.get('stock_quantity') or 0
            product.description = variation.get('description') or parent_product.get('short_description', '')
            product.is_active = variation.get('status') == 'publish' and parent_product.get('status') == 'publish'
            product.last_sync = datetime.utcnow()

            # Extraer URL de imagen: usar la de la variación o la del producto padre
            variation_image = variation.get('image')
            if variation_image and variation_image.get('src'):
                product.image_url = variation_image['src']
            else:
                parent_images = parent_product.get('images', [])
                product.image_url = parent_images[0]['src'] if parent_images else None

            db.session.add(product)
            return True

        except Exception as e:
            logger.error(f"Error sincronizando variación {variation['id']}: {str(e)}")
            return False

    # @cache.memoize(timeout=300)  # Cache por 5 minutos (comentado: requiere Redis activo)
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
            # Dividir el término de búsqueda en palabras individuales
            words = [word.strip() for word in search.split() if word.strip()]

            if words:
                # Crear filtros para que TODAS las palabras estén presentes
                filters = []
                for word in words:
                    # Detectar si es un número corto (1-3 dígitos)
                    is_short_number = word.isdigit() and len(word) <= 3

                    if is_short_number:
                        # Para números cortos, buscar como palabra completa
                        # Buscar: " 8 " o " 8-" o " 8)" o empieza con "8 " o termina con " 8"
                        word_filter = db.or_(
                            Product.name.ilike(f"% {word} %"),  # " 8 "
                            Product.name.ilike(f"% {word}-%"),   # " 8-"
                            Product.name.ilike(f"% {word})%"),   # " 8)"
                            Product.name.ilike(f"{word} %"),     # "8 " al inicio
                            Product.name.ilike(f"% {word}"),     # " 8" al final
                            Product.sku.ilike(f"%{word}%")       # SKU normal
                        )
                    else:
                        # Para texto normal, buscar como substring (comportamiento original)
                        word_filter = db.or_(
                            Product.name.ilike(f"%{word}%"),
                            Product.sku.ilike(f"%{word}%")
                        )

                    filters.append(word_filter)

                # Aplicar todos los filtros con AND (todas las palabras deben estar presentes)
                if filters:
                    query = query.filter(db.and_(*filters))

        products = query.order_by(Product.name).limit(limit).all()

        return [product.to_dict() for product in products]
