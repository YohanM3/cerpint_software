import customtkinter as ctk

from config.estilos import COLOR_FONDO, COLOR_PRIMARIO, COLOR_PRIMARIO_HOVER


class LoginView(ctk.CTkFrame):
    """Formulario compacto de acceso al sistema."""

    def __init__(self, master, al_ingresar):
        super().__init__(master=master, fg_color=COLOR_FONDO)
        self.al_ingresar = al_ingresar
        self.pack(fill="both", expand=True)

        self.card = ctk.CTkFrame(
            self,
            width=360,
            height=370,
            corner_radius=8,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E4E7EB",
        )
        self.card.pack(expand=True, padx=28, pady=28)
        self.card.pack_propagate(False)

        ctk.CTkLabel(
            self.card,
            text="CERPINT",
            font=("Segoe UI", 25, "bold"),
            text_color="#1E293B",
        ).pack(pady=(38, 2))
        ctk.CTkLabel(
            self.card,
            text="Acceso al sistema de ferretería",
            font=("Segoe UI", 12),
            text_color="#64748B",
        ).pack(pady=(0, 24))

        self.txt_usuario = ctk.CTkEntry(
            self.card,
            placeholder_text="Usuario",
            width=280,
            height=42,
            corner_radius=6,
        )
        self.txt_usuario.pack(pady=(0, 10))

        self.txt_password = ctk.CTkEntry(
            self.card,
            placeholder_text="Contraseña",
            show="*",
            width=280,
            height=42,
            corner_radius=6,
        )
        self.txt_password.pack(pady=(0, 8))

        self.lbl_error = ctk.CTkLabel(
            self.card,
            text="",
            height=20,
            font=("Segoe UI", 11),
            text_color="#C0392B",
        )
        self.lbl_error.pack(pady=(0, 8))

        self.btn_login = ctk.CTkButton(
            self.card,
            text="Acceder",
            command=self._ejecutar_login,
            width=280,
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
