# main.py
import sqlite3
from tkinter import messagebox

import customtkinter as ctk
from database.conexion import inicializar_base_de_datos
from modulos.login.login_controller import LoginController

from config.estilos import (
    COLOR_FONDO,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
)

# Importación de Módulos (Modelo, Vista, Controlador)
from modulos.inventario.inventario_model import InventarioModel
from modulos.inventario.inventario_view import InventarioView
from modulos.inventario.inventario_controller import InventarioController

from modulos.clientes.clientes_model import ClientesModel
from modulos.clientes.clientes_view import ClientesView
from modulos.clientes.clientes_controller import ClientesController

from modulos.ventas.ventas_model import VentasModel
from modulos.ventas.ventas_view import VentasView
from modulos.ventas.ventas_controller import VentasController

from modulos.consultas.consultas_model import ConsultasModel
from modulos.consultas.consultas_view import ConsultasView
from modulos.consultas.consultas_controller import ConsultasController

from componentes.boton.boton_view import BotonView


class AplicacionPrincipal(ctk.CTk):
    """Ventana principal del sistema de ventas de Ferretería Cerpint."""

    def __init__(self):
        super().__init__()

        # Configuración de la Ventana Principal
        self.title("Ferretería Cerpint - Sistema de Control de Ventas")
        self.geometry("1024x600")
        self.minsize(900, 500)
        self.after(50, lambda: self.state("zoomed"))
        self.configure(fg_color=COLOR_FONDO)

        # 1. Menú de Navegación Superior
        self.frame_navegacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_navegacion.pack(side="top", fill="x", padx=20, pady=10)

        # Botones de la barra superior
        self.btn_nav_inventario = BotonView(
            self.frame_navegacion,
            texto="Inventario",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=130,
            command=lambda: self.mostrar_modulo("inventario", mostrar_titulo=True),
        )
        self.btn_nav_inventario.pack(side="left", padx=(5, 0))

        self.btn_nav_clientes = BotonView(
            self.frame_navegacion,
            texto="Clientes",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=130,
            command=lambda: self.mostrar_modulo("clientes", mostrar_titulo=True),
        )
        self.btn_nav_clientes.pack(side="left", padx=(5, 0))

        self.btn_nav_ventas = BotonView(
            self.frame_navegacion,
            texto="Ventas / Notas",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=130,
            command=lambda: self.mostrar_modulo("ventas", mostrar_titulo=True),
        )
        self.btn_nav_ventas.pack(side="left", padx=(5, 0))

        self.btn_nav_consultas = BotonView(
            self.frame_navegacion,
            texto="Consultas",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            width=120,
            command=lambda: self.mostrar_modulo("consultas", mostrar_titulo=True),
        )
        self.btn_nav_consultas.pack(side="left", padx=(5, 0))

        self.lbl_titulo_modulo = ctk.CTkLabel(
            self.frame_navegacion,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#0d1b2a", "#e5e7eb"),
        )
        self.lbl_titulo_modulo.pack_forget()

        # 2. Contenedor Dinámico para los Módulos
        self.contenedor_modulo = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_modulo.pack(side="top", fill="both", expand=True)

        # 3. Inicialización de los Módulos MVC
        self._inicializar_modulos()

        # Mostrar módulo inicial por defecto
        self.mostrar_modulo("ventas", mostrar_titulo=False)

    def _inicializar_modulos(self):
        """Instancia los Modelos, Vistas y Controladores de cada módulo."""
        # --- Módulo Inventario ---
        self.inventario_model = InventarioModel()
        self.inventario_view = InventarioView(self.contenedor_modulo)
        self.inventario_controller = InventarioController(
            self.inventario_model, self.inventario_view
        )

        # --- Módulo Clientes ---
        self.clientes_model = ClientesModel()
        self.clientes_view = ClientesView(self.contenedor_modulo)
        self.clientes_controller = ClientesController(
            self.clientes_model, self.clientes_view
        )

        # --- Módulo Ventas ---
        self.ventas_model = VentasModel()
        self.ventas_view = VentasView(self.contenedor_modulo)
        self.ventas_controller = VentasController(
            self.ventas_model,
            self.ventas_view,
            clientes_model=self.clientes_model,
            inventario_model=self.inventario_model,
        )

        # --- Módulo Consultas ---
        self.consultas_model = ConsultasModel()
        self.consultas_view = ConsultasView(self.contenedor_modulo)
        self.consultas_controller = ConsultasController(
            self.consultas_model,
            self.consultas_view,
        )

    def mostrar_modulo(self, nombre_modulo: str, mostrar_titulo: bool = False):
        """Oculta las vistas activas y despliega la vista del módulo solicitado."""
        # Ocultar todos los frames
        self.inventario_view.pack_forget()
        self.clientes_view.pack_forget()
        self.ventas_view.pack_forget()
        self.consultas_view.pack_forget()

        titulos = {
            "inventario": "Gestión de Inventario",
            "clientes": "Gestión de Clientes",
            "ventas": "Gestión de Ventas / Notas",
            "consultas": "Consultas y Reportes",
        }

        if mostrar_titulo and nombre_modulo in titulos:
            self.lbl_titulo_modulo.configure(text=titulos[nombre_modulo])
            self.lbl_titulo_modulo.pack(side="left", padx=(10, 20))
        else:
            self.lbl_titulo_modulo.pack_forget()

        # Mostrar el seleccionado
        if nombre_modulo == "inventario":
            self.inventario_view.pack(fill="both", expand=True)
        elif nombre_modulo == "clientes":
            self.clientes_view.pack(fill="both", expand=True)
        elif nombre_modulo == "ventas":
            self.ventas_view.pack(fill="both", expand=True)
            self.after(
                100,
                lambda: (
                    self.ventas_view.enfocar_busqueda_cliente()
                    if self.ventas_view.winfo_ismapped()
                    else None
                ),
            )
        elif nombre_modulo == "consultas":
            self.consultas_view.pack(fill="both", expand=True)
            self.consultas_controller.mostrar_notas_pendientes()


def iniciar_aplicacion():
    ctk.set_appearance_mode("System")

    try:
        inicializar_base_de_datos()
    except (OSError, sqlite3.Error) as error:
        messagebox.showerror(
            "No se pudo abrir la base de datos",
            f"Verifica que ferreteria.db sea accesible y esté íntegra.\n\n{error}",
        )
        raise SystemExit(1) from error

    login = ctk.CTk()
    usuario_autenticado = {"usuario": None}

    def abrir_sistema(usuario):
        usuario_autenticado["usuario"] = usuario
        login.destroy()

    LoginController(login, abrir_sistema)
    login.mainloop()

    if usuario_autenticado["usuario"] is None:
        return

    app = AplicacionPrincipal()
    app.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()
