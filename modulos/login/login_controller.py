import sqlite3
from contextlib import closing

from database.conexion import obtener_conexion
from modulos.login.login_view import LoginView
from servicios.seguridad import es_hash_clave, generar_hash_clave, verificar_clave


class LoginController:
    """Valida las credenciales de acceso al sistema."""

    def __init__(self, master, al_autenticar_exitoso):
        master.title("Cerpint - Acceso")
        master.geometry("420x480")
        master.minsize(380, 440)
        master.resizable(False, False)
        self.al_autenticar_exitoso = al_autenticar_exitoso
        self.view = LoginView(master, self.autenticar)

    def autenticar(self, usuario, password):
        if not usuario or not password:
            self.view.mostrar_error("Ingresa usuario y contraseña.")
            return

        try:
            with closing(obtener_conexion()) as conexion:
                usuario_valido = conexion.execute(
                    "SELECT usuario, clave, rol FROM usuarios WHERE usuario = ?",
                    (usuario,),
                ).fetchone()
                if usuario_valido and verificar_clave(password, usuario_valido[1]):
                    if not es_hash_clave(usuario_valido[1]):
                        conexion.execute(
                            "UPDATE usuarios SET clave = ? WHERE usuario = ?",
                            (generar_hash_clave(password), usuario_valido[0]),
                        )
                else:
                    usuario_valido = None
        except sqlite3.Error:
            self.view.mostrar_error("No se pudo validar el acceso.")
            return

        if usuario_valido:
            self.view.mostrar_error("")
            self.al_autenticar_exitoso(usuario_valido[0], usuario_valido[2])
            return

        self.view.mostrar_error("Usuario o contraseña incorrectos.")
        self.view.txt_password.delete(0, "end")
        self.view.txt_password.focus_set()
