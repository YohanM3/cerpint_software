import customtkinter as ctk

from config.estilos import (
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_FONDO,
    COLOR_PELIGRO,
    COLOR_PELIGRO_HOVER,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
    COLOR_SUPERFICIE,
    COLOR_TEXTO_PRINCIPAL,
)
from servicios.permisos import PERMISOS


class AdministracionView(ctk.CTkToplevel):
    """Ventana para gestionar roles, permisos y asignación de usuarios."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Administración de roles y permisos")
        self.geometry("900x720")
        self.minsize(860, 680)
        self.configure(fg_color=COLOR_FONDO)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        izquierda = ctk.CTkFrame(self, fg_color=COLOR_SUPERFICIE)
        izquierda.grid(row=0, column=0, sticky="ns", padx=(12, 6), pady=12)
        ctk.CTkLabel(
            izquierda, text="Roles", font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXTO_PRINCIPAL,
        ).pack(anchor="w", padx=12, pady=(12, 4))
        self.lista_roles = ctk.CTkScrollableFrame(izquierda, width=200, height=220)
        self.lista_roles.pack(fill="both", expand=True, padx=8)
        self.txt_nuevo_rol = ctk.CTkEntry(
            izquierda, placeholder_text="Nombre del nuevo rol (ej.: vendedor)"
        )
        self.txt_nuevo_rol.pack(fill="x", padx=12, pady=(10, 4))
        self.txt_descripcion = ctk.CTkEntry(
            izquierda, placeholder_text="Descripción (opcional)"
        )
        self.txt_descripcion.pack(fill="x", padx=12, pady=4)
        self.btn_crear = ctk.CTkButton(
            izquierda, text="Crear rol", fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
        )
        self.btn_crear.pack(fill="x", padx=12, pady=4)
        self.btn_eliminar = ctk.CTkButton(
            izquierda, text="Eliminar rol", fg_color=COLOR_PELIGRO,
            hover_color=COLOR_PELIGRO_HOVER,
        )
        self.btn_eliminar.pack(fill="x", padx=12, pady=(4, 12))

        derecha = ctk.CTkFrame(self, fg_color=COLOR_SUPERFICIE)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        self.lbl_rol = ctk.CTkLabel(
            derecha, text="Selecciona un rol", font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXTO_PRINCIPAL,
        )
        self.lbl_rol.pack(anchor="w", padx=14, pady=(12, 6))
        self.variables_permisos = {}
        self.checks_permisos = {}
        for clave, etiqueta in PERMISOS.items():
            variable = ctk.BooleanVar(value=False)
            check = ctk.CTkCheckBox(derecha, text=etiqueta, variable=variable)
            check.pack(anchor="w", padx=20, pady=4)
            self.variables_permisos[clave] = variable
            self.checks_permisos[clave] = check
        self.btn_guardar = ctk.CTkButton(
            derecha, text="Guardar permisos", fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_guardar.pack(anchor="w", padx=20, pady=(10, 14))

        ctk.CTkLabel(
            derecha, text="Asignar rol a usuario", font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXTO_PRINCIPAL,
        ).pack(anchor="w", padx=14, pady=(4, 6))
        fila = ctk.CTkFrame(derecha, fg_color="transparent")
        fila.pack(fill="x", padx=14)
        self.cmb_usuario = ctk.CTkComboBox(fila, values=[""], width=180, state="readonly")
        self.cmb_usuario.pack(side="left", padx=(0, 8))
        self.cmb_rol_usuario = ctk.CTkComboBox(fila, values=[""], width=160, state="readonly")
        self.cmb_rol_usuario.pack(side="left", padx=(0, 8))
        self.btn_asignar = ctk.CTkButton(
            fila, text="Asignar", fg_color=COLOR_PRIMARIO, hover_color=COLOR_PRIMARIO_HOVER,
            width=90,
        )
        self.btn_asignar.pack(side="left")

        ctk.CTkLabel(
            derecha, text="Crear usuario / restablecer clave",
            font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXTO_PRINCIPAL,
        ).pack(anchor="w", padx=14, pady=(12, 6))
        fila_usuario = ctk.CTkFrame(derecha, fg_color="transparent")
        fila_usuario.pack(fill="x", padx=14)
        self.txt_nuevo_usuario = ctk.CTkEntry(
            fila_usuario, placeholder_text="Usuario (ej.: jperez)", width=150
        )
        self.txt_nuevo_usuario.pack(side="left", padx=(0, 8))
        self.txt_nuevo_nombre = ctk.CTkEntry(
            fila_usuario, placeholder_text="Nombre completo", width=170
        )
        self.txt_nuevo_nombre.pack(side="left", padx=(0, 8))
        self.txt_nueva_clave = ctk.CTkEntry(
            fila_usuario, placeholder_text="Clave (mín. 8)", show="*", width=130
        )
        self.txt_nueva_clave.pack(side="left")
        fila_botones = ctk.CTkFrame(derecha, fg_color="transparent")
        fila_botones.pack(fill="x", padx=14, pady=(6, 0))
        self.btn_crear_usuario = ctk.CTkButton(
            fila_botones, text="Crear usuario con el rol elegido arriba",
            fg_color=COLOR_EXITO, hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_crear_usuario.pack(side="left", padx=(0, 8))
        self.btn_restablecer = ctk.CTkButton(
            fila_botones, text="Restablecer clave del usuario elegido arriba",
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_PRIMARIO_HOVER,
        )
        self.btn_restablecer.pack(side="left")

        self.lbl_mensaje = ctk.CTkLabel(
            derecha, text="", text_color=COLOR_ERROR, wraplength=480, justify="left"
        )
        self.lbl_mensaje.pack(anchor="w", padx=14, pady=12)
        self.botones_roles = {}

    def mostrar_roles(self, roles, seleccionado, al_seleccionar):
        for boton in self.botones_roles.values():
            boton.destroy()
        self.botones_roles = {}
        for rol in roles:
            boton = ctk.CTkButton(
                self.lista_roles,
                text=rol,
                anchor="w",
                fg_color=COLOR_PRIMARIO if rol == seleccionado else "transparent",
                hover_color=COLOR_PRIMARIO_HOVER,
                text_color=COLOR_TEXTO_PRINCIPAL,
                command=lambda r=rol: al_seleccionar(r),
            )
            boton.pack(fill="x", pady=2)
            self.botones_roles[rol] = boton

    def mostrar_permisos(self, rol, permisos, editable):
        self.lbl_rol.configure(text=f"Permisos del rol: {rol}" if rol else "Selecciona un rol")
        for clave, variable in self.variables_permisos.items():
            variable.set(clave in permisos)
            self.checks_permisos[clave].configure(state="normal" if editable else "disabled")
        self.btn_guardar.configure(state="normal" if editable else "disabled")
        self.btn_eliminar.configure(state="normal" if editable else "disabled")

    def permisos_marcados(self):
        return {c for c, v in self.variables_permisos.items() if v.get()}

    def mostrar_usuarios(self, usuarios, roles):
        nombres = [u for u, _ in usuarios] or [""]
        self.cmb_usuario.configure(values=nombres)
        self.cmb_usuario.set(nombres[0])
        self.cmb_rol_usuario.configure(values=roles)
        self.cmb_rol_usuario.set(roles[0])

    def mostrar_mensaje(self, texto, error=True):
        self.lbl_mensaje.configure(
            text=texto, text_color=COLOR_ERROR if error else COLOR_EXITO
        )

    def limpiar_nuevo_usuario(self):
        for entrada in (
            self.txt_nuevo_usuario,
            self.txt_nuevo_nombre,
            self.txt_nueva_clave,
        ):
            entrada.delete(0, "end")
