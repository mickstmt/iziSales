"""
Funciones auxiliares y utilidades
"""
from flask import flash, redirect, url_for
from functools import wraps
import secrets


def generate_secret_key(length: int = 32) -> str:
    """Genera una clave secreta aleatoria"""
    return secrets.token_urlsafe(length)


def flash_errors(form):
    """
    Muestra errores de un formulario WTForms

    Args:
        form: Formulario WTForms
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'danger')


def get_or_404(model, id):
    """
    Obtiene un objeto o retorna 404

    Args:
        model: Modelo SQLAlchemy
        id: ID del objeto

    Returns:
        object: Objeto encontrado

    Raises:
        404: Si no se encuentra
    """
    obj = model.query.get(id)
    if not obj:
        from flask import abort
        abort(404)
    return obj


def paginate(query, page: int = 1, per_page: int = 20):
    """
    Pagina una consulta SQLAlchemy

    Args:
        query: Query SQLAlchemy
        page: Número de página
        per_page: Items por página

    Returns:
        Pagination: Objeto de paginación
    """
    return query.paginate(page=page, per_page=per_page, error_out=False)
