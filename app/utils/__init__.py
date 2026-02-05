"""
Utilidades del Sistema
"""
from app.utils.validators import (
    validate_ruc,
    validate_dni,
    is_business_ruc,
    validate_email,
    validate_phone,
    validate_correlative,
    sanitize_string,
    format_ruc_display,
    format_money
)

from app.utils.helpers import (
    generate_secret_key,
    flash_errors,
    get_or_404,
    paginate
)

from app.utils.constants import (
    DOCUMENT_TYPES,
    USER_ROLES,
    SUNAT_STATUS,
    RUS_ALERT_LEVELS,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES
)

from app.utils.decorators import (
    login_required,
    role_required,
    admin_required,
    active_user_required
)

__all__ = [
    # Validators
    'validate_ruc',
    'validate_dni',
    'is_business_ruc',
    'validate_email',
    'validate_phone',
    'validate_correlative',
    'sanitize_string',
    'format_ruc_display',
    'format_money',
    # Helpers
    'generate_secret_key',
    'flash_errors',
    'get_or_404',
    'paginate',
    # Constants
    'DOCUMENT_TYPES',
    'USER_ROLES',
    'SUNAT_STATUS',
    'RUS_ALERT_LEVELS',
    'SUCCESS_MESSAGES',
    'ERROR_MESSAGES',
    # Decorators
    'login_required',
    'role_required',
    'admin_required',
    'active_user_required',
]
