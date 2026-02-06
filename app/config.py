"""
iziSales - Configuración de la Aplicación
Configuraciones para diferentes entornos (Development, Production, Testing)
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    """Configuración base compartida por todos los entornos"""

    # ==============================================
    # FLASK CORE
    # ==============================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # ==============================================
    # DATABASE
    # ==============================================
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/izisales'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # ==============================================
    # REDIS
    # ==============================================
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # ==============================================
    # CACHE
    # ==============================================
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300

    # ==============================================
    # SESSION
    # ==============================================
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('PERMANENT_SESSION_LIFETIME', 28800))  # 8 horas por defecto
    )

    # ==============================================
    # CELERY
    # ==============================================
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'America/Lima'
    CELERY_ENABLE_UTC = True

    # ==============================================
    # WOOCOMMERCE
    # ==============================================
    WOO_URL = os.getenv('WOO_URL')
    WOO_CONSUMER_KEY = os.getenv('WOO_CONSUMER_KEY')
    WOO_CONSUMER_SECRET = os.getenv('WOO_CONSUMER_SECRET')
    WOO_VERSION = 'wc/v3'
    WOO_TIMEOUT = 30

    # ==============================================
    # PSE/SUNAT
    # ==============================================
    PSE_API_URL = os.getenv('PSE_API_URL')
    PSE_TOKEN = os.getenv('PSE_TOKEN')
    PSE_SANDBOX_MODE = os.getenv('PSE_SANDBOX_MODE', 'True').lower() == 'true'
    PSE_TIMEOUT = 30

    # ==============================================
    # RENIEC/SUNAT APIs
    # ==============================================
    RENIEC_API_URL = os.getenv('RENIEC_API_URL', 'https://api.apis.net.pe/v2')
    RENIEC_TOKEN = os.getenv('RENIEC_TOKEN')

    # ==============================================
    # COMPANY INFORMATION (RUS)
    # ==============================================
    COMPANY_RUC = os.getenv('COMPANY_RUC')
    COMPANY_NAME = os.getenv('COMPANY_NAME')
    COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS')
    COMPANY_UBIGEO = os.getenv('COMPANY_UBIGEO', '150101')
    COMPANY_WEBSITE = os.getenv('COMPANY_WEBSITE')

    # ==============================================
    # RUS LIMITS (en Soles)
    # ==============================================
    RUS_LIMIT_CATEGORY_1 = float(os.getenv('RUS_LIMIT_CATEGORY_1', 5000.00))
    RUS_LIMIT_CATEGORY_2 = float(os.getenv('RUS_LIMIT_CATEGORY_2', 8000.00))

    # ==============================================
    # STORAGE PATHS
    # ==============================================
    STORAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'storage')
    PDF_PATH = os.path.join(STORAGE_PATH, 'pdf')
    XML_PATH = os.path.join(STORAGE_PATH, 'xml')
    CDR_PATH = os.path.join(STORAGE_PATH, 'cdr')
    BACKUP_PATH = os.path.join(STORAGE_PATH, 'backup')

    # ==============================================
    # FILE UPLOADS
    # ==============================================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'xml', 'png', 'jpg', 'jpeg'}

    # ==============================================
    # SECURITY
    # ==============================================
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # ==============================================
    # PAGINATION
    # ==============================================
    ITEMS_PER_PAGE = 20

    # ==============================================
    # EMAIL (Optional)
    # ==============================================
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@izisales.com')

    # ==============================================
    # SENTRY (Monitoring)
    # ==============================================
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    # ==============================================
    # SLACK NOTIFICATIONS
    # ==============================================
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

    # ==============================================
    # APPLICATION
    # ==============================================
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # ==============================================
    # TIMEZONE
    # ==============================================
    TIMEZONE = 'America/Lima'


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Mostrar queries SQL en consola

    # Session menos restrictiva en desarrollo
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

    # Seguridad mejorada en producción
    SESSION_COOKIE_SECURE = True  # Solo cookies por HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)

    # Force HTTPS
    PREFERRED_URL_SCHEME = 'https'

    # Bcrypt más fuerte en producción
    BCRYPT_LOG_ROUNDS = 13

    # Cache más largo en producción
    CACHE_DEFAULT_TIMEOUT = 600


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True

    # Base de datos de prueba (SQLite in-memory por defecto para portabilidad)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite://'
    )

    # Desactivar opciones de pool incompatibles con SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # Desactivar CSRF en tests
    WTF_CSRF_ENABLED = False

    # Bcrypt más rápido en tests
    BCRYPT_LOG_ROUNDS = 4

    # Cache en memoria para tests
    CACHE_TYPE = 'simple'

    # Session en memoria para tests
    SESSION_TYPE = 'filesystem'


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
