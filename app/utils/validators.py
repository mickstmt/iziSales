"""
Validadores y utilidades para validación de datos
"""
import re
from typing import Tuple


def validate_ruc(ruc: str) -> bool:
    """
    Valida formato de RUC peruano

    Args:
        ruc: Número de RUC a validar

    Returns:
        bool: True si es válido, False si no
    """
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


def validate_dni(dni: str) -> bool:
    """
    Valida formato de DNI peruano

    Args:
        dni: Número de DNI a validar

    Returns:
        bool: True si es válido, False si no
    """
    if not dni or len(dni) != 8:
        return False
    return dni.isdigit()


def is_business_ruc(ruc: str) -> Tuple[bool, str]:
    """
    Verifica si el RUC corresponde a Persona Jurídica (RUC 20)

    Args:
        ruc: Número de RUC

    Returns:
        Tuple[bool, str]: (es_empresa, tipo)
    """
    if not validate_ruc(ruc):
        return False, "INVALID"

    if ruc.startswith('20'):
        return True, "PERSONA_JURIDICA"
    elif ruc.startswith('10'):
        return False, "PERSONA_NATURAL"
    elif ruc.startswith('15'):
        return False, "PERSONA_NATURAL"  # RUC público
    elif ruc.startswith('17'):
        return False, "PERSONA_NATURAL"  # RUC extranjero
    else:
        return False, "OTRO"


def validate_email(email: str) -> bool:
    """
    Valida formato de email

    Args:
        email: Email a validar

    Returns:
        bool: True si es válido, False si no
    """
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Valida formato de teléfono peruano

    Args:
        phone: Teléfono a validar

    Returns:
        bool: True si es válido, False si no
    """
    if not phone:
        return False

    # Limpiar caracteres
    clean_phone = re.sub(r'[^\d]', '', phone)

    # Teléfono peruano: 9 dígitos (celular) o 7 dígitos (fijo)
    return len(clean_phone) in [7, 9] and clean_phone.isdigit()


def validate_correlative(correlative: str) -> Tuple[bool, str]:
    """
    Valida formato de correlativo (B001-00000001)

    Args:
        correlative: Correlativo a validar

    Returns:
        Tuple[bool, str]: (es_valido, mensaje)
    """
    if not correlative:
        return False, "Correlativo vacío"

    pattern = r'^[BFN]\d{3}-\d{8}$'
    if not re.match(pattern, correlative):
        return False, "Formato inválido. Debe ser B001-00000001"

    return True, "OK"


def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    Limpia y sanitiza una cadena de texto

    Args:
        text: Texto a limpiar
        max_length: Longitud máxima

    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""

    # Eliminar espacios extras
    text = ' '.join(text.split())

    # Truncar si es necesario
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def format_ruc_display(ruc: str) -> str:
    """
    Formatea RUC para mostrar

    Args:
        ruc: RUC a formatear

    Returns:
        str: RUC formateado (XX-XXXXXXXXX)
    """
    if not ruc or len(ruc) != 11:
        return ruc

    return f"{ruc[:2]}-{ruc[2:]}"


def format_money(amount: float) -> str:
    """
    Formatea monto de dinero

    Args:
        amount: Monto a formatear

    Returns:
        str: Monto formateado (S/ 1,234.56)
    """
    return f"S/ {amount:,.2f}"
