from database.errores import (
    DatabaseError,
    PermisoError,
    ValidacionError,
    mensaje_error_base_datos,
)
from modulos.administracion.administracion_view import AdministracionView
from servicios import permisos as servicio


class AdministracionController:
    """Coordina la gestión de roles y permisos desde la ventana de administración."""

    def __init__(self, master, usuario_sesion):
        self.usuario_sesion = usuario_sesion
        self.rol_seleccionado = None
        self.view = AdministracionView(master)
        self.view.btn_crear.configure(command=self.crear_rol)
        self.view.btn_eliminar.configure(command=self.eliminar_rol)
        self.view.btn_guardar.configure(command=self.guardar_permisos)
        self.view.btn_asignar.configure(command=self.asignar_rol)
        self.view.btn_crear_usuario.configure(command=self.crear_usuario)
        self.view.btn_restablecer.configure(command=self.restablecer_clave)
        self.recargar()

    def recargar(self):
        roles = servicio.listar_roles()
        if self.rol_seleccionado not in roles:
            self.rol_seleccionado = roles[0]
        self.view.mostrar_roles(roles, self.rol_seleccionado, self.seleccionar_rol)
        self._mostrar_permisos_del_rol()
        try:
            self.view.mostrar_usuarios(servicio.listar_usuarios(), roles)
        except DatabaseError as error:
            self.view.mostrar_mensaje(mensaje_error_base_datos(error))

    def seleccionar_rol(self, rol):
        self.rol_seleccionado = rol
        self.recargar()

    def _mostrar_permisos_del_rol(self):
        rol = self.rol_seleccionado
        self.view.mostrar_permisos(
            rol,
            servicio.obtener_permisos(rol),
            editable=rol != servicio.ROL_ADMINISTRADOR,
        )

    def _ejecutar(self, accion, mensaje_ok):
        try:
            resultado = accion()
        except (ValidacionError, PermisoError, RuntimeError) as error:
            self.view.mostrar_mensaje(str(error))
            return None
        except DatabaseError as error:
            self.view.mostrar_mensaje(mensaje_error_base_datos(error))
            return None
        self.view.mostrar_mensaje(mensaje_ok, error=False)
        return resultado

    def crear_rol(self):
        nombre = self.view.txt_nuevo_rol.get()
        creado = self._ejecutar(
            lambda: servicio.crear_rol(nombre, self.view.txt_descripcion.get()),
            "Rol creado. Marca sus permisos y guarda.",
        )
        if creado:
            self.view.txt_nuevo_rol.delete(0, "end")
            self.view.txt_descripcion.delete(0, "end")
            self.rol_seleccionado = creado
            self.recargar()

    def guardar_permisos(self):
        self._ejecutar(
            lambda: servicio.guardar_permisos(
                self.rol_seleccionado, self.view.permisos_marcados()
            ),
            "Permisos guardados. Se aplican en el próximo inicio de sesión.",
        )

    def eliminar_rol(self):
        rol = self.rol_seleccionado
        if self._ejecutar(lambda: servicio.eliminar_rol(rol) or True, "Rol eliminado."):
            self.rol_seleccionado = None
            self.recargar()

    def asignar_rol(self):
        usuario = self.view.cmb_usuario.get()
        rol = self.view.cmb_rol_usuario.get()
        if not usuario:
            return
        if self._ejecutar(
            lambda: servicio.asignar_rol(usuario, rol, self.usuario_sesion) or True,
            f"Rol {rol} asignado a {usuario}.",
        ):
            self.recargar()

    def crear_usuario(self):
        rol = self.view.cmb_rol_usuario.get()
        creado = self._ejecutar(
            lambda: servicio.crear_usuario(
                self.view.txt_nuevo_usuario.get(),
                self.view.txt_nuevo_nombre.get(),
                rol,
                self.view.txt_nueva_clave.get(),
            ),
            f"Usuario creado con el rol {rol}.",
        )
        if creado:
            self.view.limpiar_nuevo_usuario()
            self.recargar()

    def restablecer_clave(self):
        usuario = self.view.cmb_usuario.get()
        if not usuario:
            return
        if self._ejecutar(
            lambda: servicio.restablecer_clave(
                usuario, self.view.txt_nueva_clave.get()
            )
            or True,
            f"Clave de {usuario} restablecida.",
        ):
            self.view.limpiar_nuevo_usuario()
