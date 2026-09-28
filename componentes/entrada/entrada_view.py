import customtkinter as ctk
from config.estilos import COLOR_PRIMARIO, COLOR_TEXTO_OSCURO, FUENTE_ENTRADA


class EntradaView(ctk.CTkEntry):
    """Maneja la parte gráfica del campo de texto."""

    def __init__(self, master, placeholder="", **kwargs):
        ancho = kwargs.pop("width", 220)
        alto = kwargs.pop("height", 35)
        radio = kwargs.pop("corner_radius", 6)
        color_borde = kwargs.pop("border_color", COLOR_PRIMARIO)
        color_fondo = kwargs.pop("fg_color", "#FFFFFF")
        color_texto = kwargs.pop("text_color", COLOR_TEXTO_OSCURO)
        fuente = kwargs.pop(
            "font", ctk.CTkFont(family=FUENTE_ENTRADA[0], size=FUENTE_ENTRADA[1])
        )

        super().__init__(
            master=master,
            placeholder_text=placeholder,
            width=ancho,
            height=alto,
            corner_radius=radio,
            border_color=color_borde,
            fg_color=color_fondo,
            text_color=color_texto,
            font=fuente,
            **kwargs
        )

    def obtener_texto(self) -> str:
        """Devuelve lo que el usuario escribió en la pantalla."""
        return self.get()

    def limpiar(self):
        """Borra el contenido de la caja de texto."""
        self.delete(0, "end")

    def establecer_texto(self, texto: str):
        """Escribe un texto directamente en la caja."""
        self.limpiar()
        self.insert(0, texto)
