"""
Servicio de Consulta SUNAT API
Consulta datos de RUC y DNI desde APIs externas
"""
import requests
from typing import Optional, Dict
from loguru import logger
import os


class SunatAPIService:
    """
    Servicio para consultar datos de RUC/DNI en SUNAT via APIs externas

    APIs soportadas:
    - api.decolecta.com (configurar DECOLECTA_TOKEN) - Recomendado
    - apis.net.pe (configurar SUNAT_API_TOKEN)
    - apiperu.dev (configurar APIPERU_TOKEN)
    - dniruc.apisperu.com (gratuita, sin token)
    """

    def __init__(self):
        self.api_token = os.getenv('SUNAT_API_TOKEN', '')
        self.apiperu_token = os.getenv('APIPERU_TOKEN', '')
        self.decolecta_token = os.getenv('DECOLECTA_TOKEN', '')
        self.timeout = 10

    def consultar_ruc(self, ruc: str) -> Optional[Dict]:
        """
        Consultar datos de RUC en SUNAT

        Args:
            ruc: Número de RUC (11 dígitos)

        Returns:
            Dict con datos del RUC o None si no se encuentra
            {
                'ruc': '20123456789',
                'razon_social': 'EMPRESA SAC',
                'nombre_comercial': 'EMPRESA',
                'tipo_contribuyente': 'SOCIEDAD ANONIMA CERRADA',
                'estado': 'ACTIVO',
                'condicion': 'HABIDO',
                'direccion': 'AV. PRINCIPAL 123',
                'ubigeo': '150101',
                'departamento': 'LIMA',
                'provincia': 'LIMA',
                'distrito': 'LIMA'
            }
        """
        if not ruc or len(ruc) != 11:
            return None

        try:
            # Solo usar decolecta.com
            if not self.decolecta_token:
                logger.warning("DECOLECTA_TOKEN no configurado")
                return None

            result = self._consultar_decolecta_ruc(ruc)
            if result:
                return result

            logger.warning(f"No se encontró RUC {ruc} en DeColecta")
            return None

        except Exception as e:
            logger.error(f"Error consultando RUC {ruc}: {e}")
            return None

    def consultar_dni(self, dni: str) -> Optional[Dict]:
        """
        Consultar datos de DNI en RENIEC

        Args:
            dni: Número de DNI (8 dígitos)

        Returns:
            Dict con datos del DNI o None si no se encuentra
            {
                'dni': '12345678',
                'nombres': 'JUAN',
                'apellido_paterno': 'PEREZ',
                'apellido_materno': 'GARCIA',
                'nombre_completo': 'PEREZ GARCIA JUAN'
            }
        """
        if not dni or len(dni) != 8:
            return None

        try:
            # Solo usar decolecta.com
            if not self.decolecta_token:
                logger.warning("DECOLECTA_TOKEN no configurado")
                return None

            result = self._consultar_decolecta_dni(dni)
            if result:
                return result

            logger.warning(f"No se encontró DNI {dni} en DeColecta")
            return None

        except Exception as e:
            logger.error(f"Error consultando DNI {dni}: {e}")
            return None

    # ========================================
    # DECOLECTA.COM
    # ========================================

    def _consultar_decolecta_ruc(self, ruc: str) -> Optional[Dict]:
        """Consultar RUC en api.decolecta.com"""
        try:
            url = f"https://api.decolecta.com/v1/sunat/ruc?numero={ruc}"
            headers = {
                'Authorization': f'Bearer {self.decolecta_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            logger.info(f"[DeColecta] Consultando RUC {ruc} en {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout)

            logger.info(f"[DeColecta] Status Code: {response.status_code}")
            logger.info(f"[DeColecta] Response: {response.text}")

            if response.status_code == 200:
                data = response.json()

                # DeColecta puede usar 'ruc' o 'document_number'
                ruc = data.get('ruc') or data.get('document_number')
                if not ruc:
                    logger.warning(f"[DeColecta] Respuesta sin campo 'ruc' o 'document_number': {data}")
                    return None

                # Mapear campos (DeColecta puede usar nombres en inglés o español)
                razon_social = data.get('business_name') or data.get('razonSocial') or data.get('razon_social', '')
                nombre_comercial = data.get('trade_name') or data.get('nombreComercial') or data.get('nombre_comercial', '')
                tipo_contribuyente = data.get('taxpayer_type') or data.get('tipoContribuyente') or data.get('tipo_contribuyente', '')
                estado = data.get('state') or data.get('estado', '')
                condicion = data.get('condition') or data.get('condicion', '')
                direccion = data.get('address') or data.get('direccion', '')
                ubigeo = data.get('ubigeo', '')
                departamento = data.get('department') or data.get('departamento', '')
                provincia = data.get('province') or data.get('provincia', '')
                distrito = data.get('district') or data.get('distrito', '')

                return {
                    'ruc': ruc,
                    'razon_social': razon_social.strip(),
                    'nombre_comercial': nombre_comercial.strip() or razon_social.strip(),
                    'tipo_contribuyente': tipo_contribuyente.strip(),
                    'estado': estado.strip(),
                    'condicion': condicion.strip(),
                    'direccion': direccion.strip(),
                    'ubigeo': ubigeo,
                    'departamento': departamento.strip(),
                    'provincia': provincia.strip(),
                    'distrito': distrito.strip()
                }

            logger.error(f"[DeColecta] Error HTTP {response.status_code}: {response.text}")
            return None

        except Exception as e:
            logger.error(f"[DeColecta] Excepción: {e}")
            return None

    def _consultar_decolecta_dni(self, dni: str) -> Optional[Dict]:
        """Consultar DNI en api.decolecta.com"""
        try:
            url = f"https://api.decolecta.com/v1/reniec/dni?numero={dni}"
            headers = {
                'Authorization': f'Bearer {self.decolecta_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            logger.info(f"[DeColecta] Consultando DNI {dni} en {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout)

            logger.info(f"[DeColecta] Status Code: {response.status_code}")
            logger.info(f"[DeColecta] Response: {response.text}")

            if response.status_code == 200:
                data = response.json()

                # DeColecta usa nombres de campos en inglés
                document_number = data.get('document_number')
                if not document_number:
                    logger.warning(f"[DeColecta] Respuesta sin campo 'document_number': {data}")
                    return None

                # Mapear campos de DeColecta
                first_name = data.get('first_name', '').strip()
                first_last_name = data.get('first_last_name', '').strip()
                second_last_name = data.get('second_last_name', '').strip()
                full_name = data.get('full_name', '').strip()

                return {
                    'dni': document_number,
                    'nombres': first_name,
                    'apellido_paterno': first_last_name,
                    'apellido_materno': second_last_name,
                    'nombre_completo': full_name
                }

            logger.error(f"[DeColecta] Error HTTP {response.status_code}: {response.text}")
            return None

        except Exception as e:
            logger.error(f"[DeColecta] Excepción: {e}")
            return None

    # ========================================
    # APIs.NET.PE
    # ========================================

    def _consultar_apis_net_pe_ruc(self, ruc: str) -> Optional[Dict]:
        """Consultar RUC en apis.net.pe"""
        try:
            url = f"https://api.apis.net.pe/v2/sunat/ruc/full"
            params = {'numero': ruc}
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Accept': 'application/json'
            }

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if not data.get('numeroDocumento'):
                    return None

                return {
                    'ruc': data.get('numeroDocumento'),
                    'razon_social': data.get('razonSocial', '').strip(),
                    'nombre_comercial': data.get('nombreComercial', '').strip(),
                    'tipo_contribuyente': data.get('tipoContribuyente', '').strip(),
                    'estado': data.get('estado', '').strip(),
                    'condicion': data.get('condicion', '').strip(),
                    'direccion': data.get('direccion', '').strip(),
                    'ubigeo': data.get('ubigeo', [''])[0] if isinstance(data.get('ubigeo'), list) else data.get('ubigeo', ''),
                    'departamento': data.get('departamento', '').strip(),
                    'provincia': data.get('provincia', '').strip(),
                    'distrito': data.get('distrito', '').strip()
                }

            return None

        except Exception as e:
            logger.debug(f"Error en apis.net.pe RUC: {e}")
            return None

    def _consultar_apis_net_pe_dni(self, dni: str) -> Optional[Dict]:
        """Consultar DNI en apis.net.pe"""
        try:
            url = f"https://api.apis.net.pe/v2/reniec/dni"
            params = {'numero': dni}
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Accept': 'application/json'
            }

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if not data.get('numeroDocumento'):
                    return None

                nombre_completo = f"{data.get('apellidoPaterno', '')} {data.get('apellidoMaterno', '')} {data.get('nombres', '')}".strip()

                return {
                    'dni': data.get('numeroDocumento'),
                    'nombres': data.get('nombres', '').strip(),
                    'apellido_paterno': data.get('apellidoPaterno', '').strip(),
                    'apellido_materno': data.get('apellidoMaterno', '').strip(),
                    'nombre_completo': nombre_completo
                }

            return None

        except Exception as e:
            logger.debug(f"Error en apis.net.pe DNI: {e}")
            return None

    # ========================================
    # APIPERU.DEV
    # ========================================

    def _consultar_apiperu_ruc(self, ruc: str) -> Optional[Dict]:
        """Consultar RUC en apiperu.dev"""
        try:
            url = f"https://apiperu.dev/api/ruc/{ruc}"
            headers = {
                'Authorization': f'Bearer {self.apiperu_token}',
                'Accept': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json().get('data', {})

                if not data.get('ruc'):
                    return None

                return {
                    'ruc': data.get('ruc'),
                    'razon_social': data.get('nombre_o_razon_social', '').strip(),
                    'nombre_comercial': data.get('nombre_comercial', '').strip() or data.get('nombre_o_razon_social', '').strip(),
                    'tipo_contribuyente': data.get('tipo', '').strip(),
                    'estado': data.get('estado', '').strip(),
                    'condicion': data.get('condicion', '').strip(),
                    'direccion': data.get('direccion', '').strip(),
                    'ubigeo': data.get('ubigeo', ''),
                    'departamento': data.get('departamento', '').strip(),
                    'provincia': data.get('provincia', '').strip(),
                    'distrito': data.get('distrito', '').strip()
                }

            return None

        except Exception as e:
            logger.debug(f"Error en apiperu.dev RUC: {e}")
            return None

    def _consultar_apiperu_dni(self, dni: str) -> Optional[Dict]:
        """Consultar DNI en apiperu.dev"""
        try:
            url = f"https://apiperu.dev/api/dni/{dni}"
            headers = {
                'Authorization': f'Bearer {self.apiperu_token}',
                'Accept': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json().get('data', {})

                if not data.get('numero'):
                    return None

                nombre_completo = f"{data.get('apellido_paterno', '')} {data.get('apellido_materno', '')} {data.get('nombres', '')}".strip()

                return {
                    'dni': data.get('numero'),
                    'nombres': data.get('nombres', '').strip(),
                    'apellido_paterno': data.get('apellido_paterno', '').strip(),
                    'apellido_materno': data.get('apellido_materno', '').strip(),
                    'nombre_completo': nombre_completo
                }

            return None

        except Exception as e:
            logger.debug(f"Error en apiperu.dev DNI: {e}")
            return None

    # ========================================
    # DNIRUC.APISPERU.COM (Gratuita)
    # ========================================

    def _consultar_dniruc_apisperu_ruc(self, ruc: str) -> Optional[Dict]:
        """Consultar RUC en dniruc.apisperu.com (API gratuita)"""
        try:
            url = f"https://dniruc.apisperu.com/api/v1/ruc/{ruc}"

            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if not data.get('ruc'):
                    return None

                return {
                    'ruc': data.get('ruc'),
                    'razon_social': data.get('razonSocial', '').strip(),
                    'nombre_comercial': data.get('nombreComercial', '').strip() or data.get('razonSocial', '').strip(),
                    'tipo_contribuyente': data.get('tipoContribuyente', '').strip(),
                    'estado': data.get('estado', '').strip(),
                    'condicion': data.get('condicion', '').strip(),
                    'direccion': data.get('direccion', '').strip(),
                    'ubigeo': data.get('ubigeo', ''),
                    'departamento': data.get('departamento', '').strip(),
                    'provincia': data.get('provincia', '').strip(),
                    'distrito': data.get('distrito', '').strip()
                }

            return None

        except Exception as e:
            logger.debug(f"Error en dniruc.apisperu.com RUC: {e}")
            return None

    def _consultar_dniruc_apisperu_dni(self, dni: str) -> Optional[Dict]:
        """Consultar DNI en dniruc.apisperu.com (API gratuita)"""
        try:
            url = f"https://dniruc.apisperu.com/api/v1/dni/{dni}"

            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if not data.get('dni'):
                    return None

                nombre_completo = f"{data.get('apellidoPaterno', '')} {data.get('apellidoMaterno', '')} {data.get('nombres', '')}".strip()

                return {
                    'dni': data.get('dni'),
                    'nombres': data.get('nombres', '').strip(),
                    'apellido_paterno': data.get('apellidoPaterno', '').strip(),
                    'apellido_materno': data.get('apellidoMaterno', '').strip(),
                    'nombre_completo': nombre_completo
                }

            return None

        except Exception as e:
            logger.debug(f"Error en dniruc.apisperu.com DNI: {e}")
            return None
