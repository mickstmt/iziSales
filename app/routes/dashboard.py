"""
Rutas del Dashboard
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app import db
from app.utils.decorators import login_required
from app.models.sale import Sale
from app.models.rus_control import RUSControl
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    # Obtener estadísticas básicas
    today = datetime.utcnow().date()

    # Total de ventas del día
    today_sales = Sale.query.filter(
        db.func.date(Sale.created_at) == today,
        Sale.status != 'cancelled'
    ).count()

    # Control RUS del mes actual
    rus_control = RUSControl.get_or_create_current()

    context = {
        'today_sales': today_sales,
        'rus_control': rus_control,
        'user': current_user
    }

    return render_template('dashboard/index.html', **context)
