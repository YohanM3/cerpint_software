class EntradaController:
    """Conecta los datos y la vista de la caja de texto."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista

    def guardar_valor(self):
        """Lee el texto escrito en la Vista y lo guarda en el Modelo."""
        texto_actual = self.vista.obtener_texto()
        self.modelo.actualizar_valor(texto_actual)
        return texto_actual

    def limpiar_campo(self):
        """Limpia el texto en el Modelo y en la Vista."""
        self.modelo.actualizar_valor("")
        self.vista.limpiar()
