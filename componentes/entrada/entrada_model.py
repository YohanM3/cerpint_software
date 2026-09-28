class EntradaModel:
    """Guarda los datos e información interna de la caja de texto."""

    def __init__(self, texto_inicial: str = "", es_valido: bool = True):
        self.valor = texto_inicial
        self.es_valido = es_valido

    def actualizar_valor(self, nuevo_texto: str):
        """Actualiza el dato almacenado."""
        self.valor = nuevo_texto
