import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from tkinter import simpledialog
from database.conexion import transaccion
from database.errores import DatabaseError
from modulos.login.login_view import LoginView
from servicios.permisos import rol_existe
from servicios.seguridad import generar_hash_clave, necesita_rehash, verificar_clave


class LoginController:
    """Valida las credenciales de acceso al sistema."""

    CLAVES_DEMOSTRACION = {"1234", "admin123"}
    MAX_INTENTOS_FALLIDOS = 5
    SEGUNDOS_BLOQUEO = 300
    _intentos_fallidos: dict = {}
    _bloqueados_hasta: dict = {}

    @classmethod
    def _segundos_bloqueo_restantes(cls, usuario) -> int:
        hasta = cls._bloqueados_hasta.get(usuario)
        if hasta is None:
            return 0
        restante = (hasta - datetime.now()).total_seconds()
        if restante <= 0:
            cls._bloqueados_hasta.pop(usuario, None)
            cls._intentos_fallidos.pop(usuario, None)
            return 0
        return int(restante) + 1

    @classmethod
    def _registrar_fallo(cls, usuario) -> None:
        intentos = cls._intentos_fallidos.get(usuario, 0) + 1
        cls._intentos_fallidos[usuario] = intentos
        if intentos >= cls.MAX_INTENTOS_FALLIDOS:
            cls._bloqueados_hasta[usuario] = datetime.now() + timedelta(
                seconds=cls.SEGUNDOS_BLOQUEO
            )

    def __init__(self, master, al_autenticar_exitoso):
        master.title("Cerpint - Acceso")
        master.geometry("420x480")
        master.minsize(380, 440)
        master.resizable(False, False)
        self.al_autenticar_exitoso = al_autenticar_exitoso
        self.view = LoginView(master, self.autenticar, self.recuperar_contrasena)

    def autenticar(self, usuario, password):
        if not usuario or not password:
            self.view.mostrar_error("Ingresa usuario y contraseña.")
            return

        restante = self._segundos_bloqueo_restantes(usuario)
        if restante:
            minutos = (restante + 59) // 60
            self.view.mostrar_error(
                f"Demasiados intentos fallidos. Intenta de nuevo en {minutos} minuto(s)."
            )
            return

        try:
            with transaccion() as conexion:
                usuario_valido = conexion.execute(
                    "SELECT usuario, clave, rol FROM usuarios WHERE usuario = %s",
                    (usuario,),
                ).fetchone()
                if (
                    usuario_valido
                    and rol_existe(usuario_valido[2])
                    and verificar_clave(password, usuario_valido[1])
                ):
                    if necesita_rehash(usuario_valido[1]):
                        conexion.execute(
                            "UPDATE usuarios SET clave = %s WHERE usuario = %s",
                            (generar_hash_clave(password), usuario_valido[0]),
                        )
                    if password in self.CLAVES_DEMOSTRACION:
                        if not self._cambiar_clave_demostracion(
                            conexion, usuario_valido[0]
                        ):
                            usuario_valido = None
                else:
                    usuario_valido = None
        except DatabaseError:
            self.view.mostrar_error("No se pudo validar el acceso.")
            return

        if usuario_valido:
            self._intentos_fallidos.pop(usuario, None)
            self.view.mostrar_error("")
            self.al_autenticar_exitoso(usuario_valido[0], usuario_valido[2])
            return

        self._registrar_fallo(usuario)
        if self._segundos_bloqueo_restantes(usuario):
            self.view.mostrar_error(
                "Demasiados intentos fallidos. Acceso bloqueado por 5 minutos."
            )
        else:
            self.view.mostrar_error("Usuario o contraseña incorrectos.")
        self.view.txt_password.delete(0, "end")
        self.view.txt_password.focus_set()

    def _cambiar_clave_demostracion(self, conexion, usuario: str) -> bool:
        """Solicita reemplazar una credencial pública antes de abrir el sistema."""
        parent = self.view.winfo_toplevel()
        nueva_clave = simpledialog.askstring(
            "Cambio de contraseña",
            "La contraseña de demostración debe cambiarse.\nNueva contraseña (mínimo 8 caracteres):",
            parent=parent,
            show="*",
        )
        if not nueva_clave or len(nueva_clave) < 8:
            self.view.mostrar_error(
                "Debes establecer una contraseña de al menos 8 caracteres."
            )
            return False
        confirmacion = simpledialog.askstring(
            "Confirmar contraseña",
            "Repite la nueva contraseña:",
            parent=parent,
            show="*",
        )
        if nueva_clave != confirmacion:
            self.view.mostrar_error("Las contraseñas no coinciden.")
            return False
        conexion.execute(
            "UPDATE usuarios SET clave = %s WHERE usuario = %s",
            (generar_hash_clave(nueva_clave), usuario),
        )
        return True

    def recuperar_contrasena(self):
        """Recuperación de clave disponible solo para el rol administrador."""
        parent = self.view.winfo_toplevel()
        usuario = simpledialog.askstring(
            "Recuperar contraseña",
            "Ingresa tu usuario de administrador:",
            parent=parent,
        )
        correo = simpledialog.askstring(
            "Recuperar contraseña",
            "Ingresa el correo registrado:",
            parent=parent,
        )
        if not usuario or not correo:
            self.view.mostrar_error("Debes indicar usuario y correo.")
            return

        usuario = usuario.strip()
        correo = correo.strip().lower()
        codigo = "".join(secrets.choice("0123456789") for _ in range(6))
        vencimiento = datetime.now() + timedelta(minutes=15)
        try:
            with transaccion() as conexion:
                registro = conexion.execute(
                    "SELECT usuario FROM usuarios "
                    "WHERE usuario = %s AND correo = %s AND rol = 'administrador'",
                    (usuario, correo),
                ).fetchone()
                if not registro:
                    self.view.mostrar_error(
                        "Solo un administrador con ese usuario y correo "
                        "puede recuperar su contraseña."
                    )
                    return
                conexion.execute(
                    """
                    UPDATE usuarios
                    SET codigo_recuperacion = %s, recuperacion_expira_en = %s
                    WHERE usuario = %s
                    """,
                    (generar_hash_clave(codigo), vencimiento, registro[0]),
                )
        except DatabaseError:
            self.view.mostrar_error("No se pudo iniciar la recuperación de contraseña.")
            return

        try:
            self._enviar_codigo_recuperacion(correo, codigo)
        except (OSError, smtplib.SMTPException, ValueError) as error:
            self.view.mostrar_error(f"No se pudo enviar el correo: {error}")
            return

        codigo_ingresado = simpledialog.askstring(
            "Verificar código",
            "Ingresa el código de seis dígitos enviado a tu correo:",
            parent=parent,
        )
        nueva_clave = simpledialog.askstring(
            "Nueva contraseña",
            "Escribe una nueva contraseña (mínimo 8 caracteres):",
            parent=parent,
            show="*",
        )
        confirmacion = simpledialog.askstring(
            "Confirmar contraseña",
            "Repite la nueva contraseña:",
            parent=parent,
            show="*",
        )
        if not codigo_ingresado or not nueva_clave or nueva_clave != confirmacion:
            self.view.mostrar_error("El código o las contraseñas no son válidos.")
            return
        if len(nueva_clave) < 8:
            self.view.mostrar_error(
                "La nueva contraseña debe tener al menos 8 caracteres."
            )
            return

        try:
            with transaccion() as conexion:
                registro = conexion.execute(
                    """
                    SELECT codigo_recuperacion, recuperacion_expira_en
                    FROM usuarios
                    WHERE usuario = %s AND correo = %s AND rol = 'administrador'
                    """,
                    (usuario, correo),
                ).fetchone()
                if (
                    not registro
                    or not registro[0]
                    or not registro[1]
                    or registro[1] < datetime.now()
                    or not verificar_clave(codigo_ingresado.strip(), registro[0])
                ):
                    self.view.mostrar_error("El código de recuperación no es válido.")
                    return
                conexion.execute(
                    """
                    UPDATE usuarios
                    SET clave = %s, codigo_recuperacion = NULL,
                        recuperacion_expira_en = NULL
                    WHERE usuario = %s AND rol = 'administrador'
                    """,
                    (generar_hash_clave(nueva_clave), usuario),
                )
        except DatabaseError:
            self.view.mostrar_error("No se pudo restablecer la contraseña.")
            return

        self.view.mostrar_error("Contraseña actualizada. Ya puedes iniciar sesión.")

    @staticmethod
    def _enviar_codigo_recuperacion(destinatario: str, codigo: str):
        """Envía el código temporal usando la configuración SMTP local."""
        host = os.getenv("SMTP_HOST")
        remitente = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")
        if not host or not remitente:
            raise ValueError(
                "Configura SMTP_HOST y SMTP_FROM o SMTP_USER para recuperar la contraseña."
            )

        puerto = int(os.getenv("SMTP_PORT", "587"))
        usuario = os.getenv("SMTP_USER")
        clave = os.getenv("SMTP_PASSWORD")
        mensaje = EmailMessage()
        mensaje["Subject"] = "Recuperación de contraseña - Cerpint"
        mensaje["From"] = remitente
        mensaje["To"] = destinatario
        mensaje.set_content(
            f"Tu código de recuperación es: {codigo}\n\n"
            "Vence en 15 minutos. Si no solicitaste este cambio, ignora este correo."
        )

        with smtplib.SMTP(host, puerto, timeout=15) as servidor:
            if os.getenv("SMTP_USE_TLS", "1") == "1":
                servidor.starttls()
            if usuario and clave:
                servidor.login(usuario, clave)
            servidor.send_message(mensaje)
