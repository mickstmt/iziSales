# Guía de Celery para iziSales

## Descripción

Celery está configurado para ejecutar tareas asíncronas relacionadas con el envío de comprobantes a SUNAT, permitiendo que el POS no se bloquee durante el proceso.

## Requisitos Previos

1. **Redis** debe estar instalado y corriendo
2. **Python 3.8+** con dependencias instaladas (`celery`, `redis`)

## Instalación de Redis

### Windows
```bash
# Descargar Redis para Windows desde:
# https://github.com/microsoftarchive/redis/releases

# O usar WSL:
wsl --install
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis

# Mac
brew install redis
brew services start redis
```

### Verificar Redis
```bash
redis-cli ping
# Respuesta: PONG
```

## Tareas Implementadas

### 1. `send_sale_to_sunat_async` (On-Demand)
**Descripción:** Envía una boleta a SUNAT de forma asíncrona sin bloquear el POS.

**Uso:**
```python
from app.tasks.sunat_tasks import send_sale_to_sunat_async

# Desde código
send_sale_to_sunat_async.delay(sale_id=123)
```

**Características:**
- Reintentos automáticos: 3 intentos, cada 5 minutos
- Genera PDF automáticamente si es aceptada
- No bloquea el POS

### 2. `retry_failed_sales` (Periódica: cada 30 min)
**Descripción:** Reintenta automáticamente ventas que fallaron hace más de 1 hora.

**Criterios:**
- `sunat_status == ERROR`
- `sunat_sent_at > 1 hora atrás`
- `is_cancelled == False`
- Límite: 50 ventas por ejecución

### 3. `generate_daily_report` (Periódica: 23:00 diario)
**Descripción:** Genera reporte diario de envíos a SUNAT.

**Estadísticas:**
- Total de boletas emitidas
- Aceptadas / Rechazadas / Con error / Pendientes
- Porcentaje de éxito
- Total facturado

### 4. `cleanup_old_files` (Periódica: Domingos 02:00)
**Descripción:** Limpia archivos antiguos para liberar espacio.

**Limpia:**
- XMLs de más de 6 meses
- CDRs de más de 6 meses
- QR codes de más de 6 meses
- PDFs de ventas canceladas de más de 3 meses

## Iniciar Celery

### Modo Desarrollo (3 terminales)

**Terminal 1: Worker**
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Iniciar worker
celery -A celery_app.celery worker --loglevel=info
```

**Terminal 2: Beat (tareas periódicas)**
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Iniciar beat
celery -A celery_app.celery beat --loglevel=info
```

**Terminal 3: Flask (aplicación web)**
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Iniciar Flask
flask run
```

### Modo Producción (con Supervisor)

**Archivo: `/etc/supervisor/conf.d/izisales-celery.conf`**
```ini
[program:izisales-worker]
command=/path/to/venv/bin/celery -A celery_app.celery worker --loglevel=info
directory=/path/to/iziSales
user=www-data
autostart=true
autorestart=true
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:izisales-beat]
command=/path/to/venv/bin/celery -A celery_app.celery beat --loglevel=info
directory=/path/to/iziSales
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

**Iniciar servicios:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start izisales-worker
sudo supervisorctl start izisales-beat
```

## Monitoreo

### Ver tareas en ejecución
```bash
celery -A celery_app.celery inspect active
```

### Ver tareas programadas
```bash
celery -A celery_app.celery inspect scheduled
```

### Ver estadísticas
```bash
celery -A celery_app.celery inspect stats
```

### Flower (Monitor Web)
```bash
# Instalar Flower
pip install flower

# Iniciar
celery -A celery_app.celery flower

# Acceder a http://localhost:5555
```

## Uso desde la API

### Envío Asíncrono desde POS

**Opción 1: Modificar endpoint para usar Celery**
```python
# En app/routes/pos.py

from app.tasks.sunat_tasks import send_sale_to_sunat_async

@pos_bp.route('/send-to-sunat-async/<int:sale_id>', methods=['POST'])
@login_required
@role_required('admin', 'seller')
def send_to_sunat_async_endpoint(sale_id):
    """Enviar boleta a SUNAT de forma asíncrona"""
    try:
        sale = Sale.query.get_or_404(sale_id)

        # Verificar permisos
        if sale.seller_id != current_user.id and not current_user.has_role('admin'):
            return jsonify({'success': False, 'message': 'No autorizado'}), 403

        # Lanzar tarea asíncrona
        task = send_sale_to_sunat_async.delay(sale_id)

        return jsonify({
            'success': True,
            'message': 'Boleta en cola de envío a SUNAT',
            'task_id': task.id,
            'sale_id': sale_id,
            'correlative': sale.correlative
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Opción 2: Verificar estado de tarea**
```python
@pos_bp.route('/task-status/<task_id>', methods=['GET'])
@login_required
def check_task_status(task_id):
    """Verificar estado de tarea Celery"""
    from celery.result import AsyncResult
    from celery_app import celery

    task = AsyncResult(task_id, app=celery)

    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pendiente...'}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'result': task.result}
    elif task.state == 'FAILURE':
        response = {'state': task.state, 'error': str(task.info)}
    else:
        response = {'state': task.state}

    return jsonify(response)
```

## Configuración Avanzada

### Variables de Entorno (.env)

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Timezone
TZ=America/Lima
```

### Modificar Schedule de Tareas

Editar `app/tasks/celery_config.py`:

```python
beat_schedule = {
    'retry-failed-sales-every-30min': {
        'task': 'app.tasks.sunat_tasks.retry_failed_sales',
        'schedule': crontab(minute='*/15'),  # Cambiar a cada 15 min
    },
}
```

## Troubleshooting

### Error: "No module named 'celery_app'"
```bash
# Asegurarse de estar en el directorio raíz del proyecto
cd /path/to/iziSales
python -c "import celery_app"
```

### Error: "redis.exceptions.ConnectionError"
```bash
# Verificar que Redis esté corriendo
redis-cli ping

# Si no responde, iniciar Redis
sudo service redis-server start  # Linux
brew services start redis         # Mac
```

### Error: "Task always shows PENDING"
```bash
# Verificar que el worker esté corriendo
celery -A celery_app.celery inspect active

# Revisar logs del worker
celery -A celery_app.celery worker --loglevel=debug
```

### Limpiar tareas antiguas
```bash
# Limpiar todos los resultados
celery -A celery_app.celery purge

# Reiniciar workers
celery -A celery_app.celery control shutdown
celery -A celery_app.celery worker --loglevel=info
```

## Testing

### Probar tarea manualmente
```python
python
>>> from celery_app import celery
>>> from app.tasks.sunat_tasks import send_sale_to_sunat_async
>>>
>>> # Enviar tarea
>>> result = send_sale_to_sunat_async.delay(123)
>>>
>>> # Ver estado
>>> result.state
'SUCCESS'
>>>
>>> # Ver resultado
>>> result.get()
{'success': True, 'sale_id': 123, ...}
```

### Ejecutar tarea de reporte manualmente
```bash
celery -A celery_app.celery call app.tasks.sunat_tasks.generate_daily_report
```

## Logs

Los logs de Celery se mezclan con los logs de Flask en:
- `logs/izisales_YYYY-MM-DD.log` - Logs generales
- `logs/errors_YYYY-MM-DD.log` - Solo errores

Buscar por `[Celery]` para filtrar logs de tareas:
```bash
grep "\[Celery\]" logs/izisales_$(date +%Y-%m-%d).log
```

## Performance

### Configuración recomendada para producción:

```bash
# Worker con concurrencia
celery -A celery_app.celery worker \
  --concurrency=4 \
  --max-tasks-per-child=1000 \
  --loglevel=info

# Beat (solo 1 instancia)
celery -A celery_app.celery beat --loglevel=info
```

### Monitoreo de memoria:
```bash
# Ver uso de memoria del worker
ps aux | grep celery
```

## Recursos Adicionales

- [Documentación oficial de Celery](https://docs.celeryproject.org/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices)
- [Flask + Celery Tutorial](https://blog.miguelgrinberg.com/post/using-celery-with-flask)
