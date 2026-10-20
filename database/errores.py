import mysql.connector


class ValidacionError(ValueError):
    """Indica que los datos no cumplen las reglas del negocio."""


class RegistroNoEncontradoError(LookupError):
    """Indica que el registro seleccionado ya no existe."""


class PermisoError(PermissionError):
    """Indica que el usuario actual no puede realizar la operación."""


class InventarioInsuficienteError(RuntimeError):
    """Indica que el stock disponible no alcanza para la venta."""

    def __init__(self, codigo: str, stock_disponible: int):
        self.codigo = codigo
        self.stock_disponible = stock_disponible
        super().__init__(
            f"Stock insuficiente para {codigo}; disponible: {stock_disponible}."
        )


DatabaseError = mysql.connector.Error


def mensaje_error_base_datos(error: mysql.connector.Error) -> str:
    """Traduce errores de MySQL/MariaDB a mensajes aptos para la interfaz."""
    if isinstance(error, mysql.connector.IntegrityError):
        detalle = str(error).lower()
        if "foreign key" in detalle:
            return "El registro está asociado a información existente y no se puede borrar ni cambiar su clave."
        if "duplicate" in detalle or "unique" in detalle:
            return "Ya existe un registro con esa clave."
        return "La base de datos rechazó los datos por una regla de integridad."
    if isinstance(error, mysql.connector.OperationalError):
        return "No se pudo conectar a MySQL/MariaDB. Verifica el servicio y la configuración local."
    return "No se pudo completar la operación en MySQL/MariaDB."
