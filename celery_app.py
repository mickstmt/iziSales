"""
Inicialización de Celery para iziSales

Este archivo configura Celery con Flask usando el Application Factory Pattern
"""
from celery import Celery
from app import create_app
from app.tasks.celery_config import beat_schedule, timezone


def make_celery(app=None):
    """
    Crear instancia de Celery configurada con Flask

    Args:
        app: Instancia de Flask (opcional)

    Returns:
        celery: Instancia de Celery configurada
    """
    if app is None:
        app = create_app()

    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )

    # Configurar Celery con configuración de Flask
    celery.conf.update(app.config)

    # Configurar tareas periódicas (Celery Beat)
    celery.conf.beat_schedule = beat_schedule
    celery.conf.timezone = timezone

    # Configurar serialización y otros parámetros
    celery.conf.task_serializer = 'json'
    celery.conf.result_serializer = 'json'
    celery.conf.accept_content = ['json']
    celery.conf.result_expires = 3600

    # Crear contexto de Flask para las tareas
    class ContextTask(celery.Task):
        """Tarea base que incluye contexto de Flask"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery


# Crear instancia de Celery
celery = make_celery()


# Autodescubrir tareas en app.tasks
celery.autodiscover_tasks(['app.tasks'])
