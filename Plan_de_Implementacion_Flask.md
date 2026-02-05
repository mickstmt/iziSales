# 📋 Plan de Implementación Profesional - Sistema de Facturación Electrónica RUS
## iziSales - Flask + Bootstrap

---

## 📊 Resumen Ejecutivo

Sistema de facturación electrónica para Régimen Único Simplificado (RUS) integrado con WooCommerce, desarrollado con Flask y Bootstrap. Cumple 100% con normativas SUNAT (UBL 2.1, PSE).

### Objetivos Principales:
- ✅ Emisión rápida de boletas electrónicas (interfaz tipo POS)
- ✅ Control automático de límites RUS (S/ 5,000 y S/ 8,000)
- ✅ Integración bidireccional con WooCommerce
- ✅ Cumplimiento normativo SUNAT
- ✅ Trazabilidad completa de operaciones

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Bootstrap 5)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dashboard   │  │  POS Venta   │  │   Reportes   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  Flask API    │
                    │  (Python 3.11+)│
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌─────────▼────────┐
│   MySQL DB     │  │ WooCommerce │  │   API PSE/SUNAT  │
│   (Principal)  │  │     API     │  │  (Facturación)   │
└────────────────┘  └─────────────┘  └──────────────────┘
        │
┌───────▼────────┐
│  Redis Cache   │
│  (Sesiones)    │
└────────────────┘
```

---

## 🛠️ Stack Tecnológico

### Backend
| Componente | Tecnología | Versión | Propósito |
|-----------|------------|---------|-----------|
| Framework | Flask | 3.0+ | Core de la aplicación |
| ORM | SQLAlchemy | 2.0+ | Manejo de base de datos |
| Migraciones | Flask-Migrate | 4.0+ | Versionamiento de BD |
| Auth | Flask-Login | 0.6+ | Autenticación de usuarios |
| Cache | Flask-Caching | 2.0+ | Optimización de consultas |
| API REST | Flask-RESTful | 0.3+ | Endpoints estructurados |
| Validación | Marshmallow | 3.20+ | Validación de datos |
| Tareas Async | Celery + Redis | 5.3+ | Procesos en background |
| XML | lxml | 4.9+ | Generación UBL 2.1 |
| PDF | ReportLab | 4.0+ | Generación de PDF profesionales |
| QR Codes | qrcode | 7.4+ | QR para boletas |
| HTTP Client | Requests | 2.31+ | Consumo de APIs externas |

### Frontend
| Componente | Tecnología | Versión |
|-----------|------------|---------|
| Framework CSS | Bootstrap | 5.3+ |
| JavaScript | Vanilla JS / Alpine.js | 3.13+ |
| Icons | Bootstrap Icons | 1.11+ |
| Datatables | DataTables | 1.13+ |
| Alertas | SweetAlert2 | 11.0+ |
| AJAX | Axios | 1.6+ |

### Base de Datos
| Tipo | Tecnología | Uso |
|------|------------|-----|
| Principal | MySQL | 8.0+ |
| Cache/Sesiones | Redis | 7.0+ |

### Infraestructura
- **Servidor Web**: Gunicorn + Nginx
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **Backup**: Cron + rsync
- **Monitoreo**: Logs (Loguru) + Sentry

---

## 📁 Estructura del Proyecto

```
iziSales/
├── app/
│   ├── __init__.py                 # Factory pattern
│   ├── config.py                   # Configuraciones
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # Usuarios
│   │   ├── sale.py                 # Ventas
│   │   ├── product.py              # Productos (cache de Woo)
│   │   ├── customer.py             # Clientes
│   │   ├── document.py             # Documentos electrónicos
│   │   └── correlative.py          # Control de correlativos
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login/Logout
│   │   ├── dashboard.py            # Dashboard principal
│   │   ├── pos.py                  # Punto de venta
│   │   ├── reports.py              # Reportes
│   │   └── api.py                  # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── woocommerce_service.py  # Integración Woo
│   │   ├── sunat_service.py        # API PSE/SUNAT
│   │   ├── reniec_service.py       # Consulta DNI
│   │   ├── pdf_service.py          # Generación PDF
│   │   ├── xml_service.py          # Generación XML UBL 2.1
│   │   ├── qr_service.py           # Generación QR
│   │   └── rus_control.py          # Semáforo RUS
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py           # Validadores (RUC, DNI)
│   │   ├── decorators.py           # Decoradores custom
│   │   ├── helpers.py              # Funciones auxiliares
│   │   └── constants.py            # Constantes del sistema
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── backup_task.py          # Backup automático
│   │   └── sync_task.py            # Sincronización Woo
│   ├── static/
│   │   ├── css/
│   │   │   ├── custom.css
│   │   │   └── pos.css
│   │   ├── js/
│   │   │   ├── pos.js
│   │   │   ├── dashboard.js
│   │   │   └── utils.js
│   │   └── img/
│   └── templates/
│       ├── base.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard/
│       │   └── index.html
│       ├── pos/
│       │   └── index.html
│       ├── reports/
│       │   ├── sales.html
│       │   └── products.html
│       └── components/
│           ├── navbar.html
│           ├── sidebar.html
│           └── footer.html
├── migrations/                      # Migraciones de BD
├── storage/
│   ├── pdf/                        # PDFs generados
│   ├── xml/                        # XMLs firmados
│   ├── cdr/                        # CDRs de SUNAT
│   └── backup/                     # Backups
├── logs/                           # Logs de la aplicación
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt
├── .env.example
├── run.py                          # Entry point
├── celery_worker.py               # Worker Celery
└── README.md
```

---

## 🎯 FASE 1: Configuración Base y Estructura (Semana 1)

### 1.1 Setup del Entorno
**Objetivo**: Preparar el ambiente de desarrollo

**Tareas**:
- [ ] Crear entorno virtual Python 3.11+
- [ ] Instalar dependencias base
- [ ] Configurar MySQL y Redis
- [ ] Estructura de carpetas del proyecto
- [ ] Configuración de variables de entorno (.env)
- [ ] Sistema de logs con Loguru

**Entregables**:
```python
# requirements.txt base
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-Caching==2.1.0
Flask-RESTful==0.3.10
marshmallow==3.20.1
python-dotenv==1.0.0
mysql-connector-python==8.2.0
redis==5.0.1
celery==5.3.4
requests==2.31.0
lxml==4.9.3
reportlab==4.0.7
qrcode==7.4.2
Pillow==10.1.0
loguru==0.7.2
cryptography==41.0.7
```

**Configuración**:
```python
# app/config.py
import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://user:pass@localhost/izisales')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL

    # Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = REDIS_URL
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Celery
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # WooCommerce
    WOO_URL = os.getenv('WOO_URL')
    WOO_CONSUMER_KEY = os.getenv('WOO_CONSUMER_KEY')
    WOO_CONSUMER_SECRET = os.getenv('WOO_CONSUMER_SECRET')

    # SUNAT/PSE
    PSE_API_URL = os.getenv('PSE_API_URL')
    PSE_TOKEN = os.getenv('PSE_TOKEN')

    # RENIEC/SUNAT APIs
    RENIEC_API_URL = os.getenv('RENIEC_API_URL')
    RENIEC_TOKEN = os.getenv('RENIEC_TOKEN')

    # RUS Limits
    RUS_LIMIT_CATEGORY_1 = 5000.00  # S/ 5,000
    RUS_LIMIT_CATEGORY_2 = 8000.00  # S/ 8,000

    # Storage
    STORAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'storage')
    PDF_PATH = os.path.join(STORAGE_PATH, 'pdf')
    XML_PATH = os.path.join(STORAGE_PATH, 'xml')
    CDR_PATH = os.path.join(STORAGE_PATH, 'cdr')
    BACKUP_PATH = os.path.join(STORAGE_PATH, 'backup')

    # Company Info (RUS)
    COMPANY_RUC = os.getenv('COMPANY_RUC')
    COMPANY_NAME = os.getenv('COMPANY_NAME')
    COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS')
    COMPANY_UBIGEO = os.getenv('COMPANY_UBIGEO')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://test:test@localhost/izisales_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## 🎯 FASE 2: Modelos de Datos y Migraciones (Semana 1-2)

### 2.1 Diseño de Base de Datos

**Tablas Principales**:

```python
# app/models/user.py
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Enum('admin', 'seller', 'viewer'), default='seller')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    sales = db.relationship('Sale', backref='seller', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
```

```python
# app/models/customer.py
from app import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.Enum('DNI', 'RUC', 'CE', 'PASAPORTE'), nullable=False)
    document_number = db.Column(db.String(11), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_business = db.Column(db.Boolean, default=False)  # True si es RUC 20
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    sales = db.relationship('Sale', backref='customer', lazy='dynamic')

    def __repr__(self):
        return f'<Customer {self.document_number} - {self.name}>'
```

```python
# app/models/product.py
from app import db
from datetime import datetime

class Product(db.Model):
    """Cache local de productos de WooCommerce"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    woo_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Decimal(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    sale_items = db.relationship('SaleItem', backref='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.sku} - {self.name}>'
```

```python
# app/models/correlative.py
from app import db
from datetime import datetime

class Correlative(db.Model):
    """Control de correlativos para evitar saltos"""
    __tablename__ = 'correlatives'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.Enum('BOLETA', 'FACTURA', 'NOTA_CREDITO'), nullable=False)
    series = db.Column(db.String(4), nullable=False)  # B001, F001, etc.
    current_number = db.Column(db.Integer, default=0)
    last_issued = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('document_type', 'series', name='unique_doc_series'),
    )

    def get_next_correlative(self):
        """Obtiene el siguiente correlativo sin avanzar"""
        return f"{self.series}-{str(self.current_number + 1).zfill(8)}"

    def advance_correlative(self):
        """Avanza el correlativo (solo después de éxito en SUNAT)"""
        self.current_number += 1
        self.last_issued = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<Correlative {self.series}-{self.current_number}>'
```

```python
# app/models/sale.py
from app import db
from datetime import datetime

class Sale(db.Model):
    """Venta principal"""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    correlative = db.Column(db.String(20), unique=True, nullable=False, index=True)  # B001-00000002
    document_type = db.Column(db.Enum('BOLETA', 'FACTURA'), default='BOLETA')

    # Relaciones FK
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Montos
    subtotal = db.Column(db.Decimal(10, 2), nullable=False)
    tax = db.Column(db.Decimal(10, 2), default=0.00)  # Para RUS será 0
    total = db.Column(db.Decimal(10, 2), nullable=False)

    # Control SUNAT
    xml_path = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    cdr_path = db.Column(db.String(255))
    qr_code = db.Column(db.Text)
    hash = db.Column(db.String(255))

    # Estados
    sunat_status = db.Column(db.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'ERROR'), default='PENDING')
    sunat_response = db.Column(db.Text)
    sunat_sent_at = db.Column(db.DateTime)

    # Auditoria
    is_cancelled = db.Column(db.Boolean, default=False)
    cancelled_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sale {self.correlative}>'

class SaleItem(db.Model):
    """Detalle de items de la venta"""
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Decimal(10, 2), nullable=False)
    subtotal = db.Column(db.Decimal(10, 2), nullable=False)

    # Información adicional del producto (snapshot al momento de la venta)
    product_name = db.Column(db.String(255), nullable=False)
    product_sku = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SaleItem {self.product_sku} x{self.quantity}>'
```

```python
# app/models/rus_control.py
from app import db
from datetime import datetime

class RUSControl(db.Model):
    """Control mensual de límites RUS"""
    __tablename__ = 'rus_control'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_invoiced = db.Column(db.Decimal(10, 2), default=0.00)
    transaction_count = db.Column(db.Integer, default=0)
    alert_level = db.Column(db.Enum('GREEN', 'YELLOW', 'RED'), default='GREEN')
    is_blocked = db.Column(db.Boolean, default=False)  # Bloqueo al superar S/ 8,000
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('year', 'month', name='unique_year_month'),
    )

    def update_total(self, amount):
        """Actualiza el total y el nivel de alerta"""
        self.total_invoiced += amount
        self.transaction_count += 1

        # Actualizar nivel de alerta
        if self.total_invoiced >= 8000:
            self.alert_level = 'RED'
            self.is_blocked = True
        elif self.total_invoiced >= 5000:
            self.alert_level = 'YELLOW'
        else:
            self.alert_level = 'GREEN'

        db.session.commit()

    def __repr__(self):
        return f'<RUSControl {self.year}-{self.month}: S/ {self.total_invoiced}>'
```

```python
# app/models/audit_log.py
from app import db
from datetime import datetime

class AuditLog(db.Model):
    """Log de auditoría de todas las operaciones críticas"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)  # 'CREATE_SALE', 'CANCEL_SALE', etc.
    entity_type = db.Column(db.String(50))  # 'Sale', 'Customer', etc.
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'
```

### 2.2 Migraciones
```bash
# Inicializar migraciones
flask db init

# Crear primera migración
flask db migrate -m "Initial database schema"

# Aplicar migraciones
flask db upgrade
```

---

## 🎯 FASE 3: Sistema de Autenticación y Seguridad (Semana 2)

### 3.1 Autenticación con Flask-Login

```python
# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Audit log
            audit = AuditLog(
                user_id=user.id,
                action='LOGIN',
                entity_type='User',
                entity_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            db.session.add(audit)
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action='LOGOUT',
        entity_type='User',
        entity_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(audit)
    db.session.commit()

    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('auth.login'))
```

### 3.2 Decoradores de Seguridad

```python
# app/utils/decorators.py
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """Requiere que el usuario tenga uno de los roles especificados"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('No tienes permisos para acceder a esta página', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rus_limit_check(f):
    """Verifica que no se haya superado el límite RUS antes de crear venta"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.services.rus_control import RUSControlService

        service = RUSControlService()
        if service.is_blocked():
            flash('⚠️ LÍMITE RUS SUPERADO: No se pueden emitir más boletas este mes', 'danger')
            return redirect(url_for('dashboard.index'))

        return f(*args, **kwargs)
    return decorated_function
```

### 3.3 Validadores

```python
# app/utils/validators.py
import re

def validate_ruc(ruc):
    """Valida formato de RUC peruano"""
    if not ruc or len(ruc) != 11:
        return False

    if not ruc.isdigit():
        return False

    # Verificar dígitos verificadores
    factors = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    sum_total = sum(int(ruc[i]) * factors[i] for i in range(10))
    check_digit = 11 - (sum_total % 11)

    if check_digit == 10:
        check_digit = 0
    elif check_digit == 11:
        check_digit = 1

    return check_digit == int(ruc[10])

def validate_dni(dni):
    """Valida formato de DNI peruano"""
    if not dni or len(dni) != 8:
        return False
    return dni.isdigit()

def is_business_ruc(ruc):
    """Verifica si el RUC corresponde a Persona Jurídica (RUC 20)"""
    if not validate_ruc(ruc):
        return False
    return ruc.startswith('20')

def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

---

## 🎯 FASE 4: Servicios Core (Semana 2-3)

### 4.1 Servicio de WooCommerce

```python
# app/services/woocommerce_service.py
from woocommerce import API
from app import cache
from app.models.product import Product
from app import db
from flask import current_app
from loguru import logger

class WooCommerceService:
    def __init__(self):
        self.api = API(
            url=current_app.config['WOO_URL'],
            consumer_key=current_app.config['WOO_CONSUMER_KEY'],
            consumer_secret=current_app.config['WOO_CONSUMER_SECRET'],
            version='wc/v3',
            timeout=30
        )

    @cache.cached(timeout=300, key_prefix='woo_products')
    def get_products(self, per_page=100):
        """Obtiene productos de WooCommerce con caché"""
        try:
            response = self.api.get('products', params={'per_page': per_page})
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo productos de WooCommerce: {e}")
            return []

    def search_product_by_sku(self, sku):
        """Busca producto por SKU"""
        try:
            response = self.api.get('products', params={'sku': sku})
            products = response.json()
            return products[0] if products else None
        except Exception as e:
            logger.error(f"Error buscando producto por SKU {sku}: {e}")
            return None

    def sync_products_to_local(self):
        """Sincroniza productos de Woo a base de datos local"""
        try:
            products = self.get_products()
            synced_count = 0

            for woo_product in products:
                product = Product.query.filter_by(woo_id=woo_product['id']).first()

                if not product:
                    product = Product(woo_id=woo_product['id'])

                product.sku = woo_product['sku'] or f"WOO-{woo_product['id']}"
                product.name = woo_product['name']
                product.description = woo_product['short_description']
                product.price = float(woo_product['price']) if woo_product['price'] else 0
                product.stock_quantity = woo_product.get('stock_quantity', 0)
                product.is_active = woo_product['status'] == 'publish'

                db.session.add(product)
                synced_count += 1

            db.session.commit()
            logger.info(f"Sincronizados {synced_count} productos desde WooCommerce")
            return synced_count

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando productos: {e}")
            return 0

    def update_stock(self, product_id, new_quantity):
        """Actualiza stock en WooCommerce"""
        try:
            data = {'stock_quantity': new_quantity}
            response = self.api.put(f'products/{product_id}', data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error actualizando stock en WooCommerce: {e}")
            return False
```

### 4.2 Servicio RENIEC/SUNAT

```python
# app/services/reniec_service.py
import requests
from flask import current_app
from loguru import logger
from app import cache

class ReniecService:
    """Consulta de DNI y RUC a APIs externas"""

    @cache.memoize(timeout=86400)  # Cache por 24 horas
    def query_dni(self, dni):
        """Consulta datos de DNI en RENIEC"""
        try:
            headers = {
                'Authorization': f"Bearer {current_app.config['RENIEC_TOKEN']}"
            }
            response = requests.get(
                f"{current_app.config['RENIEC_API_URL']}/dni/{dni}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'document_type': 'DNI',
                    'document_number': dni,
                    'name': f"{data.get('nombres')} {data.get('apellidoPaterno')} {data.get('apellidoMaterno')}",
                    'address': data.get('direccion', '')
                }
            else:
                logger.warning(f"DNI {dni} no encontrado")
                return {'success': False, 'message': 'DNI no encontrado'}

        except Exception as e:
            logger.error(f"Error consultando DNI {dni}: {e}")
            return {'success': False, 'message': str(e)}

    @cache.memoize(timeout=86400)
    def query_ruc(self, ruc):
        """Consulta datos de RUC en SUNAT"""
        try:
            headers = {
                'Authorization': f"Bearer {current_app.config['RENIEC_TOKEN']}"
            }
            response = requests.get(
                f"{current_app.config['RENIEC_API_URL']}/ruc/{ruc}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'document_type': 'RUC',
                    'document_number': ruc,
                    'name': data.get('razonSocial', ''),
                    'address': data.get('direccion', ''),
                    'is_business': ruc.startswith('20')
                }
            else:
                logger.warning(f"RUC {ruc} no encontrado")
                return {'success': False, 'message': 'RUC no encontrado'}

        except Exception as e:
            logger.error(f"Error consultando RUC {ruc}: {e}")
            return {'success': False, 'message': str(e)}
```

### 4.3 Servicio de Control RUS

```python
# app/services/rus_control.py
from app.models.rus_control import RUSControl
from app import db
from datetime import datetime
from flask import current_app
from loguru import logger

class RUSControlService:
    def __init__(self):
        self.category_1_limit = current_app.config['RUS_LIMIT_CATEGORY_1']
        self.category_2_limit = current_app.config['RUS_LIMIT_CATEGORY_2']

    def get_current_month_control(self):
        """Obtiene o crea el control del mes actual"""
        now = datetime.utcnow()
        control = RUSControl.query.filter_by(
            year=now.year,
            month=now.month
        ).first()

        if not control:
            control = RUSControl(year=now.year, month=now.month)
            db.session.add(control)
            db.session.commit()

        return control

    def add_sale_amount(self, amount):
        """Agrega un monto de venta y actualiza alertas"""
        control = self.get_current_month_control()
        control.update_total(amount)
        logger.info(f"RUS Control actualizado: S/ {control.total_invoiced} / S/ {self.category_2_limit}")
        return control

    def is_blocked(self):
        """Verifica si se superó el límite RUS"""
        control = self.get_current_month_control()
        return control.is_blocked

    def get_status(self):
        """Obtiene el estado actual del control RUS"""
        control = self.get_current_month_control()

        percentage = (float(control.total_invoiced) / self.category_2_limit) * 100

        return {
            'total_invoiced': float(control.total_invoiced),
            'category_1_limit': self.category_1_limit,
            'category_2_limit': self.category_2_limit,
            'alert_level': control.alert_level,
            'is_blocked': control.is_blocked,
            'percentage': round(percentage, 2),
            'remaining': self.category_2_limit - float(control.total_invoiced),
            'transactions': control.transaction_count
        }

    def can_process_sale(self, amount):
        """Verifica si se puede procesar una venta sin superar límites"""
        control = self.get_current_month_control()
        projected_total = float(control.total_invoiced) + amount

        if projected_total > self.category_2_limit:
            return False, f"Esta venta superaría el límite RUS (S/ {self.category_2_limit})"

        if projected_total > self.category_1_limit:
            return True, "⚠️ ALERTA: Esta venta te llevará a la Categoría 2 del RUS"

        return True, "OK"
```

---

## 🎯 FASE 5: Generación XML UBL 2.1 (Semana 3)

### 5.1 Servicio XML SUNAT

```python
# app/services/xml_service.py
from lxml import etree
from datetime import datetime
import hashlib
import base64
from flask import current_app
from loguru import logger
import os

class XMLService:
    """Generación de XML UBL 2.1 para SUNAT"""

    def __init__(self):
        self.company_ruc = current_app.config['COMPANY_RUC']
        self.company_name = current_app.config['COMPANY_NAME']
        self.company_address = current_app.config['COMPANY_ADDRESS']
        self.company_ubigeo = current_app.config['COMPANY_UBIGEO']

    def generate_boleta_xml(self, sale):
        """Genera XML de boleta electrónica según UBL 2.1"""

        # Namespaces UBL 2.1
        nsmap = {
            None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            'ccts': "urn:un:unece:uncefact:documentation:2",
            'ds': "http://www.w3.org/2000/09/xmldsig#",
            'ext': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            'qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
            'sac': "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1",
            'udt': "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2",
            'xs': "http://www.w3.org/2001/XMLSchema",
            'xsi': "http://www.w3.org/2001/XMLSchema-instance"
        }

        # Elemento raíz
        invoice = etree.Element("Invoice", nsmap=nsmap)

        # UBL Version
        ubl_version = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UBLVersionID")
        ubl_version.text = "2.1"

        # Customization ID
        customization = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CustomizationID")
        customization.text = "2.0"

        # ID del documento (Correlativo)
        doc_id = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        doc_id.text = sale.correlative

        # Fecha de emisión
        issue_date = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueDate")
        issue_date.text = sale.created_at.strftime("%Y-%m-%d")

        # Hora de emisión
        issue_time = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueTime")
        issue_time.text = sale.created_at.strftime("%H:%M:%S")

        # Tipo de documento (03 = Boleta)
        invoice_type = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoiceTypeCode")
        invoice_type.set("listID", "0101")  # Venta Interna
        invoice_type.text = "03"

        # Moneda (PEN = Soles)
        currency = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DocumentCurrencyCode")
        currency.text = "PEN"

        # === FIRMA DIGITAL (Extension) ===
        extensions = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtensions")
        extension = etree.SubElement(extensions, "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtension")
        ext_content = etree.SubElement(extension, "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionContent")
        # Aquí iría la firma digital (lo maneja el PSE)

        # === PROVEEDOR (Emisor) ===
        supplier = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingSupplierParty")
        supplier_party = etree.SubElement(supplier, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party")

        # RUC del emisor
        supplier_id = etree.SubElement(supplier_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyIdentification")
        supplier_id_num = etree.SubElement(supplier_id, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        supplier_id_num.set("schemeID", "6")  # 6 = RUC
        supplier_id_num.text = self.company_ruc

        # Nombre comercial
        supplier_name = etree.SubElement(supplier_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyName")
        supplier_name_text = etree.SubElement(supplier_name, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name")
        supplier_name_text.text = self.company_name

        # Dirección
        supplier_address = etree.SubElement(supplier_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity")
        supplier_legal_name = etree.SubElement(supplier_address, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName")
        supplier_legal_name.text = self.company_name

        # === CLIENTE ===
        customer = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingCustomerParty")
        customer_party = etree.SubElement(customer, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party")

        # Documento del cliente
        customer_id = etree.SubElement(customer_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyIdentification")
        customer_id_num = etree.SubElement(customer_id, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")

        # Tipo de documento (1=DNI, 6=RUC)
        doc_type = "1" if sale.customer.document_type == "DNI" else "6"
        customer_id_num.set("schemeID", doc_type)
        customer_id_num.text = sale.customer.document_number

        # Nombre del cliente
        customer_legal = etree.SubElement(customer_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity")
        customer_name = etree.SubElement(customer_legal, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName")
        customer_name.text = sale.customer.name

        # === TOTALES ===
        # Total Gravado (para RUS, incluye IGV)
        tax_total = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal")
        tax_amount = etree.SubElement(tax_total, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
        tax_amount.set("currencyID", "PEN")
        tax_amount.text = f"{float(sale.tax):.2f}"

        # Subtotal de IGV
        tax_subtotal = etree.SubElement(tax_total, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxSubtotal")
        taxable_amount = etree.SubElement(tax_subtotal, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxableAmount")
        taxable_amount.set("currencyID", "PEN")
        taxable_amount.text = f"{float(sale.subtotal):.2f}"

        tax_amt = etree.SubElement(tax_subtotal, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
        tax_amt.set("currencyID", "PEN")
        tax_amt.text = f"{float(sale.tax):.2f}"

        # Categoría del impuesto
        tax_category = etree.SubElement(tax_subtotal, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxCategory")
        tax_scheme = etree.SubElement(tax_category, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme")
        tax_scheme_id = etree.SubElement(tax_scheme, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        tax_scheme_id.text = "1000"  # IGV
        tax_scheme_name = etree.SubElement(tax_scheme, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name")
        tax_scheme_name.text = "IGV"
        tax_type = etree.SubElement(tax_scheme, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxTypeCode")
        tax_type.text = "VAT"

        # Total a pagar
        legal_monetary = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}LegalMonetaryTotal")
        payable_amount = etree.SubElement(legal_monetary, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PayableAmount")
        payable_amount.set("currencyID", "PEN")
        payable_amount.text = f"{float(sale.total):.2f}"

        # === LÍNEAS DE DETALLE ===
        for idx, item in enumerate(sale.items, start=1):
            line = etree.SubElement(invoice, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceLine")

            # Número de línea
            line_id = etree.SubElement(line, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            line_id.text = str(idx)

            # Cantidad
            quantity = etree.SubElement(line, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoicedQuantity")
            quantity.set("unitCode", "NIU")  # Unidad de medida
            quantity.text = str(item.quantity)

            # Precio total de la línea
            line_extension = etree.SubElement(line, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount")
            line_extension.set("currencyID", "PEN")
            line_extension.text = f"{float(item.subtotal):.2f}"

            # Precio unitario
            pricing = etree.SubElement(line, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PricingReference")
            alternative_price = etree.SubElement(pricing, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AlternativeConditionPrice")
            price_amount = etree.SubElement(alternative_price, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount")
            price_amount.set("currencyID", "PEN")
            price_amount.text = f"{float(item.unit_price):.2f}"

            # Item
            item_element = etree.SubElement(line, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Item")
            item_description = etree.SubElement(item_element, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Description")
            item_description.text = item.product_name

            # Código del producto
            sellers_item = etree.SubElement(item_element, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}SellersItemIdentification")
            sellers_id = etree.SubElement(sellers_item, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            sellers_id.text = item.product_sku

            # Precio
            price = etree.SubElement(line, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price")
            price_amt = etree.SubElement(price, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount")
            price_amt.set("currencyID", "PEN")
            price_amt.text = f"{float(item.unit_price):.2f}"

        # Convertir a string XML
        xml_string = etree.tostring(invoice, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        # Generar hash
        hash_value = self.generate_hash(xml_string)

        # Guardar archivo
        filename = f"{self.company_ruc}-03-{sale.correlative}.xml"
        filepath = os.path.join(current_app.config['XML_PATH'], filename)

        with open(filepath, 'wb') as f:
            f.write(xml_string)

        logger.info(f"XML generado: {filename}")

        return {
            'filename': filename,
            'filepath': filepath,
            'hash': hash_value,
            'xml_content': xml_string.decode('utf-8')
        }

    def generate_hash(self, xml_content):
        """Genera hash SHA-256 del XML"""
        if isinstance(xml_content, str):
            xml_content = xml_content.encode('utf-8')

        hash_obj = hashlib.sha256(xml_content)
        return base64.b64encode(hash_obj.digest()).decode('utf-8')
```

---

## 🎯 FASE 6: Generación PDF y QR (Semana 3-4)

### 6.1 Servicio PDF

```python
# app/services/pdf_service.py
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from flask import current_app
from loguru import logger
import os
from datetime import datetime

class PDFService:
    """Generación de PDFs para boletas electrónicas"""

    def __init__(self):
        self.company_ruc = current_app.config['COMPANY_RUC']
        self.company_name = current_app.config['COMPANY_NAME']
        self.company_address = current_app.config['COMPANY_ADDRESS']

    def generate_boleta_pdf(self, sale, qr_image_path):
        """Genera PDF de boleta electrónica"""

        filename = f"{self.company_ruc}-03-{sale.correlative}.pdf"
        filepath = os.path.join(current_app.config['PDF_PATH'], filename)

        # Crear canvas
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # === ENCABEZADO ===
        # Logo (si existe)
        # c.drawImage('path/to/logo.png', 50, height - 100, width=100, height=50)

        # Datos de la empresa
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 80, self.company_name)
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 95, f"RUC: {self.company_ruc}")
        c.drawString(50, height - 110, self.company_address)

        # Recuadro del documento
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(width - 200, height - 130, 150, 80)

        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width - 125, height - 70, "BOLETA DE VENTA")
        c.drawCentredString(width - 125, height - 85, "ELECTRÓNICA")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width - 125, height - 105, sale.correlative)

        # === DATOS DEL CLIENTE ===
        y_position = height - 160
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_position, "DATOS DEL CLIENTE")

        c.setFont("Helvetica", 10)
        y_position -= 20
        c.drawString(50, y_position, f"Documento: {sale.customer.document_type} - {sale.customer.document_number}")
        y_position -= 15
        c.drawString(50, y_position, f"Nombre: {sale.customer.name}")
        y_position -= 15
        c.drawString(50, y_position, f"Dirección: {sale.customer.address or 'N/A'}")

        # Fecha de emisión
        y_position -= 15
        c.drawString(50, y_position, f"Fecha de Emisión: {sale.created_at.strftime('%d/%m/%Y %H:%M:%S')}")

        # === DETALLE DE PRODUCTOS ===
        y_position -= 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_position, "DETALLE DE PRODUCTOS")

        y_position -= 25

        # Tabla de productos
        data = [['SKU', 'Descripción', 'Cant.', 'P. Unit.', 'Subtotal']]

        for item in sale.items:
            data.append([
                item.product_sku,
                item.product_name[:40],  # Truncar si es muy largo
                str(item.quantity),
                f"S/ {float(item.unit_price):.2f}",
                f"S/ {float(item.subtotal):.2f}"
            ])

        # Crear tabla
        table = Table(data, colWidths=[60, 250, 40, 70, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        # Dibujar tabla
        table.wrapOn(c, width, height)
        table_height = table._height
        table.drawOn(c, 50, y_position - table_height)

        y_position -= (table_height + 30)

        # === TOTALES ===
        c.setFont("Helvetica-Bold", 11)
        x_total = width - 200

        # Para RUS: Solo mostrar total (IGV incluido)
        c.drawString(x_total, y_position, "TOTAL A PAGAR:")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_total + 120, y_position, f"S/ {float(sale.total):.2f}")

        y_position -= 30
        c.setFont("Helvetica", 8)
        c.drawString(x_total, y_position, "(*) Precios incluyen IGV")

        # === CÓDIGO QR ===
        if qr_image_path and os.path.exists(qr_image_path):
            c.drawImage(qr_image_path, 50, 100, width=100, height=100)

        # === HASH ===
        c.setFont("Helvetica", 8)
        c.drawString(160, 150, f"Hash: {sale.hash[:50]}...")

        # === PIE DE PÁGINA (Texto Legal) ===
        c.setFont("Helvetica", 7)
        footer_text = [
            "Representación impresa de la Boleta de Venta Electrónica",
            f"Consulte su documento electrónico en: {current_app.config.get('COMPANY_WEBSITE', 'www.tuempresa.com')}",
            "Autorizado mediante Resolución de Intendencia N° XXX-XXX-XXXX/SUNAT",
            f"Emisor acogido al Régimen Único Simplificado (RUS)"
        ]

        y_footer = 80
        for line in footer_text:
            c.drawCentredString(width / 2, y_footer, line)
            y_footer -= 10

        # Guardar PDF
        c.save()

        logger.info(f"PDF generado: {filename}")

        return {
            'filename': filename,
            'filepath': filepath
        }

    def generate_ticket_pdf(self, sale, qr_image_path, width_mm=80):
        """Genera PDF formato ticket (80mm)"""
        # Implementación para ticket térmico
        # Similar al anterior pero adaptado a 80mm de ancho
        pass
```

### 6.2 Servicio QR

```python
# app/services/qr_service.py
import qrcode
import os
from flask import current_app
from loguru import logger

class QRService:
    """Generación de códigos QR para boletas electrónicas"""

    def generate_qr(self, sale):
        """Genera código QR según especificaciones SUNAT"""

        # Formato QR SUNAT:
        # RUC_emisor|TipoDoc|Serie|Correlativo|TotalIGV|TotalVenta|FechaEmision|TipoDocCliente|NumDocCliente|

        qr_data = (
            f"{current_app.config['COMPANY_RUC']}|"
            f"03|"  # 03 = Boleta
            f"{sale.correlative}|"
            f"{float(sale.tax):.2f}|"
            f"{float(sale.total):.2f}|"
            f"{sale.created_at.strftime('%Y-%m-%d')}|"
            f"{'1' if sale.customer.document_type == 'DNI' else '6'}|"
            f"{sale.customer.document_number}|"
        )

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar imagen
        filename = f"{current_app.config['COMPANY_RUC']}-03-{sale.correlative}-QR.png"
        filepath = os.path.join(current_app.config['PDF_PATH'], 'qr', filename)

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        img.save(filepath)

        logger.info(f"QR generado: {filename}")

        return {
            'qr_data': qr_data,
            'filename': filename,
            'filepath': filepath
        }
```

---

## 🎯 FASE 7: Integración con PSE/SUNAT (Semana 4)

### 7.1 Servicio SUNAT/PSE

```python
# app/services/sunat_service.py
import requests
from flask import current_app
from loguru import logger
from app.models.sale import Sale
from app import db
import os
from datetime import datetime

class SunatService:
    """Integración con PSE (Proveedor de Servicios Electrónicos)"""

    def __init__(self):
        self.pse_url = current_app.config['PSE_API_URL']
        self.pse_token = current_app.config['PSE_TOKEN']
        self.company_ruc = current_app.config['COMPANY_RUC']

    def send_to_sunat(self, sale_id):
        """
        Envía el XML al PSE para firma y envío a SUNAT
        Retorna: dict con status y respuesta
        """
        sale = Sale.query.get(sale_id)
        if not sale:
            return {'success': False, 'message': 'Venta no encontrada'}

        if not sale.xml_path or not os.path.exists(sale.xml_path):
            return {'success': False, 'message': 'XML no encontrado'}

        try:
            # Leer XML
            with open(sale.xml_path, 'rb') as xml_file:
                xml_content = xml_file.read()

            # Preparar request al PSE
            headers = {
                'Authorization': f'Bearer {self.pse_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'ruc': self.company_ruc,
                'tipo_documento': '03',  # Boleta
                'serie': sale.correlative.split('-')[0],
                'numero': sale.correlative.split('-')[1],
                'xml': xml_content.decode('utf-8') if isinstance(xml_content, bytes) else xml_content
            }

            # Enviar al PSE
            response = requests.post(
                f"{self.pse_url}/v1/invoice/send",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Actualizar sale con respuesta de SUNAT
                sale.sunat_status = 'ACCEPTED' if data.get('sunat_code') == '0' else 'REJECTED'
                sale.sunat_response = str(data)
                sale.sunat_sent_at = datetime.utcnow()

                # Si fue aceptado, guardar CDR
                if data.get('cdr_content'):
                    cdr_filename = f"{self.company_ruc}-03-{sale.correlative}-CDR.xml"
                    cdr_path = os.path.join(current_app.config['CDR_PATH'], cdr_filename)

                    with open(cdr_path, 'w', encoding='utf-8') as cdr_file:
                        cdr_file.write(data['cdr_content'])

                    sale.cdr_path = cdr_path

                db.session.commit()

                logger.info(f"Boleta {sale.correlative} enviada a SUNAT: {sale.sunat_status}")

                return {
                    'success': True,
                    'status': sale.sunat_status,
                    'sunat_code': data.get('sunat_code'),
                    'sunat_message': data.get('sunat_message', ''),
                    'cdr_path': sale.cdr_path
                }

            else:
                sale.sunat_status = 'ERROR'
                sale.sunat_response = f"HTTP {response.status_code}: {response.text}"
                db.session.commit()

                logger.error(f"Error enviando boleta {sale.correlative} a SUNAT: {response.text}")

                return {
                    'success': False,
                    'message': f"Error del PSE: {response.text}"
                }

        except requests.exceptions.Timeout:
            sale.sunat_status = 'ERROR'
            sale.sunat_response = 'Timeout al conectar con PSE'
            db.session.commit()

            logger.error(f"Timeout enviando boleta {sale.correlative}")
            return {'success': False, 'message': 'Timeout al conectar con PSE'}

        except Exception as e:
            sale.sunat_status = 'ERROR'
            sale.sunat_response = str(e)
            db.session.commit()

            logger.error(f"Error inesperado enviando boleta {sale.correlative}: {e}")
            return {'success': False, 'message': str(e)}

    def check_ticket_status(self, ticket):
        """Consulta el estado de un ticket en el PSE (para envíos asíncronos)"""
        try:
            headers = {'Authorization': f'Bearer {self.pse_token}'}
            response = requests.get(
                f"{self.pse_url}/v1/invoice/status/{ticket}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'message': 'Ticket no encontrado'}

        except Exception as e:
            logger.error(f"Error consultando ticket {ticket}: {e}")
            return {'success': False, 'message': str(e)}

    def verify_online(self, ruc, tipo_doc, serie, numero):
        """Verifica en línea si un documento está en SUNAT"""
        try:
            # Consultar directamente a SUNAT (si tienes acceso directo)
            # O consultar al PSE
            params = {
                'ruc': ruc,
                'tipo': tipo_doc,
                'serie': serie,
                'numero': numero
            }

            response = requests.get(
                f"{self.pse_url}/v1/invoice/verify",
                params=params,
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error verificando documento en SUNAT: {e}")
            return False
```

### 7.2 Tarea Celery para Envío Asíncrono

```python
# app/tasks/sunat_task.py
from celery import shared_task
from app.services.sunat_service import SunatService
from loguru import logger

@shared_task(bind=True, max_retries=3)
def send_to_sunat_async(self, sale_id):
    """
    Tarea asíncrona para enviar documentos a SUNAT
    Permite reintentos automáticos en caso de fallo
    """
    try:
        service = SunatService()
        result = service.send_to_sunat(sale_id)

        if not result['success']:
            # Reintentar después de 5 minutos
            raise self.retry(countdown=300)

        return result

    except Exception as e:
        logger.error(f"Error en tarea send_to_sunat_async: {e}")
        raise self.retry(exc=e, countdown=300)
```

---

## 🎯 FASE 8: Frontend POS con Bootstrap (Semana 4-5)

### 8.1 Layout Base

```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}iziSales - Sistema de Facturación{% endblock %}</title>

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">

    <!-- SweetAlert2 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    {% if current_user.is_authenticated %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('dashboard.index') }}">
                <i class="bi bi-receipt"></i> iziSales
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('dashboard.index') }}">
                            <i class="bi bi-house"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('pos.index') }}">
                            <i class="bi bi-cart"></i> Punto de Venta
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('reports.sales') }}">
                            <i class="bi bi-graph-up"></i> Reportes
                        </a>
                    </li>
                </ul>

                <!-- RUS Control Badge -->
                <div class="me-3" id="rus-badge">
                    <span class="badge bg-success" id="rus-status">
                        RUS: S/ <span id="rus-amount">0.00</span>
                    </span>
                </div>

                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle"></i> {{ current_user.full_name }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="#"><i class="bi bi-gear"></i> Configuración</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}"><i class="bi bi-box-arrow-right"></i> Cerrar Sesión</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-light text-center py-3 mt-5">
        <p class="mb-0">&copy; 2024 iziSales | Sistema de Facturación Electrónica RUS</p>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Axios -->
    <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>

    <!-- SweetAlert2 -->
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/utils.js') }}"></script>

    {% block extra_js %}{% endblock %}

    <script>
        // Auto-actualizar estado RUS cada 30 segundos
        {% if current_user.is_authenticated %}
        setInterval(updateRUSStatus, 30000);
        updateRUSStatus(); // Cargar al inicio

        function updateRUSStatus() {
            axios.get('/api/rus/status')
                .then(response => {
                    const data = response.data;
                    const badge = document.getElementById('rus-status');
                    const amount = document.getElementById('rus-amount');

                    amount.textContent = data.total_invoiced.toFixed(2);

                    // Cambiar color según nivel de alerta
                    badge.className = 'badge';
                    if (data.alert_level === 'RED') {
                        badge.classList.add('bg-danger');
                    } else if (data.alert_level === 'YELLOW') {
                        badge.classList.add('bg-warning');
                    } else {
                        badge.classList.add('bg-success');
                    }
                });
        }
        {% endif %}
    </script>
</body>
</html>
```

### 8.2 Vista POS (Punto de Venta)

```html
<!-- app/templates/pos/index.html -->
{% extends 'base.html' %}

{% block title %}Punto de Venta - iziSales{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pos.css') }}">
{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <!-- Columna Principal: Grid de Venta -->
        <div class="col-lg-8">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="bi bi-cart3"></i> Nueva Venta</h5>
                </div>
                <div class="card-body">
                    <!-- Buscador de Cliente -->
                    <div class="mb-4">
                        <label class="form-label fw-bold">Cliente</label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="customerSearch"
                                   placeholder="DNI (8 dígitos) o RUC (11 dígitos)" maxlength="11">
                            <button class="btn btn-primary" id="searchCustomerBtn">
                                <i class="bi bi-search"></i> Buscar
                            </button>
                        </div>

                        <!-- Información del Cliente -->
                        <div id="customerInfo" class="mt-2 p-3 bg-light rounded d-none">
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Nombre:</strong> <span id="customerName"></span>
                                </div>
                                <div class="col-md-6">
                                    <strong>Documento:</strong> <span id="customerDoc"></span>
                                </div>
                            </div>
                            <input type="hidden" id="customerId">
                        </div>
                    </div>

                    <!-- Grid de Productos -->
                    <div class="table-responsive">
                        <table class="table table-hover" id="productsTable">
                            <thead class="table-dark">
                                <tr>
                                    <th style="width: 15%">SKU</th>
                                    <th style="width: 35%">Descripción</th>
                                    <th style="width: 12%">Cantidad</th>
                                    <th style="width: 15%">P. Unitario</th>
                                    <th style="width: 15%">Subtotal</th>
                                    <th style="width: 8%">Acción</th>
                                </tr>
                            </thead>
                            <tbody id="productsBody">
                                <!-- Las filas se agregan dinámicamente -->
                            </tbody>
                        </table>
                    </div>

                    <button class="btn btn-success" id="addRowBtn">
                        <i class="bi bi-plus-circle"></i> Agregar Producto
                    </button>
                </div>
            </div>
        </div>

        <!-- Columna Derecha: Resumen y Acciones -->
        <div class="col-lg-4">
            <div class="card shadow-sm sticky-top" style="top: 20px;">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="bi bi-calculator"></i> Resumen</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <div class="d-flex justify-content-between mb-2">
                            <span>Subtotal:</span>
                            <strong>S/ <span id="subtotalAmount">0.00</span></strong>
                        </div>
                        <div class="d-flex justify-content-between mb-2 text-muted">
                            <small>IGV (18% incluido):</small>
                            <small>S/ <span id="taxAmount">0.00</span></small>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between">
                            <h4>TOTAL:</h4>
                            <h4 class="text-success">S/ <span id="totalAmount">0.00</span></h4>
                        </div>
                    </div>

                    <div class="d-grid gap-2">
                        <button class="btn btn-primary btn-lg" id="processSaleBtn" disabled>
                            <i class="bi bi-check-circle"></i> Procesar Venta
                        </button>
                        <button class="btn btn-outline-secondary" id="clearSaleBtn">
                            <i class="bi bi-x-circle"></i> Limpiar
                        </button>
                    </div>

                    <!-- Info adicional -->
                    <div class="mt-4 p-3 bg-light rounded">
                        <small class="text-muted">
                            <i class="bi bi-info-circle"></i> La boleta se enviará automáticamente a SUNAT
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pos.js') }}"></script>
{% endblock %}
```

### 8.3 JavaScript POS

```javascript
// app/static/js/pos.js
class POSSystem {
    constructor() {
        this.customerId = null;
        this.items = [];
        this.rowCounter = 0;

        this.initEventListeners();
        this.addNewRow();
    }

    initEventListeners() {
        // Buscar cliente
        document.getElementById('searchCustomerBtn').addEventListener('click', () => this.searchCustomer());
        document.getElementById('customerSearch').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchCustomer();
        });

        // Agregar fila
        document.getElementById('addRowBtn').addEventListener('click', () => this.addNewRow());

        // Procesar venta
        document.getElementById('processSaleBtn').addEventListener('click', () => this.processSale());

        // Limpiar
        document.getElementById('clearSaleBtn').addEventListener('click', () => this.clearAll());
    }

    async searchCustomer() {
        const docNumber = document.getElementById('customerSearch').value.trim();

        if (!docNumber) {
            Swal.fire('Error', 'Ingrese un documento', 'error');
            return;
        }

        // Validar formato
        if (docNumber.length !== 8 && docNumber.length !== 11) {
            Swal.fire('Error', 'El documento debe tener 8 (DNI) o 11 (RUC) dígitos', 'error');
            return;
        }

        // Bloquear RUC 20 (empresas)
        if (docNumber.startsWith('20')) {
            Swal.fire({
                icon: 'warning',
                title: 'RUC No Permitido',
                text: 'No se puede emitir boleta a empresas (RUC 20). El RUS solo puede emitir a consumidores finales.',
                confirmButtonColor: '#d33'
            });
            return;
        }

        try {
            // Mostrar loading
            Swal.fire({
                title: 'Buscando...',
                allowOutsideClick: false,
                didOpen: () => Swal.showLoading()
            });

            const response = await axios.get(`/api/customers/search?doc=${docNumber}`);

            Swal.close();

            if (response.data.success) {
                this.customerId = response.data.customer.id;
                document.getElementById('customerId').value = this.customerId;
                document.getElementById('customerName').textContent = response.data.customer.name;
                document.getElementById('customerDoc').textContent =
                    `${response.data.customer.document_type} - ${response.data.customer.document_number}`;
                document.getElementById('customerInfo').classList.remove('d-none');

                this.validateForm();
            } else {
                Swal.fire('Error', response.data.message, 'error');
            }
        } catch (error) {
            Swal.close();
            Swal.fire('Error', 'Error al buscar cliente', 'error');
            console.error(error);
        }
    }

    addNewRow() {
        this.rowCounter++;
        const tbody = document.getElementById('productsBody');

        const row = document.createElement('tr');
        row.id = `row-${this.rowCounter}`;
        row.innerHTML = `
            <td>
                <input type="text" class="form-control form-control-sm sku-input"
                       data-row="${this.rowCounter}" placeholder="SKU o buscar">
            </td>
            <td>
                <input type="text" class="form-control form-control-sm"
                       id="desc-${this.rowCounter}" readonly>
                <input type="hidden" id="product-id-${this.rowCounter}">
            </td>
            <td>
                <input type="number" class="form-control form-control-sm quantity-input"
                       id="qty-${this.rowCounter}" min="1" value="1" data-row="${this.rowCounter}">
            </td>
            <td>
                <input type="number" class="form-control form-control-sm price-input"
                       id="price-${this.rowCounter}" step="0.01" min="0" data-row="${this.rowCounter}">
            </td>
            <td>
                <strong>S/ <span id="subtotal-${this.rowCounter}">0.00</span></strong>
            </td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="pos.removeRow(${this.rowCounter})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(row);

        // Event listeners para la nueva fila
        this.attachRowListeners(this.rowCounter);
    }

    attachRowListeners(rowId) {
        // Buscar producto por SKU
        const skuInput = document.querySelector(`input.sku-input[data-row="${rowId}"]`);
        skuInput.addEventListener('blur', () => this.searchProduct(rowId));
        skuInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchProduct(rowId);
        });

        // Calcular subtotal al cambiar cantidad o precio
        document.getElementById(`qty-${rowId}`).addEventListener('input', () => this.calculateRowSubtotal(rowId));
        document.getElementById(`price-${rowId}`).addEventListener('input', () => this.calculateRowSubtotal(rowId));
    }

    async searchProduct(rowId) {
        const sku = document.querySelector(`input.sku-input[data-row="${rowId}"]`).value.trim();

        if (!sku) return;

        try {
            const response = await axios.get(`/api/products/search?sku=${sku}`);

            if (response.data.success) {
                const product = response.data.product;
                document.getElementById(`product-id-${rowId}`).value = product.id;
                document.getElementById(`desc-${rowId}`).value = product.name;
                document.getElementById(`price-${rowId}`).value = product.price;

                this.calculateRowSubtotal(rowId);
            } else {
                Swal.fire('No encontrado', 'Producto no encontrado', 'warning');
            }
        } catch (error) {
            console.error('Error buscando producto:', error);
        }
    }

    calculateRowSubtotal(rowId) {
        const qty = parseFloat(document.getElementById(`qty-${rowId}`).value) || 0;
        const price = parseFloat(document.getElementById(`price-${rowId}`).value) || 0;
        const subtotal = qty * price;

        document.getElementById(`subtotal-${rowId}`).textContent = subtotal.toFixed(2);

        this.calculateTotals();
    }

    calculateTotals() {
        let total = 0;

        document.querySelectorAll('[id^="subtotal-"]').forEach(span => {
            total += parseFloat(span.textContent) || 0;
        });

        // Para RUS: El IGV está incluido
        const subtotal = total / 1.18;
        const tax = total - subtotal;

        document.getElementById('subtotalAmount').textContent = subtotal.toFixed(2);
        document.getElementById('taxAmount').textContent = tax.toFixed(2);
        document.getElementById('totalAmount').textContent = total.toFixed(2);

        this.validateForm();
    }

    removeRow(rowId) {
        document.getElementById(`row-${rowId}`).remove();
        this.calculateTotals();
    }

    validateForm() {
        const hasCustomer = this.customerId !== null;
        const hasProducts = document.querySelectorAll('#productsBody tr').length > 0;
        const hasTotal = parseFloat(document.getElementById('totalAmount').textContent) > 0;

        document.getElementById('processSaleBtn').disabled = !(hasCustomer && hasProducts && hasTotal);
    }

    async processSale() {
        // Recopilar datos de la venta
        const items = [];

        document.querySelectorAll('#productsBody tr').forEach(row => {
            const rowId = row.id.split('-')[1];
            const productId = document.getElementById(`product-id-${rowId}`).value;

            if (productId) {
                items.push({
                    product_id: parseInt(productId),
                    quantity: parseInt(document.getElementById(`qty-${rowId}`).value),
                    unit_price: parseFloat(document.getElementById(`price-${rowId}`).value)
                });
            }
        });

        if (items.length === 0) {
            Swal.fire('Error', 'Debe agregar al menos un producto', 'error');
            return;
        }

        const saleData = {
            customer_id: this.customerId,
            items: items
        };

        // Confirmar venta
        const result = await Swal.fire({
            title: '¿Procesar Venta?',
            html: `
                <p>Total: <strong>S/ ${document.getElementById('totalAmount').textContent}</strong></p>
                <p class="text-muted">Se generará la boleta electrónica y se enviará a SUNAT</p>
            `,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, Procesar',
            cancelButtonText: 'Cancelar'
        });

        if (!result.isConfirmed) return;

        try {
            Swal.fire({
                title: 'Procesando venta...',
                html: 'Generando boleta electrónica y enviando a SUNAT',
                allowOutsideClick: false,
                didOpen: () => Swal.showLoading()
            });

            const response = await axios.post('/api/sales/create', saleData);

            if (response.data.success) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Venta Procesada!',
                    html: `
                        <p>Boleta N°: <strong>${response.data.sale.correlative}</strong></p>
                        <p>Estado SUNAT: <strong>${response.data.sale.sunat_status}</strong></p>
                    `,
                    confirmButtonText: 'Ver PDF'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.open(`/api/sales/${response.data.sale.id}/pdf`, '_blank');
                    }
                });

                this.clearAll();
            } else {
                Swal.fire('Error', response.data.message, 'error');
            }
        } catch (error) {
            Swal.fire('Error', 'Error al procesar la venta', 'error');
            console.error(error);
        }
    }

    clearAll() {
        this.customerId = null;
        document.getElementById('customerSearch').value = '';
        document.getElementById('customerInfo').classList.add('d-none');
        document.getElementById('productsBody').innerHTML = '';
        this.rowCounter = 0;
        this.addNewRow();
        this.calculateTotals();
    }
}

// Inicializar POS
let pos;
document.addEventListener('DOMContentLoaded', function() {
    pos = new POSSystem();
});
```

### 8.4 API Routes

```python
# app/routes/api.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.correlative import Correlative
from app.services.reniec_service import ReniecService
from app.services.rus_control import RUSControlService
from app.services.xml_service import XMLService
from app.services.qr_service import QRService
from app.services.pdf_service import PDFService
from app.services.sunat_service import SunatService
from app.utils.validators import validate_ruc, validate_dni, is_business_ruc
from app import db
from loguru import logger
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/customers/search', methods=['GET'])
@login_required
def search_customer():
    """Busca o crea cliente por DNI/RUC"""
    doc_number = request.args.get('doc', '').strip()

    if not doc_number:
        return jsonify({'success': False, 'message': 'Documento requerido'}), 400

    # Verificar si ya existe en BD
    customer = Customer.query.filter_by(document_number=doc_number).first()

    if customer:
        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'document_type': customer.document_type,
                'document_number': customer.document_number,
                'name': customer.name,
                'address': customer.address,
                'is_business': customer.is_business
            }
        })

    # Si no existe, consultar API externa
    reniec_service = ReniecService()

    if len(doc_number) == 8:
        if not validate_dni(doc_number):
            return jsonify({'success': False, 'message': 'DNI inválido'}), 400

        result = reniec_service.query_dni(doc_number)
    elif len(doc_number) == 11:
        if not validate_ruc(doc_number):
            return jsonify({'success': False, 'message': 'RUC inválido'}), 400

        # Bloquear RUC 20
        if is_business_ruc(doc_number):
            return jsonify({
                'success': False,
                'message': 'No se puede emitir a empresas (RUC 20). Solo consumidores finales.'
            }), 400

        result = reniec_service.query_ruc(doc_number)
    else:
        return jsonify({'success': False, 'message': 'Documento inválido'}), 400

    if not result['success']:
        return jsonify(result), 404

    # Crear cliente en BD
    customer = Customer(
        document_type=result['document_type'],
        document_number=result['document_number'],
        name=result['name'],
        address=result.get('address', ''),
        is_business=result.get('is_business', False)
    )
    db.session.add(customer)
    db.session.commit()

    return jsonify({
        'success': True,
        'customer': {
            'id': customer.id,
            'document_type': customer.document_type,
            'document_number': customer.document_number,
            'name': customer.name,
            'address': customer.address,
            'is_business': customer.is_business
        }
    })

@api_bp.route('/products/search', methods=['GET'])
@login_required
def search_product():
    """Busca producto por SKU"""
    sku = request.args.get('sku', '').strip()

    if not sku:
        return jsonify({'success': False, 'message': 'SKU requerido'}), 400

    product = Product.query.filter_by(sku=sku, is_active=True).first()

    if not product:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404

    return jsonify({
        'success': True,
        'product': {
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'price': float(product.price),
            'stock': product.stock_quantity
        }
    })

@api_bp.route('/sales/create', methods=['POST'])
@login_required
def create_sale():
    """Crea una nueva venta y genera documentos electrónicos"""
    try:
        data = request.get_json()

        customer_id = data.get('customer_id')
        items = data.get('items', [])

        if not customer_id or not items:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

        # Calcular totales
        subtotal = 0
        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'success': False, 'message': f'Producto {item["product_id"]} no encontrado'}), 404

            item['subtotal'] = item['quantity'] * item['unit_price']
            subtotal += item['subtotal']

        total = subtotal  # Para RUS, el precio ya incluye IGV
        tax = total - (total / 1.18)

        # Verificar límite RUS
        rus_service = RUSControlService()
        can_process, message = rus_service.can_process_sale(total)

        if not can_process:
            return jsonify({'success': False, 'message': message}), 403

        # Obtener correlativo
        correlative_model = Correlative.query.filter_by(
            document_type='BOLETA',
            series='B001',
            is_active=True
        ).first()

        if not correlative_model:
            # Crear correlativo inicial
            correlative_model = Correlative(
                document_type='BOLETA',
                series='B001',
                current_number=1
            )
            db.session.add(correlative_model)
            db.session.commit()

        correlative = correlative_model.get_next_correlative()

        # Crear venta
        sale = Sale(
            correlative=correlative,
            document_type='BOLETA',
            customer_id=customer_id,
            seller_id=current_user.id,
            subtotal=subtotal / 1.18,
            tax=tax,
            total=total
        )
        db.session.add(sale)
        db.session.flush()

        # Crear items
        for item_data in items:
            product = Product.query.get(item_data['product_id'])
            item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                subtotal=item_data['subtotal'],
                product_name=product.name,
                product_sku=product.sku
            )
            db.session.add(item)

        db.session.commit()

        # Generar XML
        xml_service = XMLService()
        xml_result = xml_service.generate_boleta_xml(sale)
        sale.xml_path = xml_result['filepath']
        sale.hash = xml_result['hash']

        # Generar QR
        qr_service = QRService()
        qr_result = qr_service.generate_qr(sale)
        sale.qr_code = qr_result['qr_data']

        # Generar PDF
        pdf_service = PDFService()
        pdf_result = pdf_service.generate_boleta_pdf(sale, qr_result['filepath'])
        sale.pdf_path = pdf_result['filepath']

        db.session.commit()

        # Enviar a SUNAT (asíncrono)
        sunat_service = SunatService()
        sunat_result = sunat_service.send_to_sunat(sale.id)

        # Avanzar correlativo solo si SUNAT aceptó
        if sunat_result['success'] and sunat_result['status'] == 'ACCEPTED':
            correlative_model.advance_correlative()

            # Actualizar control RUS
            rus_service.add_sale_amount(float(total))

        db.session.commit()

        logger.info(f"Venta creada: {sale.correlative} por usuario {current_user.username}")

        return jsonify({
            'success': True,
            'sale': {
                'id': sale.id,
                'correlative': sale.correlative,
                'total': float(sale.total),
                'sunat_status': sale.sunat_status,
                'pdf_url': f'/api/sales/{sale.id}/pdf'
            }
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando venta: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/sales/<int:sale_id>/pdf', methods=['GET'])
@login_required
def get_sale_pdf(sale_id):
    """Descarga PDF de una venta"""
    from flask import send_file

    sale = Sale.query.get_or_404(sale_id)

    if not sale.pdf_path:
        return jsonify({'error': 'PDF no disponible'}), 404

    return send_file(sale.pdf_path, as_attachment=True)

@api_bp.route('/rus/status', methods=['GET'])
@login_required
def rus_status():
    """Obtiene el estado actual del control RUS"""
    rus_service = RUSControlService()
    status = rus_service.get_status()
    return jsonify(status)
```

---

## 🎯 FASE 9: Dashboard y Reportes (Semana 5)

### 9.1 Dashboard Principal

```python
# app/routes/dashboard.py
from flask import Blueprint, render_template
from flask_login import login_required
from app.models.sale import Sale
from app.models.rus_control import RUSControl
from app.services.rus_control import RUSControlService
from sqlalchemy import func
from datetime import datetime, timedelta
import calendar

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Estadísticas del mes actual
    now = datetime.utcnow()
    first_day = datetime(now.year, now.month, 1)
    last_day = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])

    # Total ventas del mes
    monthly_sales = db.session.query(func.sum(Sale.total)).filter(
        Sale.created_at >= first_day,
        Sale.created_at <= last_day,
        Sale.is_cancelled == False
    ).scalar() or 0

    # Cantidad de boletas
    monthly_count = Sale.query.filter(
        Sale.created_at >= first_day,
        Sale.created_at <= last_day,
        Sale.is_cancelled == False
    ).count()

    # Control RUS
    rus_service = RUSControlService()
    rus_status = rus_service.get_status()

    # Ventas de los últimos 7 días
    week_ago = now - timedelta(days=7)
    daily_sales = db.session.query(
        func.date(Sale.created_at).label('date'),
        func.sum(Sale.total).label('total'),
        func.count(Sale.id).label('count')
    ).filter(
        Sale.created_at >= week_ago,
        Sale.is_cancelled == False
    ).group_by(func.date(Sale.created_at)).all()

    # Últimas 10 ventas
    recent_sales = Sale.query.filter_by(is_cancelled=False).order_by(
        Sale.created_at.desc()
    ).limit(10).all()

    return render_template('dashboard/index.html',
        monthly_sales=monthly_sales,
        monthly_count=monthly_count,
        rus_status=rus_status,
        daily_sales=daily_sales,
        recent_sales=recent_sales
    )
```

```html
<!-- app/templates/dashboard/index.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container-fluid py-4">
    <h2 class="mb-4">Dashboard</h2>

    <!-- Tarjetas de Resumen -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card bg-primary text-white shadow">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <p class="mb-0">Ventas del Mes</p>
                            <h3>S/ {{ "%.2f"|format(monthly_sales) }}</h3>
                        </div>
                        <div>
                            <i class="bi bi-cash-coin" style="font-size: 3rem; opacity: 0.5;"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card bg-success text-white shadow">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <p class="mb-0">Boletas Emitidas</p>
                            <h3>{{ monthly_count }}</h3>
                        </div>
                        <div>
                            <i class="bi bi-receipt" style="font-size: 3rem; opacity: 0.5;"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-body">
                    <h5 class="card-title">Control RUS</h5>
                    <div class="progress mb-2" style="height: 30px;">
                        <div class="progress-bar
                            {% if rus_status.alert_level == 'RED' %}bg-danger
                            {% elif rus_status.alert_level == 'YELLOW' %}bg-warning
                            {% else %}bg-success{% endif %}"
                            style="width: {{ rus_status.percentage }}%">
                            {{ "%.2f"|format(rus_status.percentage) }}%
                        </div>
                    </div>
                    <div class="d-flex justify-content-between">
                        <small>S/ {{ "%.2f"|format(rus_status.total_invoiced) }} de S/ {{ "%.2f"|format(rus_status.category_2_limit) }}</small>
                        <small>Quedan: S/ {{ "%.2f"|format(rus_status.remaining) }}</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Gráfico de Ventas Semanales -->
    <div class="row mb-4">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header">
                    <h5 class="mb-0">Ventas de los últimos 7 días</h5>
                </div>
                <div class="card-body">
                    <canvas id="salesChart"></canvas>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card shadow">
                <div class="card-header">
                    <h5 class="mb-0">Acciones Rápidas</h5>
                </div>
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <a href="{{ url_for('pos.index') }}" class="btn btn-primary">
                            <i class="bi bi-cart-plus"></i> Nueva Venta
                        </a>
                        <button class="btn btn-outline-secondary" id="syncProductsBtn">
                            <i class="bi bi-arrow-repeat"></i> Sincronizar Productos
                        </button>
                        <a href="{{ url_for('reports.sales') }}" class="btn btn-outline-info">
                            <i class="bi bi-file-earmark-bar-graph"></i> Ver Reportes
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Últimas Ventas -->
    <div class="row">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header">
                    <h5 class="mb-0">Últimas Ventas</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Correlativo</th>
                                    <th>Cliente</th>
                                    <th>Total</th>
                                    <th>Estado SUNAT</th>
                                    <th>Fecha</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for sale in recent_sales %}
                                <tr>
                                    <td><strong>{{ sale.correlative }}</strong></td>
                                    <td>{{ sale.customer.name[:30] }}</td>
                                    <td>S/ {{ "%.2f"|format(sale.total) }}</td>
                                    <td>
                                        <span class="badge
                                            {% if sale.sunat_status == 'ACCEPTED' %}bg-success
                                            {% elif sale.sunat_status == 'REJECTED' %}bg-danger
                                            {% elif sale.sunat_status == 'PENDING' %}bg-warning
                                            {% else %}bg-secondary{% endif %}">
                                            {{ sale.sunat_status }}
                                        </span>
                                    </td>
                                    <td>{{ sale.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                                    <td>
                                        <a href="/api/sales/{{ sale.id }}/pdf" class="btn btn-sm btn-primary" target="_blank">
                                            <i class="bi bi-file-pdf"></i>
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
    // Gráfico de ventas
    const ctx = document.getElementById('salesChart');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ daily_sales|map(attribute='date')|list|tojson }},
            datasets: [{
                label: 'Ventas (S/)',
                data: {{ daily_sales|map(attribute='total')|list|tojson }},
                backgroundColor: 'rgba(13, 110, 253, 0.5)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Sincronizar productos
    document.getElementById('syncProductsBtn').addEventListener('click', async function() {
        const btn = this;
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm"></i> Sincronizando...';

        try {
            const response = await axios.post('/api/products/sync');
            if (response.data.success) {
                Swal.fire('Éxito', `${response.data.synced} productos sincronizados`, 'success');
            }
        } catch (error) {
            Swal.fire('Error', 'Error al sincronizar productos', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-arrow-repeat"></i> Sincronizar Productos';
        }
    });
</script>
{% endblock %}
```

---

## 🎯 FASE 10: Testing (Semana 6)

### 10.1 Configuración de Tests

```python
# tests/conftest.py
import pytest
from app import create_app, db
from app.models.user import User
from app.config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    return app

@pytest.fixture(scope='function')
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    """Database session for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_client(client, session):
    """Authenticated test client"""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='admin'
    )
    user.set_password('testpass123')
    session.add(user)
    session.commit()

    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })

    return client
```

### 10.2 Tests Unitarios

```python
# tests/unit/test_validators.py
from app.utils.validators import validate_ruc, validate_dni, is_business_ruc

def test_validate_dni_valid():
    assert validate_dni('12345678') == True

def test_validate_dni_invalid_length():
    assert validate_dni('123') == False

def test_validate_dni_not_numeric():
    assert validate_dni('1234567A') == False

def test_validate_ruc_valid():
    assert validate_ruc('20123456789') == True

def test_validate_ruc_invalid():
    assert validate_ruc('12345678901') == False

def test_is_business_ruc():
    assert is_business_ruc('20123456789') == True
    assert is_business_ruc('10123456789') == False
```

```python
# tests/unit/test_rus_control.py
from app.services.rus_control import RUSControlService
from app.models.rus_control import RUSControl

def test_can_process_sale_within_limit(app, session):
    with app.app_context():
        service = RUSControlService()
        can_process, message = service.can_process_sale(1000.00)
        assert can_process == True

def test_cannot_process_sale_exceeding_limit(app, session):
    with app.app_context():
        # Crear control con monto cercano al límite
        control = RUSControl(year=2024, month=1, total_invoiced=7900.00)
        session.add(control)
        session.commit()

        service = RUSControlService()
        can_process, message = service.can_process_sale(200.00)
        assert can_process == False
```

### 10.3 Tests de Integración

```python
# tests/integration/test_api_sales.py
import json

def test_create_sale_success(auth_client, session):
    """Test creating a sale successfully"""
    # Crear customer y producto de prueba
    from app.models.customer import Customer
    from app.models.product import Product

    customer = Customer(
        document_type='DNI',
        document_number='12345678',
        name='Test Customer'
    )
    session.add(customer)

    product = Product(
        woo_id=1,
        sku='TEST001',
        name='Test Product',
        price=100.00
    )
    session.add(product)
    session.commit()

    # Crear venta
    response = auth_client.post('/api/sales/create',
        data=json.dumps({
            'customer_id': customer.id,
            'items': [{
                'product_id': product.id,
                'quantity': 2,
                'unit_price': 100.00
            }]
        }),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'sale' in data

def test_create_sale_without_customer(auth_client):
    """Test creating sale without customer fails"""
    response = auth_client.post('/api/sales/create',
        data=json.dumps({
            'items': []
        }),
        content_type='application/json'
    )

    assert response.status_code == 400
```

### 10.4 Comando para Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/
```

---

## 🎯 FASE 11: Deployment con EasyPanel (Semana 6)

### 11.1 Preparación para Producción

```python
# app/config.py - Agregar configuración de producción
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    # Seguridad
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)

    # Force HTTPS
    PREFERRED_URL_SCHEME = 'https'
```

```python
# wsgi.py - Entry point para Gunicorn
from app import create_app
from app.config import ProductionConfig

app = create_app(ProductionConfig)

if __name__ == '__main__':
    app.run()
```

### 11.2 Configuración Gunicorn

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = '0.0.0.0:8000'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = 'logs/gunicorn-access.log'
errorlog = 'logs/gunicorn-error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'izisales'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (si lo maneja Gunicorn directamente, sino deja que Nginx lo maneje)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
```

### 11.3 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs storage/pdf storage/xml storage/cdr storage/backup

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
```

### 11.4 Docker Compose (para desarrollo/testing local)

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql://izisales:password@db:3306/izisales
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=izisales
      - MYSQL_USER=izisales
      - MYSQL_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery_worker:
    build: .
    command: celery -A celery_worker.celery worker --loglevel=info
    environment:
      - DATABASE_URL=mysql://izisales:password@db:3306/izisales
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery_beat:
    build: .
    command: celery -A celery_worker.celery beat --loglevel=info
    environment:
      - DATABASE_URL=mysql://izisales:password@db:3306/izisales
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  mysql_data:
```

### 11.5 Deployment en EasyPanel

**Paso 1: Configuración inicial en el VPS**

```bash
# Conectar al VPS
ssh user@tu-vps-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker si no está instalado
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Paso 2: Instalar EasyPanel**

```bash
# Instalar EasyPanel (según su documentación oficial)
curl -sSL https://get.easypanel.io | sh
```

**Paso 3: Configurar aplicación en EasyPanel**

1. Accede al panel de EasyPanel en tu navegador: `http://tu-vps-ip:3000`
2. Crea un nuevo proyecto: `iziSales`
3. Agrega un servicio tipo **Docker**
4. Configura el servicio:

```yaml
# Configuración en EasyPanel
name: izisales-web
image: custom
build:
  context: .
  dockerfile: Dockerfile
ports:
  - 8000:8000
environment:
  FLASK_ENV: production
  SECRET_KEY: tu-secret-key-super-seguro
  DATABASE_URL: mysql://user:pass@izisales-db:3306/izisales
  REDIS_URL: redis://izisales-redis:6379/0
  # ... resto de variables de entorno
volumes:
  - ./storage:/app/storage
  - ./logs:/app/logs
```

5. Agrega servicio de **MySQL**:

```yaml
name: izisales-db
image: mysql:8.0
environment:
  MYSQL_ROOT_PASSWORD: rootpassword
  MYSQL_DATABASE: izisales
  MYSQL_USER: izisales
  MYSQL_PASSWORD: password
volumes:
  - mysql_data:/var/lib/mysql
```

6. Agrega servicio de **Redis**:

```yaml
name: izisales-redis
image: redis:7-alpine
```

7. Agrega servicio de **Celery Worker**:

```yaml
name: izisales-celery
image: custom
build:
  context: .
  dockerfile: Dockerfile
command: celery -A celery_worker.celery worker --loglevel=info
environment:
  # Mismas variables que web
```

**Paso 4: Configurar Nginx Reverse Proxy (EasyPanel lo hace automático)**

Si EasyPanel no configura automáticamente, configurar manualmente:

```nginx
# /etc/nginx/sites-available/izisales
server {
    listen 80;
    server_name tu-dominio.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 10M;
}
```

**Paso 5: SSL/TLS con Let's Encrypt**

EasyPanel generalmente incluye Let's Encrypt. Si no:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

**Paso 6: Ejecutar Migraciones**

```bash
# Dentro del contenedor web
docker exec -it izisales-web bash
flask db upgrade
```

**Paso 7: Crear usuario admin inicial**

```python
# Script: create_admin.py
from app import create_app, db
from app.models.user import User
from app.config import ProductionConfig

app = create_app(ProductionConfig)

with app.app_context():
    admin = User(
        username='admin',
        email='admin@tuempresa.com',
        full_name='Administrador',
        role='admin'
    )
    admin.set_password('cambiar_password_seguro')
    db.session.add(admin)
    db.session.commit()
    print("Usuario admin creado exitosamente")
```

```bash
docker exec -it izisales-web python create_admin.py
```

### 11.6 Variables de Entorno Producción

```bash
# .env.production (NO SUBIR A GIT)
# Flask
SECRET_KEY=tu-secret-key-super-seguro-y-aleatorio
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=mysql://izisales:password_seguro@localhost:3306/izisales

# Redis
REDIS_URL=redis://localhost:6379/0

# WooCommerce
WOO_URL=https://tu-tienda.com
WOO_CONSUMER_KEY=ck_xxxxxxxxxxxx
WOO_CONSUMER_SECRET=cs_xxxxxxxxxxxx

# PSE/SUNAT
PSE_API_URL=https://api-pse.com
PSE_TOKEN=tu_token_pse

# RENIEC/SUNAT
RENIEC_API_URL=https://api.apis.net.pe
RENIEC_TOKEN=tu_token_apis

# Company
COMPANY_RUC=20123456789
COMPANY_NAME=Tu Empresa SAC
COMPANY_ADDRESS=Av. Principal 123, Lima
COMPANY_UBIGEO=150101
COMPANY_WEBSITE=https://tuempresa.com
```

### 11.7 Script de Deployment

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Iniciando deployment de iziSales..."

# Pull latest changes
git pull origin main

# Build Docker image
docker-compose build

# Stop old containers
docker-compose down

# Start new containers
docker-compose up -d

# Run migrations
docker-compose exec web flask db upgrade

# Restart Celery workers
docker-compose restart celery_worker celery_beat

# Check health
sleep 5
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment completado exitosamente"
```

---

## 🎯 FASE 12: Mantenimiento y Monitoreo (Semana 7+)

### 12.1 Health Check Endpoint

```python
# app/routes/health.py
from flask import Blueprint, jsonify
from app import db
from redis import Redis
from flask import current_app

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint para monitoreo"""
    health_status = {
        'status': 'healthy',
        'checks': {}
    }

    # Check database
    try:
        db.session.execute('SELECT 1')
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Check Redis
    try:
        redis_client = Redis.from_url(current_app.config['REDIS_URL'])
        redis_client.ping()
        health_status['checks']['redis'] = 'ok'
    except Exception as e:
        health_status['checks']['redis'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Check storage directories
    import os
    for path_key in ['PDF_PATH', 'XML_PATH', 'CDR_PATH']:
        path = current_app.config.get(path_key)
        if path and os.path.exists(path) and os.access(path, os.W_OK):
            health_status['checks'][path_key.lower()] = 'ok'
        else:
            health_status['checks'][path_key.lower()] = 'error: not writable'
            health_status['status'] = 'unhealthy'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
```

### 12.2 Backup Automático

```python
# app/tasks/backup_task.py
from celery import shared_task
import subprocess
from datetime import datetime
from flask import current_app
from loguru import logger
import os

@shared_task
def backup_database():
    """Backup automático de la base de datos"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_{timestamp}.sql"
        backup_path = os.path.join(current_app.config['BACKUP_PATH'], backup_file)

        # Extraer credenciales de DATABASE_URL
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        # mysql://user:pass@host:port/dbname

        # Ejecutar mysqldump
        subprocess.run([
            'mysqldump',
            '-u', 'user',
            '-p', 'password',
            'izisales',
            '-r', backup_path
        ], check=True)

        logger.info(f"Backup creado exitosamente: {backup_file}")

        # Comprimir backup
        subprocess.run(['gzip', backup_path], check=True)

        # Eliminar backups antiguos (> 30 días)
        cleanup_old_backups(current_app.config['BACKUP_PATH'], days=30)

        return {'success': True, 'file': f"{backup_file}.gz"}

    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return {'success': False, 'error': str(e)}

def cleanup_old_backups(backup_dir, days=30):
    """Elimina backups antiguos"""
    import time
    now = time.time()
    cutoff = now - (days * 86400)

    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            if os.stat(filepath).st_mtime < cutoff:
                os.remove(filepath)
                logger.info(f"Backup antiguo eliminado: {filename}")
```

### 12.3 Tareas Programadas (Celery Beat)

```python
# celery_worker.py
from celery import Celery
from celery.schedules import crontab
from app import create_app
from app.config import config

flask_app = create_app(config['production'])

celery = Celery(
    flask_app.import_name,
    broker=flask_app.config['CELERY_BROKER_URL'],
    backend=flask_app.config['CELERY_RESULT_BACKEND']
)

celery.conf.update(flask_app.config)

# Configurar tareas programadas
celery.conf.beat_schedule = {
    # Backup diario a las 2 AM
    'daily-backup': {
        'task': 'app.tasks.backup_task.backup_database',
        'schedule': crontab(hour=2, minute=0),
    },
    # Sincronizar productos cada 6 horas
    'sync-products': {
        'task': 'app.tasks.sync_task.sync_woocommerce_products',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Limpiar logs antiguos semanalmente
    'cleanup-logs': {
        'task': 'app.tasks.maintenance_task.cleanup_old_logs',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),
    },
}

celery.conf.timezone = 'America/Lima'

if __name__ == '__main__':
    celery.start()
```

### 12.4 Logging Avanzado

```python
# app/__init__.py - Configurar Loguru
from loguru import logger
import sys
import os

def setup_logging(app):
    """Configurar sistema de logs con Loguru"""

    # Remover handler por defecto
    logger.remove()

    # Console logging (desarrollo)
    if app.config['DEBUG']:
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level="DEBUG"
        )

    # File logging (producción)
    log_path = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_path, exist_ok=True)

    # Logs generales
    logger.add(
        os.path.join(log_path, "izisales_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention="30 days",
        compression="gz",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # Logs de errores
    logger.add(
        os.path.join(log_path, "errors_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention="90 days",
        compression="gz",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"
    )

    # Logs de auditoría (ventas, cambios críticos)
    logger.add(
        os.path.join(log_path, "audit_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention="365 days",  # 1 año por cumplimiento
        compression="gz",
        level="INFO",
        filter=lambda record: "audit" in record["extra"]
    )

    return logger
```

### 12.5 Monitoreo con Sentry (Opcional pero Recomendado)

```python
# app/__init__.py - Integrar Sentry
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

def setup_sentry(app):
    """Configurar Sentry para monitoreo de errores"""
    if not app.config['DEBUG'] and app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                CeleryIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% de transacciones
            environment=app.config['FLASK_ENV'],
            release=app.config.get('APP_VERSION', '1.0.0')
        )
```

### 12.6 Script de Mantenimiento

```bash
#!/bin/bash
# maintenance.sh - Script de mantenimiento semanal

echo "🔧 Iniciando tareas de mantenimiento..."

# Limpiar logs antiguos
echo "📁 Limpiando logs antiguos..."
find /app/logs -name "*.log.gz" -mtime +90 -delete

# Optimizar base de datos
echo "🗄️ Optimizando base de datos..."
docker-compose exec db mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "OPTIMIZE TABLE izisales.sales, izisales.sale_items, izisales.customers, izisales.products, izisales.audit_logs;"

# Limpiar cache de Redis
echo "🗑️ Limpiando cache expirado..."
docker-compose exec redis redis-cli FLUSHDB

# Verificar espacio en disco
echo "💾 Verificando espacio en disco..."
df -h /app/storage

# Verificar salud de servicios
echo "🏥 Verificando salud de servicios..."
curl -f http://localhost:8000/health || echo "⚠️ Servicio web no responde"

echo "✅ Mantenimiento completado"
```

### 12.7 Alertas y Notificaciones

```python
# app/services/notification_service.py
import requests
from flask import current_app
from loguru import logger

class NotificationService:
    """Servicio para enviar notificaciones (Slack, Email, SMS)"""

    @staticmethod
    def send_slack_alert(message, level='warning'):
        """Envía alerta a Slack"""
        webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')
        if not webhook_url:
            return

        color = {
            'info': '#36a64f',
            'warning': '#ff9800',
            'error': '#f44336'
        }.get(level, '#808080')

        payload = {
            "attachments": [{
                "color": color,
                "title": "iziSales Alert",
                "text": message,
                "footer": "iziSales Monitoring",
                "ts": int(datetime.now().timestamp())
            }]
        }

        try:
            requests.post(webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Error enviando alerta a Slack: {e}")

    @staticmethod
    def alert_rus_limit(percentage):
        """Alerta cuando se acerca el límite RUS"""
        if percentage >= 90:
            message = f"🚨 CRÍTICO: Has alcanzado el {percentage}% del límite RUS mensual"
            NotificationService.send_slack_alert(message, 'error')
        elif percentage >= 75:
            message = f"⚠️ ALERTA: Has alcanzado el {percentage}% del límite RUS mensual"
            NotificationService.send_slack_alert(message, 'warning')
```

---

## 📚 Documentación Adicional

### Comandos Útiles

```bash
# Desarrollo
flask run --debug

# Migraciones
flask db migrate -m "Descripción"
flask db upgrade
flask db downgrade

# Celery
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f web
docker-compose exec web bash

# Backup manual
./maintenance.sh

# Deployment
./deploy.sh
```

### Estructura Final de Archivos

```
iziSales/
├── app/
├── tests/
├── logs/
├── storage/
├── migrations/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── gunicorn.conf.py
├── wsgi.py
├── celery_worker.py
├── create_admin.py
├── deploy.sh
├── maintenance.sh
├── .env.example
├── .env.production (no subir a git)
├── .gitignore
└── README.md
```

---

## ✅ Checklist Final de Deployment

- [ ] Variables de entorno configuradas en producción
- [ ] Base de datos creada y migrada
- [ ] Usuario admin creado
- [ ] SSL/TLS configurado (HTTPS)
- [ ] Backup automático configurado
- [ ] Logs configurados y rotando
- [ ] Health check funcionando
- [ ] Celery workers corriendo
- [ ] Redis operativo
- [ ] Sincronización con WooCommerce probada
- [ ] API de RENIEC/SUNAT configurada
- [ ] PSE/SUNAT configurado y probado
- [ ] Límites RUS configurados correctamente
- [ ] PDFs generándose correctamente
- [ ] XMLs válidos según UBL 2.1
- [ ] QR codes generándose
- [ ] Monitoreo activo (Sentry opcional)
- [ ] Firewall configurado en VPS
- [ ] Backups funcionando
- [ ] Documentación actualizada

---

## 🎓 Recursos y Referencias

- **Flask**: https://flask.palletsprojects.com/
- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Celery**: https://docs.celeryq.dev/
- **SUNAT UBL 2.1**: https://cpe.sunat.gob.pe/
- **EasyPanel**: https://easypanel.io/docs
- **Docker**: https://docs.docker.com/

---

## 📞 Soporte y Mantenimiento

Para soporte o consultas:
- Email: soporte@tuempresa.com
- Documentación: /docs
- Logs: /logs

---

**Versión**: 1.0.0
**Última actualización**: 2024
**Desarrollado con**: Flask + Bootstrap + ❤️
