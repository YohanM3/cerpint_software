class TablaController:
    """Conecta la lista de datos del Modelo con la Vista."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista

    def cargar_datos(self, nuevas_filas: list):
        """Actualiza el Modelo y refresca la Vista."""
        self.modelo.actualizar_datos(nuevas_filas)
        self.vista.Insertar_filas(nuevas_filas)

    def obtener_seleccion(self):  # <--- Se agregó self aquí
        """Retorna la fila que el usuario seleccionó con el clic."""
        item_seleccionado = self.vista.tabla.selection()
        if item_seleccionado:
            return self.vista.tabla.item(item_seleccionado[0])["values"]
        return None
