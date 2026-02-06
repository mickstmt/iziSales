"""
Configuración de Celery Beat para tareas periódicas

Define el schedule para tareas que se ejecutan automáticamente
"""
from celery.schedules import crontab


# Configuración de tareas periódicas
beat_schedule = {
    # Reintentar ventas con error cada 30 minutos
    'retry-failed-sales-every-30min': {
        'task': 'app.tasks.sunat_tasks.retry_failed_sales',
        'schedule': crontab(minute='*/30'),  # Cada 30 minutos
        'options': {
            'expires': 60 * 25,  # La tarea expira en 25 minutos
        }
    },

    # Generar reporte diario de SUNAT a las 23:00
    'generate-daily-sunat-report': {
        'task': 'app.tasks.sunat_tasks.generate_daily_report',
        'schedule': crontab(hour=23, minute=0),  # 23:00 todos los días
        'options': {
            'expires': 60 * 30,  # La tarea expira en 30 minutos
        }
    },

    # Limpiar archivos antiguos todos los domingos a las 02:00
    'cleanup-old-files-weekly': {
        'task': 'app.tasks.sunat_tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Domingos 02:00
        'options': {
            'expires': 60 * 60 * 2,  # La tarea expira en 2 horas
        }
    },
}


# Configuración de timezone
timezone = 'America/Lima'


# Configuración de resultados
result_expires = 3600  # Resultados expiran en 1 hora


# Configuración de serialización
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
