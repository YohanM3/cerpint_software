# componentes/tabla/tabla_model.py


class TablaModel:
    """Guarda las columnas y las filas de datos de la tabla."""

    def __init__(self, columnas: list):
        self.columnas = columnas  # Ej: ["Código", "Producto", "Precio"]
        self.datos = []  # Lista de filas

    def actualizar_datos(self, nuevos_datos: list):
        """Reemplaza los datos actuales por unos nuevos."""
        self.datos = nuevos_datos
