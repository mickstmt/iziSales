# 📋 iziSales - Sistema de Facturación Electrónica RUS

Sistema profesional de facturación electrónica para el Régimen Único Simplificado (RUS) en Perú, desarrollado con Flask y Bootstrap.

## 🚀 Características

- ✅ Emisión de boletas electrónicas (UBL 2.1)
- ✅ Integración con WooCommerce
- ✅ Consulta automática DNI/RUC (RENIEC/SUNAT)
- ✅ Control automático de límites RUS
- ✅ Generación de PDF y código QR
- ✅ Envío automático a SUNAT vía PSE
- ✅ Interface tipo POS optimizada
- ✅ Dashboard con reportes en tiempo real

## 📋 Requisitos

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- WooCommerce 3.0+

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd iziSales
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
notepad .env
```

### 5. Configurar base de datos

```bash
# Crear base de datos en MySQL
mysql -u root -p
CREATE DATABASE izisales CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Inicializar migraciones
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Crear usuario administrador

```bash
flask create-admin
```

### 7. Inicializar correlativos

```bash
flask init-correlatives
```

### 8. Sincronizar productos (opcional)

```bash
flask sync-products
```

## 🎯 Uso

### Desarrollo

```bash
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

### Producción

```bash
gunicorn --config gunicorn.conf.py wsgi:app
```

## 📁 Estructura del Proyecto

```
iziSales/
├── app/
│   ├── models/         # Modelos de datos
│   ├── routes/         # Rutas y vistas
│   ├── services/       # Lógica de negocio
│   ├── utils/          # Utilidades
│   ├── tasks/          # Tareas Celery
│   ├── static/         # CSS, JS, imágenes
│   └── templates/      # Templates HTML
├── storage/            # Archivos generados
│   ├── pdf/           # PDFs de boletas
│   ├── xml/           # XMLs firmados
│   ├── cdr/           # CDRs de SUNAT
│   └── backup/        # Backups
├── logs/              # Logs de la aplicación
├── tests/             # Tests
├── migrations/        # Migraciones de BD
├── requirements.txt
├── run.py
└── README.md
```

## 🔧 Comandos Disponibles

```bash
# Flask CLI
flask run --debug              # Iniciar en modo debug
flask create-admin             # Crear usuario admin
flask init-db                  # Inicializar base de datos
flask init-correlatives        # Inicializar correlativos
flask sync-products            # Sincronizar productos de WooCommerce

# Migraciones
flask db migrate -m "message"  # Crear migración
flask db upgrade               # Aplicar migraciones
flask db downgrade             # Revertir migración

# Celery
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/
pytest tests/integration/
```

## 📚 Documentación

- [Plan de Implementación](Plan_de_Implementacion_Flask.md)
- [Documentación de la API](#)
- [Guía de Usuario](#)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial.

## 📞 Soporte

Para soporte o consultas:
- Email: soporte@tuempresa.com
- Logs: `./logs/`

## 🎯 Estado del Proyecto

- [x] FASE 1: Configuración Base ✅
- [ ] FASE 2: Modelos de Datos
- [ ] FASE 3: Autenticación
- [ ] FASE 4: Servicios Core
- [ ] FASE 5: Generación XML
- [ ] FASE 6: Generación PDF/QR
- [ ] FASE 7: Integración SUNAT
- [ ] FASE 8: Frontend POS
- [ ] FASE 9: Dashboard
- [ ] FASE 10: Testing
- [ ] FASE 11: Deployment
- [ ] FASE 12: Mantenimiento

---

**Versión**: 1.0.0
**Desarrollado con**: Flask + Bootstrap + ❤️
