"""
iziSales - Sistema de Facturación Electrónica RUS
Flask Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from loguru import logger
import sys
import os
from datetime import timedelta

# Inicializar extensiones (sin app context)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()
bcrypt = Bcrypt()


def create_app(config_class=None):
    """
    Application Factory Pattern

    Args:
        config_class: Clase de configuración (DevelopmentConfig, ProductionConfig, etc.)

    Returns:
        app: Instancia de Flask configurada
    """
    app = Flask(__name__)

    # Cargar configuración
    if config_class is None:
        from app.config import config
        env = os.getenv('FLASK_ENV', 'development')
        config_class = config.get(env, config['development'])

    app.config.from_object(config_class)

    # Inicializar extensiones con app context
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    bcrypt.init_app(app)

    # Importar modelos para que Alembic los detecte
    with app.app_context():
        from app import models  # noqa: F401

    # Configurar Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Configurar Logging
    setup_logging(app)

    # Configurar Sentry (si está disponible)
    if not app.config['DEBUG'] and app.config.get('SENTRY_DSN'):
        setup_sentry(app)

    # Crear directorios necesarios
    create_directories(app)

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Ruta raíz
    @app.route('/')
    def index():
        """Ruta raíz - redirige a login o dashboard según autenticación"""
        from flask import redirect, url_for
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Registrar Blueprints
    register_blueprints(app)

    # Registrar comandos CLI
    register_commands(app)

    # Registrar manejadores de errores
    register_error_handlers(app)

    # Context processors
    register_context_processors(app)

    logger.info(f"iziSales iniciado en modo: {app.config['FLASK_ENV']}")

    return app


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

    # File logging (producción y desarrollo)
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


def setup_sentry(app):
    """Configurar Sentry para monitoreo de errores en producción"""
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

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
        logger.info("Sentry configurado exitosamente")
    except Exception as e:
        logger.warning(f"No se pudo configurar Sentry: {e}")


def create_directories(app):
    """Crear directorios necesarios para storage"""
    directories = [
        app.config.get('PDF_PATH'),
        app.config.get('XML_PATH'),
        app.config.get('CDR_PATH'),
        app.config.get('BACKUP_PATH'),
        os.path.join(app.config.get('PDF_PATH'), 'qr'),
    ]

    for directory in directories:
        if directory:
            os.makedirs(directory, exist_ok=True)

    logger.debug("Directorios de storage creados/verificados")


def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""

    # Blueprint de autenticación
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Blueprint de dashboard
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # Blueprint de POS (Punto de Venta)
    from app.routes.pos import pos_bp
    app.register_blueprint(pos_bp)

    # Blueprint de clientes
    from app.routes.customers import customers_bp
    app.register_blueprint(customers_bp)

    # Blueprint de usuarios
    from app.routes.users import users_bp
    app.register_blueprint(users_bp)

    # Blueprint de API
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    # Blueprint de reportes
    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp)

    # Blueprint de ventas
    from app.routes.sales import sales_bp
    app.register_blueprint(sales_bp)

    # Blueprint de health check
    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    logger.debug("Blueprints registrados exitosamente")


def register_commands(app):
    """Registrar comandos CLI personalizados"""

    @app.cli.command('init-db')
    def init_db():
        """Inicializar la base de datos"""
        db.create_all()
        logger.info("Base de datos inicializada")
        print("✅ Base de datos inicializada exitosamente")

    @app.cli.command('create-admin')
    def create_admin():
        """Crear usuario administrador"""
        from app.models.user import User

        username = input("Username: ")
        email = input("Email: ")
        full_name = input("Nombre completo: ")
        password = input("Password: ")

        admin = User(
            username=username,
            email=email,
            full_name=full_name,
            role='admin'
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        logger.info(f"Usuario admin creado: {username}")
        print(f"✅ Usuario admin '{username}' creado exitosamente")

    @app.cli.command('sync-products')
    def sync_products():
        """Sincronizar productos desde WooCommerce"""
        from app.services.woocommerce_service import WooCommerceService

        service = WooCommerceService()
        count = service.sync_products_to_local()

        logger.info(f"Productos sincronizados: {count}")
        print(f"✅ {count} productos sincronizados desde WooCommerce")

    @app.cli.command('init-correlatives')
    def init_correlatives():
        """Inicializar correlativos de documentos"""
        from app.models.correlative import Correlative

        # Crear correlativo para boletas
        boleta = Correlative(
            document_type='BOLETA',
            series='B001',
            current_number=1,
            is_active=True
        )
        db.session.add(boleta)
        db.session.commit()

        logger.info("Correlativos inicializados")
        print("✅ Correlativos inicializados (B001-00000001)")


def register_error_handlers(app):
    """Registrar manejadores de errores personalizados"""

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        logger.error(f"Error 500: {error}")
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403


def register_context_processors(app):
    """Registrar context processors para templates"""

    @app.context_processor
    def inject_app_version():
        """Inyectar versión de la app en todos los templates"""
        return dict(app_version=app.config.get('APP_VERSION', '1.0.0'))

    @app.context_processor
    def inject_company_info():
        """Inyectar información de la empresa en todos los templates"""
        return dict(
            company_name=app.config.get('COMPANY_NAME', ''),
            company_ruc=app.config.get('COMPANY_RUC', '')
        )
