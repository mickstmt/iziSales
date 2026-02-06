"""
Tareas asíncronas para SUNAT con Celery

Tareas para envío de comprobantes a SUNAT sin bloquear el POS
"""
from celery import shared_task
from datetime import datetime, timedelta
from loguru import logger

from app import create_app, db
from app.models.sale import Sale
from app.services.pse_service import PSEService
from app.services.pdf_service import PDFService


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_sale_to_sunat_async(self, sale_id):
    """
    Tarea asíncrona: Enviar boleta a SUNAT

    Ventajas:
    - No bloquea la interfaz del POS
    - Reintentos automáticos (3 veces, cada 5 minutos)
    - Si es ACCEPTED → genera PDF automáticamente
    - Usuario puede continuar trabajando mientras se envía

    Args:
        sale_id: ID de la venta a enviar

    Returns:
        dict: Resultado del envío
    """
    app = create_app()

    with app.app_context():
        try:
            logger.info(f"[Celery] Iniciando envío asíncrono de venta {sale_id} a SUNAT")

            # Enviar a SUNAT
            pse_service = PSEService()
            result = pse_service.send_sale_to_sunat(sale_id)

            if not result['success']:
                error_message = result.get('message', 'Error desconocido')
                sunat_status = result.get('sunat_status', 'ERROR')

                # Si es error temporal (timeout, servicio no disponible), reintentar
                if sunat_status == 'ERROR' or 'TIMEOUT' in error_message.upper():
                    logger.warning(
                        f"[Celery] Error temporal en venta {sale_id}, "
                        f"reintentando ({self.request.retries + 1}/3)..."
                    )
                    raise self.retry(exc=Exception(error_message))
                else:
                    # Error permanente (validación, rechazado)
                    logger.error(
                        f"[Celery] Error permanente en venta {sale_id}: {error_message}"
                    )
                    return result

            # Si fue aceptado, generar PDF
            if result.get('sunat_status') == 'ACCEPTED':
                logger.info(f"[Celery] Boleta {sale_id} aceptada, generando PDF...")
                try:
                    sale = Sale.query.get(sale_id)
                    if sale:
                        pdf_service = PDFService()
                        pdf_path = pdf_service.generate_invoice_pdf(sale)
                        sale.pdf_path = pdf_path
                        db.session.commit()
                        logger.info(f"[Celery] PDF generado para venta {sale_id}: {pdf_path}")
                except Exception as pdf_error:
                    logger.error(f"[Celery] Error generando PDF para venta {sale_id}: {pdf_error}")
                    # No fallar la tarea si solo el PDF falla

            logger.info(
                f"[Celery] Venta {sale_id} procesada exitosamente. "
                f"Estado: {result.get('sunat_status')}"
            )
            return result

        except Exception as e:
            logger.error(f"[Celery] Error procesando venta {sale_id}: {e}")

            # Actualizar estado a ERROR en la base de datos
            try:
                sale = Sale.query.get(sale_id)
                if sale and sale.sunat_status != 'ERROR':
                    sale.sunat_status = 'ERROR'
                    sale.sunat_response = f'Error Celery: {str(e)}'
                    sale.sunat_sent_at = datetime.utcnow()
                    db.session.commit()
            except Exception as db_error:
                logger.error(f"[Celery] Error actualizando estado de venta {sale_id}: {db_error}")

            # Propagar excepción para que Celery maneje reintentos
            raise


@shared_task
def retry_failed_sales():
    """
    Tarea periódica: Reintentar ventas con error

    Ejecutar cada 30 minutos vía Celery Beat

    Criterios de selección:
    - sunat_status == ERROR
    - sunat_sent_at > 1 hora atrás (evitar reintentar inmediatamente)
    - is_cancelled == False
    - Límite: 50 ventas por ejecución (evitar sobrecarga)

    Returns:
        dict: Estadísticas de reintentos
    """
    app = create_app()

    with app.app_context():
        try:
            logger.info("[Celery] Iniciando tarea de reintentos automáticos")

            # Buscar ventas con error hace más de 1 hora
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            failed_sales = Sale.query.filter(
                Sale.sunat_status == 'ERROR',
                Sale.sunat_sent_at < one_hour_ago,
                Sale.is_cancelled == False
            ).limit(50).all()

            if not failed_sales:
                logger.info("[Celery] No hay ventas con error para reintentar")
                return {
                    'success': True,
                    'total_retried': 0,
                    'message': 'No hay ventas pendientes'
                }

            logger.info(f"[Celery] Se reintentarán {len(failed_sales)} ventas con error")

            # Lanzar tarea asíncrona para cada venta
            retried_count = 0
            for sale in failed_sales:
                try:
                    send_sale_to_sunat_async.delay(sale.id)
                    retried_count += 1
                    logger.info(f"[Celery] Tarea de reintento lanzada para venta {sale.id}")
                except Exception as e:
                    logger.error(f"[Celery] Error lanzando reintento para venta {sale.id}: {e}")

            logger.info(f"[Celery] {retried_count} tareas de reintento lanzadas exitosamente")

            return {
                'success': True,
                'total_retried': retried_count,
                'message': f'Se lanzaron {retried_count} reintentos'
            }

        except Exception as e:
            logger.error(f"[Celery] Error en tarea de reintentos: {e}")
            return {
                'success': False,
                'error': str(e)
            }


@shared_task
def generate_daily_report():
    """
    Tarea periódica: Generar reporte diario de envíos SUNAT

    Ejecutar a las 23:00 todos los días vía Celery Beat

    Estadísticas:
    - Total de boletas emitidas hoy
    - Aceptadas por SUNAT
    - Rechazadas
    - Con error
    - Pendientes de envío

    Returns:
        dict: Reporte con estadísticas del día
    """
    app = create_app()

    with app.app_context():
        try:
            logger.info("[Celery] Generando reporte diario de SUNAT")

            # Obtener ventas del día actual
            today = datetime.utcnow().date()

            sales = Sale.query.filter(
                db.func.date(Sale.created_at) == today,
                Sale.is_cancelled == False
            ).all()

            # Calcular estadísticas
            total = len(sales)
            accepted = len([s for s in sales if s.sunat_status == 'ACCEPTED'])
            rejected = len([s for s in sales if s.sunat_status == 'REJECTED'])
            error = len([s for s in sales if s.sunat_status == 'ERROR'])
            pending = len([s for s in sales if s.sunat_status == 'PENDING'])

            # Calcular porcentaje de éxito
            success_rate = (accepted / total * 100) if total > 0 else 0

            # Calcular total facturado (solo aceptadas)
            total_facturado = sum(
                float(s.total) for s in sales
                if s.sunat_status == 'ACCEPTED'
            )

            report = {
                'date': today.isoformat(),
                'total': total,
                'accepted': accepted,
                'rejected': rejected,
                'error': error,
                'pending': pending,
                'success_rate': round(success_rate, 2),
                'total_facturado': round(total_facturado, 2)
            }

            logger.info(f"[Celery] Reporte diario SUNAT: {report}")

            # TODO: Opcional - Enviar reporte por email a administradores
            # from app.services.email_service import EmailService
            # email_service = EmailService()
            # email_service.send_daily_sunat_report(report)

            return {
                'success': True,
                'report': report
            }

        except Exception as e:
            logger.error(f"[Celery] Error generando reporte diario: {e}")
            return {
                'success': False,
                'error': str(e)
            }


@shared_task
def cleanup_old_files():
    """
    Tarea periódica: Limpiar archivos antiguos (opcional)

    Ejecutar semanalmente para liberar espacio en disco

    Limpia:
    - XMLs de más de 6 meses
    - CDRs de más de 6 meses
    - QR codes de más de 6 meses
    - PDFs de ventas canceladas de más de 3 meses

    Returns:
        dict: Estadísticas de limpieza
    """
    app = create_app()

    with app.app_context():
        try:
            import os
            from pathlib import Path

            logger.info("[Celery] Iniciando limpieza de archivos antiguos")

            xml_dir = Path(app.config.get('XML_PATH'))
            cdr_dir = Path(app.config.get('CDR_PATH'))
            pdf_dir = Path(app.config.get('PDF_PATH'))
            qr_dir = pdf_dir / 'qr'

            six_months_ago = datetime.utcnow() - timedelta(days=180)
            three_months_ago = datetime.utcnow() - timedelta(days=90)

            cleaned_files = 0

            # Limpiar XMLs antiguos
            if xml_dir.exists():
                for xml_file in xml_dir.glob('*.xml'):
                    if datetime.fromtimestamp(xml_file.stat().st_mtime) < six_months_ago:
                        xml_file.unlink()
                        cleaned_files += 1

            # Limpiar CDRs antiguos
            if cdr_dir.exists():
                for cdr_file in cdr_dir.glob('*.zip'):
                    if datetime.fromtimestamp(cdr_file.stat().st_mtime) < six_months_ago:
                        cdr_file.unlink()
                        cleaned_files += 1

            # Limpiar QR codes antiguos
            if qr_dir.exists():
                for qr_file in qr_dir.glob('*.png'):
                    if datetime.fromtimestamp(qr_file.stat().st_mtime) < six_months_ago:
                        qr_file.unlink()
                        cleaned_files += 1

            # Limpiar PDFs de ventas canceladas
            cancelled_sales = Sale.query.filter(
                Sale.is_cancelled == True,
                Sale.created_at < three_months_ago,
                Sale.pdf_path.isnot(None)
            ).all()

            for sale in cancelled_sales:
                if sale.pdf_path and os.path.exists(sale.pdf_path):
                    os.unlink(sale.pdf_path)
                    sale.pdf_path = None
                    cleaned_files += 1

            db.session.commit()

            logger.info(f"[Celery] Limpieza completada: {cleaned_files} archivos eliminados")

            return {
                'success': True,
                'files_cleaned': cleaned_files
            }

        except Exception as e:
            logger.error(f"[Celery] Error en limpieza de archivos: {e}")
            return {
                'success': False,
                'error': str(e)
            }
