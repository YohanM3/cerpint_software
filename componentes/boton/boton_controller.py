class BotonController:
    """Conecta el Modelo y la Vista del botón."""

    def __init__(self, modelo, vista, funcion_accion=None):
        self.modelo = modelo
        self.vista = vista
        self.funcion_accion = funcion_accion

        self.vista.configure(command=self.procesar_clic)

    def procesar_clic(self):
        """Se ejecuta al presionar el botón."""
        if not self.modelo.habilitado:
            return

        self.modelo.registrar_clic()

        if callable(self.funcion_accion):
            self.funcion_accion()

    def desactivar(self):
        """Desactiva el modelo y la vista."""
        self.modelo.habilitado = False
        self.vista.cambiar_estado(activo=False)

    def activar(self):
        """Activa el modelo y la vista."""
        self.modelo.habilitado = True
        self.vista.cambiar_estado(activo=True)
