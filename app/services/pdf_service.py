"""
Servicio de generación de PDF para boletas electrónicas
Genera PDFs con formato oficial SUNAT incluyendo QR code
"""
import os
import qrcode
from decimal import Decimal
from datetime import datetime
from flask import current_app
from loguru import logger

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Table, TableStyle


class PDFService:
    """
    Generador de PDF para boletas electrónicas

    Genera PDFs con:
    - Encabezado con datos de empresa
    - Información del cliente
    - Detalle de items
    - Totales (subtotal, IGV, total)
    - QR code SUNAT
    - Leyendas legales
    """

    # Códigos de tipo de documento para QR
    DOCUMENT_TYPE_CODES = {
        'DNI': '1',
        'RUC': '6',
        'CE': '4',
        'PASAPORTE': '7',
        'OTRO': '-'
    }

    def __init__(self):
        """Inicializar servicio con configuración de empresa"""
        self.company_ruc = current_app.config.get('COMPANY_RUC')
        self.company_name = current_app.config.get('COMPANY_NAME')
        self.company_address = current_app.config.get('COMPANY_ADDRESS')

    def generate_invoice_pdf(self, sale) -> str:
        """
        Generar PDF completo de boleta

        Args:
            sale: Objeto Sale con todos los datos

        Returns:
            str: Ruta del PDF generado
        """
        try:
            logger.info(f"Generando PDF para boleta {sale.correlative}")

            # Crear directorio si no existe
            pdf_dir = current_app.config.get('PDF_PATH')
            os.makedirs(pdf_dir, exist_ok=True)

            # Nombre del archivo
            filename = f"{self.company_ruc}-03-{sale.correlative}.pdf"
            file_path = os.path.join(pdf_dir, filename)

            # Crear canvas
            c = pdf_canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # Generar QR code primero
            qr_path = self._generate_qr_code(sale)

            # Dibujar contenido
            y_position = height - 2 * cm
            y_position = self._draw_header(c, y_position, width)
            y_position = self._draw_document_info(c, y_position, sale)
            y_position = self._draw_customer_info(c, y_position, sale)
            y_position = self._draw_items_table(c, y_position, sale, width)
            y_position = self._draw_totals(c, y_position, sale, width)
            self._draw_footer(c, y_position, sale, qr_path, width)

            # Guardar PDF
            c.save()

            # Actualizar ruta en sale
            sale.pdf_path = file_path

            logger.info(f"PDF generado exitosamente: {filename}")
            return file_path

        except Exception as e:
            logger.error(f"Error generando PDF para venta {sale.id}: {e}")
            raise

    def _generate_qr_code(self, sale) -> str:
        """
        Generar QR code con formato SUNAT

        Formato:
        RUC|TIPO_DOC|SERIE|NUMERO|IGV|TOTAL|FECHA|TIPO_DOC_CLI|NUM_DOC_CLI

        Args:
            sale: Objeto Sale

        Returns:
            str: Ruta del QR generado
        """
        try:
            # Crear directorio para QR
            qr_dir = os.path.join(current_app.config.get('PDF_PATH'), 'qr')
            os.makedirs(qr_dir, exist_ok=True)

            # Extraer serie y número del correlativo
            parts = sale.correlative.split('-')
            serie = parts[0] if len(parts) > 0 else 'B001'
            numero = parts[1] if len(parts) > 1 else '1'

            # Tipo de documento del cliente
            doc_type_code = self.DOCUMENT_TYPE_CODES.get(
                sale.customer.document_type.upper() if sale.customer.document_type else 'OTRO',
                '1'
            )

            # Formatear datos para QR
            qr_data = (
                f"{self.company_ruc}|"
                f"03|"  # Tipo documento: 03 = Boleta
                f"{serie}|"
                f"{numero}|"
                f"{float(sale.tax):.2f}|"
                f"{float(sale.total):.2f}|"
                f"{sale.created_at.strftime('%Y-%m-%d')}|"
                f"{doc_type_code}|"
                f"{sale.customer.document_number or '-'}"
            )

            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")

            # Guardar
            qr_filename = f"QR-{sale.correlative}.png"
            qr_path = os.path.join(qr_dir, qr_filename)
            img.save(qr_path)

            # Guardar datos del QR en la venta
            sale.qr_code = qr_data

            logger.info(f"QR code generado: {qr_filename}")
            return qr_path

        except Exception as e:
            logger.error(f"Error generando QR code: {e}")
            raise

    def _draw_header(self, c, y_pos, width) -> float:
        """
        Dibujar encabezado con datos de empresa

        Args:
            c: Canvas de reportlab
            y_pos: Posición Y actual
            width: Ancho de página

        Returns:
            float: Nueva posición Y
        """
        # Rectángulo para encabezado
        c.setFillColor(colors.HexColor('#f8f9fa'))
        c.rect(2 * cm, y_pos - 3 * cm, width - 4 * cm, 3 * cm, fill=True, stroke=True)

        # Nombre de empresa
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 16)
        c.drawString(2.5 * cm, y_pos - 1 * cm, self.company_name)

        # RUC
        c.setFont('Helvetica', 10)
        c.drawString(2.5 * cm, y_pos - 1.5 * cm, f"RUC: {self.company_ruc}")

        # Dirección
        c.setFont('Helvetica', 9)
        c.drawString(2.5 * cm, y_pos - 2 * cm, self.company_address[:80])

        # Cuadro de tipo de comprobante (derecha)
        box_x = width - 8 * cm
        c.setFillColor(colors.HexColor('#dc3545'))
        c.rect(box_x, y_pos - 2.5 * cm, 5.5 * cm, 2 * cm, fill=True, stroke=True)

        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(box_x + 2.75 * cm, y_pos - 1.2 * cm, "BOLETA DE VENTA")
        c.setFont('Helvetica', 10)
        c.drawCentredString(box_x + 2.75 * cm, y_pos - 1.8 * cm, "ELECTRÓNICA")

        return y_pos - 3.5 * cm

    def _draw_document_info(self, c, y_pos, sale) -> float:
        """
        Dibujar información del documento (correlativo, fecha)

        Args:
            c: Canvas
            y_pos: Posición Y
            sale: Objeto Sale

        Returns:
            float: Nueva posición Y
        """
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 12)
        c.drawString(2 * cm, y_pos, f"Boleta N°: {sale.correlative}")

        c.setFont('Helvetica', 10)
        fecha_emision = sale.created_at.strftime('%d/%m/%Y %H:%M')
        c.drawString(2 * cm, y_pos - 0.6 * cm, f"Fecha de Emisión: {fecha_emision}")

        return y_pos - 1.5 * cm

    def _draw_customer_info(self, c, y_pos, sale) -> float:
        """
        Dibujar información del cliente

        Args:
            c: Canvas
            y_pos: Posición Y
            sale: Objeto Sale

        Returns:
            float: Nueva posición Y
        """
        c.setFont('Helvetica-Bold', 10)
        c.drawString(2 * cm, y_pos, "DATOS DEL CLIENTE")

        c.setFont('Helvetica', 9)
        y_pos -= 0.6 * cm
        c.drawString(2 * cm, y_pos, f"Nombre: {sale.customer.name}")

        y_pos -= 0.5 * cm
        doc_label = sale.customer.document_type or 'Documento'
        doc_number = sale.customer.document_number or '-'
        c.drawString(2 * cm, y_pos, f"{doc_label}: {doc_number}")

        return y_pos - 1 * cm

    def _draw_items_table(self, c, y_pos, sale, width) -> float:
        """
        Dibujar tabla de items

        Args:
            c: Canvas
            y_pos: Posición Y
            sale: Objeto Sale
            width: Ancho de página

        Returns:
            float: Nueva posición Y
        """
        # Encabezados de tabla
        data = [['Item', 'Descripción', 'Cant.', 'P. Unit.', 'Subtotal']]

        # Items
        for index, item in enumerate(sale.items, start=1):
            data.append([
                str(index),
                item.product.name[:40],  # Limitar longitud
                str(int(item.quantity)),
                f"S/ {float(item.price):.2f}",
                f"S/ {float(item.quantity * item.price):.2f}"
            ])

        # Crear tabla
        table = Table(data, colWidths=[1.5 * cm, 9 * cm, 2 * cm, 3 * cm, 3 * cm])

        # Estilo de tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item centrado
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Cantidad centrada
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Precios a la derecha

            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        # Calcular altura de tabla
        table_width, table_height = table.wrap(width, y_pos)

        # Dibujar tabla
        table.drawOn(c, 2 * cm, y_pos - table_height)

        return y_pos - table_height - 1 * cm

    def _draw_totals(self, c, y_pos, sale, width) -> float:
        """
        Dibujar totales (subtotal, IGV, total)

        Args:
            c: Canvas
            y_pos: Posición Y
            sale: Objeto Sale
            width: Ancho de página

        Returns:
            float: Nueva posición Y
        """
        x_label = width - 9 * cm
        x_value = width - 4 * cm

        # Subtotal
        c.setFont('Helvetica', 10)
        c.drawString(x_label, y_pos, "Subtotal:")
        c.drawRightString(x_value, y_pos, f"S/ {float(sale.subtotal):.2f}")

        # IGV 18%
        y_pos -= 0.6 * cm
        c.drawString(x_label, y_pos, "IGV (18%):")
        c.drawRightString(x_value, y_pos, f"S/ {float(sale.tax):.2f}")

        # Línea separadora
        y_pos -= 0.4 * cm
        c.line(x_label, y_pos, x_value, y_pos)

        # Total
        y_pos -= 0.6 * cm
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x_label, y_pos, "TOTAL:")
        c.drawRightString(x_value, y_pos, f"S/ {float(sale.total):.2f}")

        return y_pos - 1 * cm

    def _draw_footer(self, c, y_pos, sale, qr_path, width):
        """
        Dibujar footer con QR y leyendas

        Args:
            c: Canvas
            y_pos: Posición Y
            sale: Objeto Sale
            qr_path: Ruta del QR code
            width: Ancho de página
        """
        # QR code
        if qr_path and os.path.exists(qr_path):
            qr_size = 4 * cm
            qr_x = 2 * cm
            qr_y = 2 * cm
            c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)

        # Leyendas legales
        text_x = 7 * cm
        text_y = 4.5 * cm

        c.setFont('Helvetica', 8)
        c.drawString(text_x, text_y, "Representación impresa de la Boleta de Venta Electrónica")

        text_y -= 0.5 * cm
        c.drawString(text_x, text_y, "Autorizado mediante Resolución de Intendencia SUNAT")

        text_y -= 0.5 * cm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, f"Consulte su comprobante en: {current_app.config.get('COMPANY_WEBSITE', 'www.sunat.gob.pe')}")

        # Hash del documento (si existe)
        if sale.hash:
            text_y -= 0.8 * cm
            c.setFont('Helvetica', 7)
            c.setFillColor(colors.grey)
            c.drawString(text_x, text_y, f"Hash: {sale.hash[:40]}...")

        # Vendedor
        text_y -= 0.5 * cm
        c.setFillColor(colors.black)
        if sale.seller:
            c.drawString(text_x, text_y, f"Atendido por: {sale.seller.username}")
