"""
Servicio de generación de XML UBL 2.1 para SUNAT
Genera archivos XML compatibles con la especificación SUNAT para boletas electrónicas
"""
from lxml import etree
from decimal import Decimal
from datetime import datetime
from flask import current_app
from loguru import logger


class XMLBuilder:
    """
    Constructor de XML UBL 2.1 para boletas electrónicas SUNAT

    Genera XML según especificación UBL 2.1 de OASIS para el estándar peruano
    """

    # Namespaces UBL 2.1
    NAMESPACES = {
        None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        'ds': "http://www.w3.org/2000/09/xmldsig#",
        'ext': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    }

    # Códigos de tipo de documento SUNAT
    DOCUMENT_TYPE_CODES = {
        'DNI': '1',
        'RUC': '6',
        'CE': '4',
        'PASAPORTE': '7',
        'OTRO': '-'
    }

    def __init__(self):
        """Inicializar builder con configuración de la empresa"""
        self.company_ruc = current_app.config.get('COMPANY_RUC')
        self.company_name = current_app.config.get('COMPANY_NAME')
        self.company_address = current_app.config.get('COMPANY_ADDRESS')
        self.company_ubigeo = current_app.config.get('COMPANY_UBIGEO', '150101')

    def build_invoice(self, sale) -> str:
        """
        Construir XML UBL 2.1 completo para una boleta

        Args:
            sale: Objeto Sale con todos los datos de la venta

        Returns:
            str: XML formateado como string
        """
        try:
            # Crear elemento raíz Invoice
            root = etree.Element(
                'Invoice',
                nsmap=self.NAMESPACES
            )

            # Construir secciones del XML
            self._build_header(root, sale)
            self._build_signature_placeholder(root)
            self._build_supplier(root)
            self._build_customer(root, sale.customer)
            self._build_tax_totals(root, sale)
            self._build_monetary_totals(root, sale)
            self._build_invoice_lines(root, sale)

            # Convertir a string con formato
            xml_string = etree.tostring(
                root,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            ).decode('utf-8')

            logger.info(f"XML generado exitosamente para venta {sale.correlative}")
            return xml_string

        except Exception as e:
            logger.error(f"Error generando XML para venta {sale.id}: {e}")
            raise

    def _build_header(self, root, sale):
        """
        Construir encabezado del documento

        Incluye: versión UBL, ID, fecha, tipo documento, moneda
        """
        cbc = self.NAMESPACES['cbc']

        # Versión UBL
        etree.SubElement(root, f'{{{cbc}}}UBLVersionID').text = '2.1'
        etree.SubElement(root, f'{{{cbc}}}CustomizationID').text = '2.0'

        # Correlativo de la boleta (B001-00000001)
        etree.SubElement(root, f'{{{cbc}}}ID').text = sale.correlative

        # Fecha y hora de emisión
        issue_datetime = sale.created_at if sale.created_at else datetime.utcnow()
        etree.SubElement(root, f'{{{cbc}}}IssueDate').text = issue_datetime.strftime('%Y-%m-%d')
        etree.SubElement(root, f'{{{cbc}}}IssueTime').text = issue_datetime.strftime('%H:%M:%S')

        # Tipo de documento: 03 = Boleta
        etree.SubElement(
            root,
            f'{{{cbc}}}InvoiceTypeCode',
            listID='0101'
        ).text = '03'

        # Moneda: PEN = Soles
        etree.SubElement(root, f'{{{cbc}}}DocumentCurrencyCode').text = 'PEN'

    def _build_signature_placeholder(self, root):
        """
        Construir placeholder para firma digital

        La firma digital real será agregada por el PSE
        """
        cac = self.NAMESPACES['cac']
        cbc = self.NAMESPACES['cbc']

        signature = etree.SubElement(root, f'{{{cac}}}Signature')
        etree.SubElement(signature, f'{{{cbc}}}ID').text = 'SignatureSP'

        signatory_party = etree.SubElement(signature, f'{{{cac}}}SignatoryParty')
        party_identification = etree.SubElement(signatory_party, f'{{{cac}}}PartyIdentification')
        etree.SubElement(party_identification, f'{{{cbc}}}ID').text = self.company_ruc

        party_name = etree.SubElement(signatory_party, f'{{{cac}}}PartyName')
        etree.SubElement(party_name, f'{{{cbc}}}Name').text = self.company_name

        digital_signature = etree.SubElement(signature, f'{{{cac}}}DigitalSignatureAttachment')
        external_reference = etree.SubElement(digital_signature, f'{{{cac}}}ExternalReference')
        etree.SubElement(external_reference, f'{{{cbc}}}URI').text = f'#SignatureSP'

    def _build_supplier(self, root):
        """
        Construir datos del emisor (nuestra empresa)

        Incluye: RUC, nombre comercial, razón social, dirección
        """
        cac = self.NAMESPACES['cac']
        cbc = self.NAMESPACES['cbc']

        supplier = etree.SubElement(root, f'{{{cac}}}AccountingSupplierParty')
        party = etree.SubElement(supplier, f'{{{cac}}}Party')

        # RUC de la empresa
        party_identification = etree.SubElement(party, f'{{{cac}}}PartyIdentification')
        etree.SubElement(
            party_identification,
            f'{{{cbc}}}ID',
            schemeID='6'  # 6 = RUC
        ).text = self.company_ruc

        # Nombre comercial
        party_name = etree.SubElement(party, f'{{{cac}}}PartyName')
        etree.SubElement(party_name, f'{{{cbc}}}Name').text = self.company_name

        # Datos legales
        party_legal = etree.SubElement(party, f'{{{cac}}}PartyLegalEntity')
        etree.SubElement(party_legal, f'{{{cbc}}}RegistrationName').text = self.company_name

        # Dirección
        address = etree.SubElement(party_legal, f'{{{cac}}}RegistrationAddress')
        etree.SubElement(address, f'{{{cbc}}}AddressTypeCode').text = '0000'

        # Ubigeo (código de ubicación geográfica)
        etree.SubElement(address, f'{{{cbc}}}ID').text = self.company_ubigeo

        # Dirección textual
        address_line = etree.SubElement(address, f'{{{cac}}}AddressLine')
        etree.SubElement(address_line, f'{{{cbc}}}Line').text = self.company_address

        # País
        country = etree.SubElement(address, f'{{{cac}}}Country')
        etree.SubElement(country, f'{{{cbc}}}IdentificationCode').text = 'PE'

    def _build_customer(self, root, customer):
        """
        Construir datos del cliente

        Args:
            customer: Objeto Customer con datos del cliente
        """
        cac = self.NAMESPACES['cac']
        cbc = self.NAMESPACES['cbc']

        customer_party = etree.SubElement(root, f'{{{cac}}}AccountingCustomerParty')
        party = etree.SubElement(customer_party, f'{{{cac}}}Party')

        # Tipo y número de documento del cliente
        party_identification = etree.SubElement(party, f'{{{cac}}}PartyIdentification')

        # Obtener código de tipo de documento
        doc_type_code = self.DOCUMENT_TYPE_CODES.get(
            customer.document_type.upper(),
            '1'  # Default: DNI
        )

        etree.SubElement(
            party_identification,
            f'{{{cbc}}}ID',
            schemeID=doc_type_code
        ).text = customer.document_number or '-'

        # Nombre del cliente
        party_legal = etree.SubElement(party, f'{{{cac}}}PartyLegalEntity')
        etree.SubElement(party_legal, f'{{{cbc}}}RegistrationName').text = customer.name

    def _build_tax_totals(self, root, sale):
        """
        Construir totales de impuestos (IGV 18%)

        Args:
            sale: Objeto Sale con datos de la venta
        """
        cac = self.NAMESPACES['cac']
        cbc = self.NAMESPACES['cbc']

        tax_total = etree.SubElement(root, f'{{{cac}}}TaxTotal')

        # Monto total de IGV
        etree.SubElement(
            tax_total,
            f'{{{cbc}}}TaxAmount',
            currencyID='PEN'
        ).text = self._format_decimal(sale.tax)

        # Detalle del impuesto
        tax_subtotal = etree.SubElement(tax_total, f'{{{cac}}}TaxSubtotal')

        # Base imponible (subtotal sin IGV)
        etree.SubElement(
            tax_subtotal,
            f'{{{cbc}}}TaxableAmount',
            currencyID='PEN'
        ).text = self._format_decimal(sale.subtotal)

        # Monto del IGV
        etree.SubElement(
            tax_subtotal,
            f'{{{cbc}}}TaxAmount',
            currencyID='PEN'
        ).text = self._format_decimal(sale.tax)

        # Categoría del impuesto
        tax_category = etree.SubElement(tax_subtotal, f'{{{cac}}}TaxCategory')
        etree.SubElement(
            tax_category,
            f'{{{cbc}}}ID',
            schemeID='UN/ECE 5305',
            schemeName='Tax Category Identifier'
        ).text = 'S'  # S = Gravado

        # Esquema del impuesto (IGV)
        tax_scheme = etree.SubElement(tax_category, f'{{{cac}}}TaxScheme')
        etree.SubElement(
            tax_scheme,
            f'{{{cbc}}}ID',
            schemeID='UN/ECE 5153',
            schemeName='Tax Scheme Identifier'
        ).text = '1000'  # 1000 = IGV
        etree.SubElement(tax_scheme, f'{{{cbc}}}Name').text = 'IGV'
        etree.SubElement(tax_scheme, f'{{{cbc}}}TaxTypeCode').text = 'VAT'

    def _build_monetary_totals(self, root, sale):
        """
        Construir totales monetarios del documento

        Args:
            sale: Objeto Sale con datos de la venta
        """
        cac = self.NAMESPACES['cac']
        cbc = self.NAMESPACES['cbc']

        legal_monetary = etree.SubElement(root, f'{{{cac}}}LegalMonetaryTotal')

        # Subtotal (sin IGV)
        etree.SubElement(
            legal_monetary,
            f'{{{cbc}}}LineExtensionAmount',
            currencyID='PEN'
        ).text = self._format_decimal(sale.subtotal)

        # Total con impuestos
        etree.SubElement(
            legal_monetary,
            f'{{{cbc}}}TaxInclusiveAmount',
            currencyID='PEN'
        ).text = self._format_decimal(sale.total)

        # Monto total a pagar
        etree.SubElement(
            legal_monetary,
            f'{{{cbc}}}PayableAmount',
            currencyID='PEN'
        ).text = self._format_decimal(sale.total)

    def _build_invoice_lines(self, root, sale):
        """
        Construir líneas de items de la venta

        Args:
            sale: Objeto Sale con items (sale.items)
        """
        cac = self.NAMESPACES['cac']
        cbc = self.NAMESPACES['cbc']

        for index, item in enumerate(sale.items, start=1):
            invoice_line = etree.SubElement(root, f'{{{cac}}}InvoiceLine')

            # Número de línea
            etree.SubElement(invoice_line, f'{{{cbc}}}ID').text = str(index)

            # Cantidad
            etree.SubElement(
                invoice_line,
                f'{{{cbc}}}InvoicedQuantity',
                unitCode='NIU'  # NIU = Unidad
            ).text = self._format_decimal(item.quantity, 0)

            # Subtotal de la línea (cantidad × precio unitario sin IGV)
            line_subtotal = Decimal(str(item.quantity)) * Decimal(str(item.unit_price))
            etree.SubElement(
                invoice_line,
                f'{{{cbc}}}LineExtensionAmount',
                currencyID='PEN'
            ).text = self._format_decimal(line_subtotal)

            # Precio de referencia (precio con IGV)
            pricing_reference = etree.SubElement(invoice_line, f'{{{cac}}}PricingReference')
            alt_condition = etree.SubElement(pricing_reference, f'{{{cac}}}AlternativeConditionPrice')
            price_with_tax = Decimal(str(item.unit_price)) * Decimal('1.18')
            etree.SubElement(
                alt_condition,
                f'{{{cbc}}}PriceAmount',
                currencyID='PEN'
            ).text = self._format_decimal(price_with_tax)
            etree.SubElement(alt_condition, f'{{{cbc}}}PriceTypeCode').text = '01'  # 01 = Precio unitario

            # IGV del item
            item_tax_total = etree.SubElement(invoice_line, f'{{{cac}}}TaxTotal')
            item_tax_amount = line_subtotal * Decimal('0.18')
            etree.SubElement(
                item_tax_total,
                f'{{{cbc}}}TaxAmount',
                currencyID='PEN'
            ).text = self._format_decimal(item_tax_amount)

            # Detalle del impuesto del item
            item_tax_subtotal = etree.SubElement(item_tax_total, f'{{{cac}}}TaxSubtotal')
            etree.SubElement(
                item_tax_subtotal,
                f'{{{cbc}}}TaxableAmount',
                currencyID='PEN'
            ).text = self._format_decimal(line_subtotal)
            etree.SubElement(
                item_tax_subtotal,
                f'{{{cbc}}}TaxAmount',
                currencyID='PEN'
            ).text = self._format_decimal(item_tax_amount)

            item_tax_category = etree.SubElement(item_tax_subtotal, f'{{{cac}}}TaxCategory')
            etree.SubElement(item_tax_category, f'{{{cbc}}}Percent').text = '18'
            etree.SubElement(item_tax_category, f'{{{cbc}}}TaxExemptionReasonCode').text = '10'  # 10 = Gravado

            item_tax_scheme = etree.SubElement(item_tax_category, f'{{{cac}}}TaxScheme')
            etree.SubElement(item_tax_scheme, f'{{{cbc}}}ID').text = '1000'
            etree.SubElement(item_tax_scheme, f'{{{cbc}}}Name').text = 'IGV'
            etree.SubElement(item_tax_scheme, f'{{{cbc}}}TaxTypeCode').text = 'VAT'

            # Información del producto
            item_element = etree.SubElement(invoice_line, f'{{{cac}}}Item')
            etree.SubElement(item_element, f'{{{cbc}}}Description').text = item.product_name

            # Código del producto (SKU)
            sellers_item = etree.SubElement(item_element, f'{{{cac}}}SellersItemIdentification')
            etree.SubElement(sellers_item, f'{{{cbc}}}ID').text = item.product_sku

            # Precio unitario sin IGV
            price = etree.SubElement(invoice_line, f'{{{cac}}}Price')
            etree.SubElement(
                price,
                f'{{{cbc}}}PriceAmount',
                currencyID='PEN'
            ).text = self._format_decimal(item.unit_price)

    def _format_decimal(self, value, decimals=2) -> str:
        """
        Formatear valor decimal para XML

        Args:
            value: Valor a formatear (puede ser Decimal, float, int)
            decimals: Número de decimales (default: 2)

        Returns:
            str: Valor formateado
        """
        if value is None:
            value = 0

        decimal_value = Decimal(str(value))
        format_string = f'%.{decimals}f'
        return format_string % decimal_value

    def validate_xml(self, xml_string: str) -> tuple[bool, list[str]]:
        """
        Validar estructura básica del XML generado

        Args:
            xml_string: XML como string

        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []

        try:
            # Parsear XML
            root = etree.fromstring(xml_string.encode('utf-8'))

            # Validaciones básicas
            if root.tag != '{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice':
                errors.append("Elemento raíz no es Invoice")

            # Verificar elementos requeridos
            cbc = self.NAMESPACES['cbc']
            required_elements = ['UBLVersionID', 'ID', 'IssueDate', 'InvoiceTypeCode']

            for element_name in required_elements:
                if root.find(f'.//{{{cbc}}}{element_name}') is None:
                    errors.append(f"Elemento requerido faltante: {element_name}")

            return (len(errors) == 0, errors)

        except etree.XMLSyntaxError as e:
            errors.append(f"Error de sintaxis XML: {str(e)}")
            return (False, errors)
        except Exception as e:
            errors.append(f"Error validando XML: {str(e)}")
            return (False, errors)
