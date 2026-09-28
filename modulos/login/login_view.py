import customtkinter as ctk

from config.estilos import (
    COLOR_BORDE,
    COLOR_ERROR,
    COLOR_FONDO,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
    COLOR_SUPERFICIE,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
)


class LoginView(ctk.CTkFrame):
    """Formulario compacto de acceso al sistema."""

    def __init__(self, master, al_ingresar):
        super().__init__(master=master, fg_color=COLOR_FONDO)
        self.al_ingresar = al_ingresar
        self.pack(fill="both", expand=True)

        self.card = ctk.CTkFrame(
            self,
            width=380,
            height=410,
            corner_radius=8,
            fg_color=COLOR_SUPERFICIE,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        self.card.pack(expand=True, padx=28, pady=28)
        self.card.pack_propagate(False)

        ctk.CTkFrame(
            self.card,
            height=5,
            corner_radius=0,
            fg_color=COLOR_PRIMARIO,
        ).pack(fill="x")

        ctk.CTkLabel(
            self.card,
            text="CERPINT",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXTO_PRINCIPAL,
        ).pack(pady=(34, 2))
        ctk.CTkLabel(
            self.card,
            text="Inicia sesión para continuar",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).pack(pady=(0, 22))

        ctk.CTkLabel(
            self.card,
            text="Usuario",
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXTO_PRINCIPAL,
        ).pack(anchor="w", padx=46, pady=(0, 5))

        self.txt_usuario = ctk.CTkEntry(
            self.card,
            placeholder_text="Escribe tu usuario",
            width=288,
            height=42,
            corner_radius=6,
        )
        self.txt_usuario.pack(pady=(0, 14))

        ctk.CTkLabel(
            self.card,
            text="Contraseña",
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXTO_PRINCIPAL,
        ).pack(anchor="w", padx=46, pady=(0, 5))

        self.txt_password = ctk.CTkEntry(
            self.card,
            placeholder_text="Escribe tu contraseña",
            show="*",
            width=288,
            height=42,
            corner_radius=6,
        )
        self.txt_password.pack(pady=(0, 6))

        self.lbl_error = ctk.CTkLabel(
            self.card,
            text="",
            height=20,
            font=("Segoe UI", 11),
            text_color=COLOR_ERROR,
        )
        self.lbl_error.pack(pady=(0, 6))

        self.btn_login = ctk.CTkButton(
            self.card,
            text="Acceder",
            command=self._ejecutar_login,
            width=288,
            height=42,
            corner_radius=6,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
        )
        self.btn_login.pack()

        self.txt_usuario.bind("<Return>", self._enfocar_password)
        self.txt_password.bind("<Return>", self._enviar_login)
        self.after(150, self.txt_usuario.focus_set)

    def _enfocar_password(self, _evento=None):
        self.txt_password.focus_set()
        return "break"

    def _enviar_login(self, _evento=None):
        self._ejecutar_login()
        return "break"

    def _ejecutar_login(self):
        self.al_ingresar(
            self.txt_usuario.get().strip(), self.txt_password.get().strip()
        )

    def mostrar_error(self, mensaje):
        self.lbl_error.configure(text=mensaje)
