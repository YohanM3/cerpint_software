import sqlite3


class ValidacionError(ValueError):
    """Indica que los datos no cumplen las reglas del negocio."""


class RegistroNoEncontradoError(LookupError):
    """Indica que el registro seleccionado ya no existe."""


class InventarioInsuficienteError(RuntimeError):
    """Indica que el stock disponible no alcanza para la venta."""

    def __init__(self, codigo: str, stock_disponible: int):
        self.codigo = codigo
        self.stock_disponible = stock_disponible
        super().__init__(
            f"Stock insuficiente para {codigo}; disponible: {stock_disponible}."
        )


def mensaje_error_sqlite(error: sqlite3.Error) -> str:
    detalle = str(error).lower()
    if isinstance(error, sqlite3.IntegrityError):
        if "foreign key" in detalle:
            return "El registro está asociado a ventas existentes y no se puede borrar ni cambiar su clave."
        if "unique" in detalle:
            return "Ya existe un registro con esa clave."
        return "La base de datos rechazó los datos por una regla de integridad."
    if isinstance(error, sqlite3.OperationalError) and "locked" in detalle:
        return (
            "La base de datos está ocupada. Espera unos segundos e inténtalo de nuevo."
        )
    return "No se pudo completar la operación en la base de datos. Verifica el archivo y vuelve a intentarlo."
