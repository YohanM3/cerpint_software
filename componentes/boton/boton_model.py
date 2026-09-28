# componentes/boton/boton_model.py


class BotonModel:
    """Guarda únicamente los datos y el estado del botón."""

    def __init__(self, texto: str = "Botón", habilitado: bool = True):
        self.texto = texto
        self.habilitado = habilitado
        self.contador_clics = 0

    def registrar_clic(self):
        """Suma un clic al contador de datos."""
        self.contador_clics += 1
