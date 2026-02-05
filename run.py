"""
iziSales - Entry Point
Sistema de Facturación Electrónica RUS

Para iniciar en desarrollo:
    python run.py

Para iniciar con Flask CLI:
    flask run --debug
"""
from app import create_app
from app.config import config
import os

# Crear instancia de la aplicación
env = os.getenv('FLASK_ENV', 'development')
app = create_app(config[env])

if __name__ == '__main__':
    # Configuración para desarrollo
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    print("=" * 60)
    print(f"🚀 iziSales v{app.config.get('APP_VERSION', '1.0.0')}")
    print(f"📍 Entorno: {env}")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"🔧 Debug: {debug}")
    print("=" * 60)

    app.run(
        host=host,
        port=port,
        debug=debug
    )
