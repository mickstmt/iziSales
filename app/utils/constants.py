"""
Constantes del sistema
"""

# Tipos de documento
DOCUMENT_TYPES = {
    'DNI': 'DNI',
    'RUC': 'RUC',
    'CE': 'Carné de Extranjería',
    'PASAPORTE': 'Pasaporte'
}

# Roles de usuario
USER_ROLES = {
    'admin': 'Administrador',
    'seller': 'Vendedor',
    'viewer': 'Visualizador'
}

# Estados SUNAT
SUNAT_STATUS = {
    'PENDING': 'Pendiente',
    'ACCEPTED': 'Aceptado',
    'REJECTED': 'Rechazado',
    'ERROR': 'Error'
}

# Niveles de alerta RUS
RUS_ALERT_LEVELS = {
    'GREEN': 'Normal',
    'YELLOW': 'Alerta',
    'RED': 'Crítico'
}

# Tipos de documento electrónico
ELECTRONIC_DOCUMENT_TYPES = {
    'BOLETA': '03',
    'FACTURA': '01',
    'NOTA_CREDITO': '07',
    'NOTA_DEBITO': '08'
}

# Códigos SUNAT comunes
SUNAT_CODES = {
    '0': 'Aceptado',
    '0100': 'Comprobante aceptado',
    '2000': 'Comprobante rechazado por error en formato',
    '2001': 'Comprobante rechazado por error en firma digital',
    '2100': 'Comprobante rechazado por inconsistencia en datos',
}

# Mensajes de éxito
SUCCESS_MESSAGES = {
    'login': 'Sesión iniciada exitosamente',
    'logout': 'Sesión cerrada exitosamente',
    'sale_created': 'Venta registrada exitosamente',
    'sale_cancelled': 'Venta cancelada exitosamente',
    'product_synced': 'Productos sincronizados exitosamente',
}

# Mensajes de error
ERROR_MESSAGES = {
    'login_failed': 'Usuario o contraseña incorrectos',
    'unauthorized': 'No tienes permiso para acceder a esta página',
    'rus_limit_exceeded': 'Límite RUS superado. No se pueden emitir más boletas este mes',
    'invalid_ruc_20': 'No se puede emitir boleta a empresas (RUC 20). El RUS solo permite emitir a consumidores finales',
}
