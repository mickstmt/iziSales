"""
Servicio de integración con PSE/SUNAT
Gestiona el envío de comprobantes electrónicos a SUNAT vía Proveedor de Servicios Electrónicos (PSE)
"""
import os
import base64
import hashlib
import requests
from datetime import datetime
from flask import current_app
from loguru import logger

from app import db
from app.models.sale import Sale
from app.models.rus_control import RUSControl
from app.services.xml_builder import XMLBuilder


class PSEService:
    """
    Servicio de integración con PSE para facturación electrónica SUNAT

    Gestiona el ciclo completo:
    1. Generación de XML UBL 2.1
    2. Envío a PSE para firma y transmisión a SUNAT
    3. Recepción y procesamiento de CDR
    4. Actualización de estados
    """

    # Códigos de respuesta SUNAT
    SUNAT_CODES = {
        '2000': ('ACCEPTED', 'Aceptado'),
        '2001': ('ACCEPTED', 'Aceptado con observaciones'),
        '4000': ('REJECTED', 'Error en formato del XML'),
        '4001': ('REJECTED', 'RUC del emisor inválido'),
        '4002': ('REJECTED', 'Documento duplicado'),
        '4003': ('REJECTED', 'Total declarado no coincide'),
        '5000': ('ERROR', 'Servicio SUNAT no disponible'),
        '5001': ('ERROR', 'Timeout en servicio SUNAT'),
        '5002': ('ERROR', 'Error interno de SUNAT'),
    }

    def __init__(self):
        """Inicializar servicio con configuración PSE"""
        self.api_url = current_app.config.get('PSE_API_URL')
        self.token = current_app.config.get('PSE_TOKEN')
        self.sandbox_mode = current_app.config.get('PSE_SANDBOX_MODE', True)
        self.timeout = current_app.config.get('PSE_TIMEOUT', 30)
        self.xml_builder = XMLBuilder()
        self.company_ruc = current_app.config.get('COMPANY_RUC')

    def send_sale_to_sunat(self, sale_id: int) -> dict:
        """
        Enviar boleta a SUNAT vía PSE

        Flujo completo:
        1. Validar venta
        2. Generar XML
        3. Enviar a PSE
        4. Guardar XML
        5. Procesar CDR
        6. Actualizar estado

        Args:
            sale_id: ID de la venta a enviar

        Returns:
            dict: {
                'success': bool,
                'sale_id': int,
                'correlative': str,
                'sunat_status': str,
                'message': str,
                'cdr_path': str (opcional),
                'errors': list (opcional)
            }
        """
        try:
            # Obtener venta
            sale = Sale.query.get(sale_id)
            if not sale:
                return {
                    'success': False,
                    'sale_id': sale_id,
                    'message': 'Venta no encontrada'
                }

            # Validar venta antes de enviar
            is_valid, errors = self._validate_sale_for_sending(sale)
            if not is_valid:
                return {
                    'success': False,
                    'sale_id': sale_id,
                    'correlative': sale.correlative,
                    'message': 'Validación fallida',
                    'errors': errors
                }

            logger.info(f"Iniciando envío de boleta {sale.correlative} a SUNAT")

            # Generar XML UBL 2.1
            xml_content = self._generate_xml_content(sale)

            # Calcular hash del XML
            xml_hash = self._calculate_hash(xml_content)

            # Enviar a PSE
            pse_response = self._send_to_pse_api(xml_content, sale)

            if not pse_response.get('success'):
                # Error en envío a PSE
                self._update_sale_status(sale, 'ERROR', {
                    'message': pse_response.get('message', 'Error desconocido'),
                    'error_code': pse_response.get('error_code')
                })
                db.session.commit()

                return {
                    'success': False,
                    'sale_id': sale_id,
                    'correlative': sale.correlative,
                    'sunat_status': 'ERROR',
                    'message': pse_response.get('message', 'Error al enviar a PSE')
                }

            # Guardar XML localmente
            xml_path = self._save_xml_file(xml_content, sale)
            sale.xml_path = xml_path
            sale.hash = xml_hash

            # Procesar respuesta CDR
            cdr_success = self._process_cdr_response(pse_response.get('cdr', {}), sale)

            # Guardar CDR si existe
            cdr_path = None
            if pse_response.get('cdr') and pse_response['cdr'].get('content'):
                cdr_path = self._save_cdr_file(
                    base64.b64decode(pse_response['cdr']['content']),
                    sale
                )
                sale.cdr_path = cdr_path

            db.session.commit()

            logger.info(
                f"Boleta {sale.correlative} procesada. "
                f"Estado: {sale.sunat_status}"
            )

            return {
                'success': True,
                'sale_id': sale_id,
                'correlative': sale.correlative,
                'sunat_status': sale.sunat_status,
                'message': f'Boleta enviada. Estado: {sale.sunat_status}',
                'cdr_path': cdr_path
            }

        except Exception as e:
            logger.error(f"Error enviando boleta {sale_id} a SUNAT: {e}")
            db.session.rollback()

            # Actualizar estado a ERROR
            try:
                sale = Sale.query.get(sale_id)
                if sale:
                    self._update_sale_status(sale, 'ERROR', {
                        'message': str(e)
                    })
                    db.session.commit()
            except:
                pass

            return {
                'success': False,
                'sale_id': sale_id,
                'message': f'Error inesperado: {str(e)}'
            }

    def check_sunat_status(self, sale_id: int) -> dict:
        """
        Verificar estado actual de envío a SUNAT

        Args:
            sale_id: ID de la venta

        Returns:
            dict: Estado actual con detalles
        """
        try:
            sale = Sale.query.get(sale_id)
            if not sale:
                return {
                    'success': False,
                    'message': 'Venta no encontrada'
                }

            return {
                'success': True,
                'sale_id': sale.id,
                'correlative': sale.correlative,
                'sunat_status': sale.sunat_status,
                'sunat_response': sale.sunat_response,
                'sent_at': sale.sunat_sent_at.isoformat() if sale.sunat_sent_at else None,
                'can_resend': sale.sunat_status in ['ERROR', 'REJECTED'],
                'has_pdf': sale.pdf_path is not None and os.path.exists(sale.pdf_path) if sale.pdf_path else False,
                'has_cdr': sale.cdr_path is not None and os.path.exists(sale.cdr_path) if sale.cdr_path else False
            }

        except Exception as e:
            logger.error(f"Error verificando estado SUNAT de venta {sale_id}: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    def resend_to_sunat(self, sale_id: int) -> dict:
        """
        Reenviar boleta con error o rechazada

        Solo permite reenvío de estados ERROR o REJECTED

        Args:
            sale_id: ID de la venta

        Returns:
            dict: Resultado del reenvío
        """
        try:
            sale = Sale.query.get(sale_id)
            if not sale:
                return {
                    'success': False,
                    'message': 'Venta no encontrada'
                }

            # Verificar que puede reenviarse
            if sale.sunat_status not in ['ERROR', 'REJECTED']:
                return {
                    'success': False,
                    'sale_id': sale_id,
                    'correlative': sale.correlative,
                    'message': f'No se puede reenviar boletas con estado {sale.sunat_status}'
                }

            logger.info(f"Reenviando boleta {sale.correlative} a SUNAT")

            # Resetear estado a PENDING
            sale.sunat_status = 'PENDING'
            sale.sunat_response = None
            sale.sunat_sent_at = None
            db.session.commit()

            # Enviar nuevamente
            return self.send_sale_to_sunat(sale_id)

        except Exception as e:
            logger.error(f"Error reenviando boleta {sale_id}: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    def download_cdr(self, sale_id: int) -> str:
        """
        Descargar CDR desde PSE si no existe localmente

        Args:
            sale_id: ID de la venta

        Returns:
            str: Ruta local del CDR o None si falla
        """
        try:
            sale = Sale.query.get(sale_id)
            if not sale:
                logger.error(f"Venta {sale_id} no encontrada")
                return None

            # Si ya existe localmente, retornar
            if sale.cdr_path and os.path.exists(sale.cdr_path):
                return sale.cdr_path

            # Descargar desde PSE
            logger.info(f"Descargando CDR de boleta {sale.correlative} desde PSE")

            response = requests.get(
                f"{self.api_url}/cdr/{sale.correlative}",
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=self.timeout
            )

            if response.status_code == 200:
                cdr_content = response.content
                cdr_path = self._save_cdr_file(cdr_content, sale)
                sale.cdr_path = cdr_path
                db.session.commit()
                return cdr_path
            else:
                logger.error(f"Error descargando CDR: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error descargando CDR de venta {sale_id}: {e}")
            return None

    # ===================
    # MÉTODOS PRIVADOS
    # ===================

    def _validate_sale_for_sending(self, sale: Sale) -> tuple[bool, list[str]]:
        """
        Validar venta antes de enviar a SUNAT

        Validaciones:
        1. Venta no cancelada
        2. Estado PENDING o ERROR
        3. Tiene items
        4. Cliente válido con documento
        5. NO es RUC 20 (empresas)
        6. Total > 0
        7. No excede límite RUS

        Args:
            sale: Objeto Sale a validar

        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []

        # 1. Venta no cancelada
        if sale.is_cancelled:
            errors.append("Venta cancelada, no se puede enviar")

        # 2. Estado PENDING o ERROR
        if sale.sunat_status not in ['PENDING', 'ERROR']:
            errors.append(f"Estado inválido para envío: {sale.sunat_status}")

        # 3. Tiene items
        if not sale.items or sale.items.count() == 0:
            errors.append("Venta sin items")

        # 4. Cliente válido
        if not sale.customer:
            errors.append("Cliente no encontrado")
        else:
            # Cliente con documento
            if not sale.customer.document_number:
                errors.append("Cliente sin número de documento")

            # 5. No es RUC 20 (empresas)
            if sale.customer.document_type == 'RUC':
                if sale.customer.document_number.startswith('20'):
                    errors.append(
                        "No se puede emitir boleta a empresas (RUC 20). "
                        "RUS solo puede emitir boletas a personas naturales"
                    )

        # 6. Total válido
        if not sale.total or sale.total <= 0:
            errors.append("Total inválido o cero")

        # 7. Límite RUS
        rus_control = RUSControl.get_or_create_current()
        if not rus_control.can_add_amount(sale.total):
            errors.append(
                f"Excede límite RUS mensual. "
                f"Disponible: S/ {rus_control.remaining_amount():.2f}"
            )

        return (len(errors) == 0, errors)

    def _generate_xml_content(self, sale: Sale) -> str:
        """
        Generar contenido XML UBL 2.1

        Args:
            sale: Objeto Sale

        Returns:
            str: XML como string
        """
        return self.xml_builder.build_invoice(sale)

    def _send_to_pse_api(self, xml_content: str, sale: Sale) -> dict:
        """
        Enviar XML a PSE para firma y transmisión a SUNAT

        Args:
            xml_content: XML como string
            sale: Objeto Sale

        Returns:
            dict: Respuesta del PSE
        """
        try:
            # Codificar XML en base64
            xml_base64 = base64.b64encode(xml_content.encode('utf-8')).decode('utf-8')

            # Extraer serie y número del correlativo (B001-00000001)
            parts = sale.correlative.split('-')
            serie = parts[0] if len(parts) > 0 else 'B001'
            numero = parts[1] if len(parts) > 1 else '00000001'

            # Preparar payload
            payload = {
                'xml_content': xml_base64,
                'document_type': '03',  # Boleta
                'serie': serie,
                'numero': numero,
                'correlative': sale.correlative,
                'ruc': self.company_ruc
            }

            logger.info(f"Enviando boleta {sale.correlative} a PSE: {self.api_url}")

            # MODO SANDBOX: No enviar a API real, simular éxito
            if self.sandbox_mode:
                logger.warning(f"MODO SANDBOX ACTIVADO: Simulando éxito para {sale.correlative}")
                return {
                    'success': True,
                    'cdr': {
                        'code': '2000',
                        'description': 'ACEPTADO (SIMULADO - MODO PRUEBA)',
                        'content': base64.b64encode(b'MODO PRUEBA').decode('utf-8')
                    },
                    'sunat_code': '2000',
                    'sunat_message': 'La Boleta ha sido aceptada (MOCK)'
                }

            # Enviar a PSE
            response = requests.post(
                f"{self.api_url}/invoices/send",
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"PSE respondió exitosamente para {sale.correlative}")
                return {
                    'success': True,
                    'cdr': data.get('cdr', {}),
                    'sunat_code': data.get('sunat_code'),
                    'sunat_message': data.get('sunat_message')
                }
            else:
                logger.error(
                    f"PSE error {response.status_code} para {sale.correlative}: "
                    f"{response.text}"
                )
                return {
                    'success': False,
                    'message': f'Error PSE: {response.status_code}',
                    'error_code': response.status_code
                }

        except requests.Timeout:
            logger.error(f"Timeout al enviar {sale.correlative} a PSE")
            return {
                'success': False,
                'message': 'Timeout de conexión con PSE',
                'error_code': 'TIMEOUT'
            }
        except requests.ConnectionError:
            logger.error(f"Error de conexión con PSE para {sale.correlative}")
            return {
                'success': False,
                'message': 'No se pudo conectar con PSE',
                'error_code': 'CONNECTION_ERROR'
            }
        except Exception as e:
            logger.error(f"Error inesperado enviando a PSE: {e}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'UNKNOWN'
            }

    def _save_xml_file(self, xml_content: str, sale: Sale) -> str:
        """
        Guardar XML en storage/xml/

        Args:
            xml_content: XML como string
            sale: Objeto Sale

        Returns:
            str: Ruta relativa del archivo guardado
        """
        try:
            # Directorio de XMLs
            xml_dir = current_app.config.get('XML_PATH')
            os.makedirs(xml_dir, exist_ok=True)

            # Nombre: RUC-03-B001-00000001.xml
            filename = f"{self.company_ruc}-03-{sale.correlative}.xml"
            file_path = os.path.join(xml_dir, filename)

            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            logger.info(f"XML guardado: {filename}")
            return file_path

        except Exception as e:
            logger.error(f"Error guardando XML: {e}")
            raise

    def _process_cdr_response(self, cdr_response: dict, sale: Sale) -> bool:
        """
        Procesar respuesta CDR de SUNAT

        CDR contiene:
        - Código respuesta (2000, 2001, 4xxx, 5xxx)
        - Descripción
        - Hash del documento

        Args:
            cdr_response: Dict con respuesta CDR
            sale: Objeto Sale

        Returns:
            bool: True si procesado exitosamente
        """
        try:
            sunat_code = cdr_response.get('code', '5000')
            sunat_message = cdr_response.get('description', 'Sin respuesta')

            # Determinar estado según código
            status, default_message = self._get_status_from_code(sunat_code)

            # Actualizar estado de la venta
            self._update_sale_status(sale, status, {
                'code': sunat_code,
                'message': sunat_message or default_message
            })

            return status == 'ACCEPTED'

        except Exception as e:
            logger.error(f"Error procesando CDR: {e}")
            return False

    def _save_cdr_file(self, cdr_content: bytes, sale: Sale) -> str:
        """
        Guardar CDR en storage/cdr/

        Args:
            cdr_content: Contenido del CDR (bytes)
            sale: Objeto Sale

        Returns:
            str: Ruta relativa del archivo guardado
        """
        try:
            # Directorio de CDRs
            cdr_dir = current_app.config.get('CDR_PATH')
            os.makedirs(cdr_dir, exist_ok=True)

            # Nombre: R-RUC-03-B001-00000001.zip
            filename = f"R-{self.company_ruc}-03-{sale.correlative}.zip"
            file_path = os.path.join(cdr_dir, filename)

            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(cdr_content)

            logger.info(f"CDR guardado: {filename}")
            return file_path

        except Exception as e:
            logger.error(f"Error guardando CDR: {e}")
            raise

    def _update_sale_status(self, sale: Sale, status: str, response: dict):
        """
        Actualizar estado SUNAT de la venta

        Args:
            sale: Objeto Sale
            status: Nuevo estado (PENDING|ACCEPTED|REJECTED|ERROR)
            response: Dict con información de respuesta
        """
        sale.sunat_status = status
        sale.sunat_response = f"{response.get('code', 'N/A')}: {response.get('message', 'Sin mensaje')}"
        sale.sunat_sent_at = datetime.utcnow()

        logger.info(
            f"Estado actualizado para {sale.correlative}: "
            f"{status} - {sale.sunat_response}"
        )

    def _calculate_hash(self, xml_content: str) -> str:
        """
        Calcular hash SHA-256 del XML

        Args:
            xml_content: XML como string

        Returns:
            str: Hash en hexadecimal
        """
        return hashlib.sha256(xml_content.encode('utf-8')).hexdigest()

    def _get_status_from_code(self, code: str) -> tuple[str, str]:
        """
        Obtener estado y mensaje desde código SUNAT

        Args:
            code: Código de respuesta SUNAT

        Returns:
            tuple: (status, message)
        """
        return self.SUNAT_CODES.get(
            code,
            ('ERROR', f'Código desconocido: {code}')
        )
