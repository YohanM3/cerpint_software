import customtkinter as ctk
from componentes.boton.boton_view import BotonView
from componentes.entrada.entrada_view import EntradaView
from componentes.tabla.tabla_view import TablaView
from config.estilos import (
    COLOR_FONDO,
    FUENTE_TITULO,
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_SECUNDARIO,
    COLOR_SECUNDARIO_HOVER,
)


class ClientesView(ctk.CTkFrame):
    """Interfaz gráfica del módulo de Clientes."""

    def __init__(self, master):
        super().__init__(master=master, fg_color=COLOR_FONDO)

        # Título
        self.lbl_titulo = ctk.CTkLabel(
            self, text="Gestión de Clientes", font=FUENTE_TITULO
        )
        self.lbl_titulo.pack(pady=10)

        # Frame de Formulario
        self.frame_form = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_form.pack(pady=10, fill="x", padx=20)

        for i in range(4):
            self.frame_form.grid_columnconfigure(i, weight=1)

        self.txt_documento = EntradaView(self.frame_form, placeholder="RIF / Cédula")
        self.txt_documento.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.txt_nombre = EntradaView(
            self.frame_form, placeholder="Nombre / Razón Social"
        )
        self.txt_nombre.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.txt_telefono = EntradaView(self.frame_form, placeholder="Teléfono")
        self.txt_telefono.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        self.txt_direccion = EntradaView(self.frame_form, placeholder="Dirección")
        self.txt_direccion.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_acciones.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_guardar = BotonView(
            self.frame_acciones,
            texto="Guardar Cliente",
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
            width=170,
        )
        self.btn_guardar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.btn_actualizar = BotonView(
            self.frame_acciones,
            texto="Actualizar Cliente",
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER,
            width=170,
        )
        self.btn_actualizar.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.btn_eliminar = BotonView(
            self.frame_acciones,
            texto="Eliminar Cliente",
            fg_color="#C0392B",
            hover_color="#A93226",
            width=170,
        )
        self.btn_eliminar.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # Tabla de Clientes
        self.tabla_clientes = TablaView(
            self,
            columnas=["RIF/Cédula", "Nombre / Razon Social", "Teléfono", "Dirección"],
        )
        self.tabla_clientes.pack(pady=15, fill="both", expand=True, padx=20)
