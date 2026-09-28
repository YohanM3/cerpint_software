import customtkinter as ctk
from config.estilos import (
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
    COLOR_TEXTO_BLANCO,
    FUENTE_BOTON,
)
from componentes.boton.boton_controller import BotonController
from componentes.boton.boton_model import BotonModel


class BotonView(ctk.CTkButton):
    """Maneja únicamente la apariencia gráfica del botón."""

    def __init__(self, master, texto="Botón", command=None, **kwargs):
        estado = kwargs.get("state", "normal")
        # Extraemos los argumentos de estilo para no duplicarlos en kwargs
        ancho = kwargs.pop("width", 160)
        alto = kwargs.pop("height", 40)
        radio = kwargs.pop("corner_radius", 8)
        color_fondo = kwargs.pop("fg_color", COLOR_PRIMARIO)
        color_hover = kwargs.pop("hover_color", COLOR_PRIMARIO_HOVER)
        color_texto = kwargs.pop("text_color", COLOR_TEXTO_BLANCO)
        fuente = kwargs.pop(
            "font",
            ctk.CTkFont(
                family=FUENTE_BOTON[0], size=FUENTE_BOTON[1], weight=FUENTE_BOTON[2]
            ),
        )

        super().__init__(
            master=master,
            text=texto,
            command=command,  # Usamos 'command' en inglés directamente
            width=ancho,
            height=alto,
            corner_radius=radio,
            fg_color=color_fondo,
            hover_color=color_hover,
            text_color=color_texto,
            font=fuente,
            **kwargs
        )

        self.modelo = BotonModel(texto, habilitado=(estado != "disabled"))
        self.controlador = BotonController(self.modelo, self, command)

    def configure(self, **kwargs):
        if hasattr(self, "controlador") and "command" in kwargs:
            accion = kwargs["command"]
            if accion != self.controlador.procesar_clic:
                self.controlador.funcion_accion = accion
            kwargs["command"] = self.controlador.procesar_clic
        return super().configure(**kwargs)

    config = configure

    def cambiar_estado(self, activo: bool):
        """Cambia el aspecto visual entre activo y deshabilitado."""
        self.modelo.habilitado = activo
        self.configure(state="normal" if activo else "disabled")

    def actualizar_texto(self, nuevo_texto: str):
        """Cambia el texto que se dibuja en pantalla."""
        self.modelo.texto = nuevo_texto
        self.configure(text=nuevo_texto)
