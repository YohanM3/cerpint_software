import customtkinter as ctk

from componentes.boton.boton_view import BotonView
from componentes.entrada.entrada_view import EntradaView
from componentes.tabla.tabla_view import TablaView
from config.estilos import (
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_FONDO,
    COLOR_SECUNDARIO,
    COLOR_SECUNDARIO_HOVER,
    FUENTE_TITULO,
)


class ClientesView(ctk.CTkFrame):
    """Vista de clientes centrada en localizar registros existentes."""

    def __init__(self, master):
        super().__init__(master=master, fg_color=COLOR_FONDO)

        self.lbl_titulo = ctk.CTkLabel(
            self, text="Clientes", font=FUENTE_TITULO
        )
        self.lbl_titulo.pack(pady=10)

        self.frame_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_busqueda.grid_columnconfigure(0, weight=1)

        self.txt_busqueda = EntradaView(
            self.frame_busqueda,
            placeholder="Buscar por documento, nombre, teléfono o dirección",
        )
        self.txt_busqueda.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.btn_crear = BotonView(
            self.frame_busqueda,
            texto="Crear cliente",
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_crear.grid(row=0, column=1)

        self.tabla_clientes = TablaView(
            self,
            columnas=[
                "RIF/Cédula",
                "Nombre / Razón social",
                "Teléfono",
                "Dirección",
                "Estado",
            ],
        )
        self.tabla_clientes.pack(pady=(0, 10), fill="both", expand=True, padx=20)

        self.frame_form = ctk.CTkFrame(self, fg_color="transparent")
        for indice in range(4):
            self.frame_form.grid_columnconfigure(indice, weight=1)

        self.txt_documento = EntradaView(self.frame_form, placeholder="RIF / Cédula")
        self.txt_documento.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.txt_nombre = EntradaView(
            self.frame_form, placeholder="Nombre / Razón social"
        )
        self.txt_nombre.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.txt_telefono = EntradaView(self.frame_form, placeholder="Teléfono")
        self.txt_telefono.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        self.txt_direccion = EntradaView(self.frame_form, placeholder="Dirección")
        self.txt_direccion.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        self.btn_guardar = BotonView(
            self.frame_form,
            texto="Guardar cliente",
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_guardar.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.btn_actualizar = BotonView(
            self.frame_form,
            texto="Actualizar cliente",
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER,
        )
        self.btn_actualizar.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        self.btn_activar = BotonView(
            self.frame_form,
            texto="Activar cliente",
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER,
            state="disabled",
        )
        self.btn_activar.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.btn_desactivar = BotonView(
            self.frame_form,
            texto="Desactivar cliente",
            fg_color="#C0392B",
            hover_color="#A93226",
            state="disabled",
        )
        self.btn_desactivar.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    def mostrar_formulario(self):
        self.frame_form.pack(fill="x", padx=20, pady=(0, 10))

    def ocultar_formulario(self):
        self.frame_form.pack_forget()

    def establecer_solo_lectura(self, solo_lectura: bool):
        """Deshabilita todos los controles que cambian clientes."""
        estado = "disabled" if solo_lectura else "normal"
        for entrada in (
            self.txt_documento,
            self.txt_nombre,
            self.txt_telefono,
            self.txt_direccion,
        ):
            entrada.configure(state=estado)
        for boton in (
            self.btn_crear,
            self.btn_guardar,
            self.btn_actualizar,
            self.btn_activar,
            self.btn_desactivar,
        ):
            boton.configure(state=estado)
