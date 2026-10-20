"""Roles dinámicos y permisos asignables por el administrador."""

import re

from database.conexion import transaccion
from database.errores import DatabaseError, PermisoError, ValidacionError
from servicios.seguridad import generar_hash_clave

ROL_ADMINISTRADOR = "administrador"

PERMISOS = {
    "inventario.ver": "Ver inventario",
    "inventario.modificar": "Crear, modificar y desactivar productos",
    "clientes.ver": "Ver clientes",
    "clientes.modificar": "Crear, modificar y desactivar clientes",
    "ventas.realizar": "Realizar ventas / notas",
    "consultas.ver": "Ver consultas y reportes",
    "consultas.modificar": "Registrar pagos y cambiar notas",
}

PERMISOS_ESCRITURA = {
    "inventario.modificar",
    "clientes.modificar",
    "ventas.realizar",
    "consultas.modificar",
}

ROLES_BASE = {
    ROL_ADMINISTRADOR: set(PERMISOS),
    "consultor": {"consultas.ver"},
    "almacenista": {"inventario.ver", "clientes.ver"},
}

_PATRON_ROL = re.compile(r"^[a-z0-9_]{3,32}$")
_PATRON_USUARIO = re.compile(r"^[a-z0-9_.]{3,32}$")
_MODULOS = ("inventario", "clientes", "ventas", "consultas")
_ACCIONES_DB = ("puede_ver", "puede_crear", "puede_editar", "puede_eliminar")


def _requerir_administrador_actual():
    from servicios.auditoria import obtener_rol_actual

    if obtener_rol_actual() != ROL_ADMINISTRADOR:
        raise PermisoError("Solo el administrador puede gestionar roles y permisos.")


def _error_esquema(error):
    return RuntimeError(
        "No se pudieron consultar las tablas roles y permisos_roles. "
        f"Verifica su estructura. Detalle: {error}"
    )


def _id_rol(conexion, rol):
    fila = conexion.execute(
        "SELECT id FROM roles WHERE nombre = %s AND activo = 1", (rol,)
    ).fetchone()
    if not fila:
        raise ValidacionError("El rol seleccionado no existe o está inactivo.")
    return fila[0]


def _permisos_a_filas(permisos):
    """Traduce los permisos de la interfaz a los indicadores CRUD existentes."""
    filas = {
        modulo: {accion: 0 for accion in _ACCIONES_DB}
        for modulo in _MODULOS
    }
    for permiso in permisos:
        modulo, accion = permiso.split(".", 1)
        if permiso == "ventas.realizar":
            filas["ventas"]["puede_ver"] = 1
            filas["ventas"]["puede_crear"] = 1
        elif accion == "ver":
            filas[modulo]["puede_ver"] = 1
        elif accion == "modificar":
            for clave in ("puede_crear", "puede_editar", "puede_eliminar"):
                filas[modulo][clave] = 1
    return filas


def _filas_a_permisos(filas):
    permisos = set()
    for modulo, puede_ver, puede_crear, puede_editar, puede_eliminar in filas:
        if modulo not in _MODULOS:
            continue
        if puede_ver:
            if modulo == "ventas":
                if puede_crear:
                    permisos.add("ventas.realizar")
            else:
                permisos.add(f"{modulo}.ver")
        if modulo == "ventas" and puede_crear:
            permisos.add("ventas.realizar")
        elif modulo == "consultas" and (puede_crear or puede_editar or puede_eliminar):
            permisos.add("consultas.modificar")
        elif modulo in {"inventario", "clientes"} and (
            puede_crear or puede_editar or puede_eliminar
        ):
            permisos.add(f"{modulo}.modificar")
    return permisos


def listar_roles() -> list[str]:
    try:
        with transaccion() as conexion:
            filas = conexion.execute(
                "SELECT nombre FROM roles WHERE activo = 1 ORDER BY nombre"
            ).fetchall()
    except DatabaseError as error:
        raise _error_esquema(error) from error
    return sorted(
        {fila[0] for fila in filas},
        key=lambda rol: (rol != ROL_ADMINISTRADOR, rol),
    )


def rol_existe(rol: str) -> bool:
    return rol in listar_roles()


def obtener_permisos(rol: str) -> set[str]:
    if rol == ROL_ADMINISTRADOR:
        return set(PERMISOS)
    try:
        with transaccion() as conexion:
            rol_id = _id_rol(conexion, rol)
            filas = conexion.execute(
                """
                SELECT modulo, puede_ver, puede_crear, puede_editar, puede_eliminar
                FROM permisos_roles
                WHERE rol_id = %s
                """,
                (rol_id,),
            ).fetchall()
    except DatabaseError as error:
        raise _error_esquema(error) from error
    if not filas:
        return set(ROLES_BASE.get(rol, set()))
    return _filas_a_permisos(filas)


def crear_rol(nombre: str, descripcion: str = "") -> str:
    _requerir_administrador_actual()
    nombre = (nombre or "").strip().lower().replace(" ", "_")
    if not _PATRON_ROL.match(nombre):
        raise ValidacionError(
            "El nombre del rol debe tener de 3 a 32 letras, números o guion bajo."
        )
    try:
        with transaccion() as conexion:
            existente = conexion.execute(
                "SELECT 1 FROM roles WHERE nombre = %s", (nombre,)
            ).fetchone()
            if existente:
                raise ValidacionError("Ya existe un rol con ese nombre.")
            conexion.execute(
                "INSERT INTO roles (nombre, descripcion, activo) VALUES (%s, %s, 1)",
                (nombre, (descripcion or "").strip()[:120]),
            )
            rol_id = conexion.execute(
                "SELECT id FROM roles WHERE nombre = %s", (nombre,)
            ).fetchone()[0]
            for modulo in _MODULOS:
                conexion.execute(
                    """
                    INSERT INTO permisos_roles
                        (rol_id, modulo, puede_ver, puede_crear, puede_editar, puede_eliminar)
                    VALUES (%s, %s, 0, 0, 0, 0)
                    """,
                    (rol_id, modulo),
                )
    except DatabaseError as error:
        raise _error_esquema(error) from error
    return nombre


def guardar_permisos(rol: str, permisos) -> None:
    _requerir_administrador_actual()
    if rol == ROL_ADMINISTRADOR:
        raise ValidacionError("El administrador siempre tiene todos los permisos.")
    permisos = set(permisos)
    if not permisos <= set(PERMISOS):
        raise ValidacionError("Se indicó un permiso desconocido.")
    try:
        with transaccion() as conexion:
            rol_id = _id_rol(conexion, rol)
            conexion.execute(
                "DELETE FROM permisos_roles WHERE rol_id = %s", (rol_id,)
            )
            filas = _permisos_a_filas(permisos)
            for modulo, acciones in filas.items():
                conexion.execute(
                    """
                    INSERT INTO permisos_roles
                        (rol_id, modulo, puede_ver, puede_crear, puede_editar, puede_eliminar)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        rol_id,
                        modulo,
                        acciones["puede_ver"],
                        acciones["puede_crear"],
                        acciones["puede_editar"],
                        acciones["puede_eliminar"],
                    ),
                )
    except DatabaseError as error:
        raise _error_esquema(error) from error


def eliminar_rol(rol: str) -> None:
    _requerir_administrador_actual()
    if rol in ROLES_BASE:
        raise ValidacionError("Los roles base del sistema no se pueden eliminar.")
    try:
        with transaccion() as conexion:
            rol_id = _id_rol(conexion, rol)
            usuarios = conexion.execute(
                "SELECT COUNT(*) FROM usuarios WHERE rol = %s", (rol,)
            ).fetchone()[0]
            if usuarios:
                raise ValidacionError(
                    "Hay usuarios con este rol; reasígnalos antes de eliminarlo."
                )
            conexion.execute(
                "DELETE FROM permisos_roles WHERE rol_id = %s", (rol_id,)
            )
            conexion.execute("DELETE FROM roles WHERE id = %s", (rol_id,))
    except DatabaseError as error:
        raise _error_esquema(error) from error


def listar_usuarios() -> list[tuple[str, str]]:
    with transaccion() as conexion:
        return [
            (fila[0], fila[1])
            for fila in conexion.execute(
                "SELECT usuario, rol FROM usuarios ORDER BY usuario"
            ).fetchall()
        ]


def _validar_clave_nueva(clave: str) -> None:
    if not clave or len(clave) < 8:
        raise ValidacionError("La contraseña debe tener al menos 8 caracteres.")


def crear_usuario(usuario: str, nombre: str, rol: str, clave: str) -> str:
    _requerir_administrador_actual()
    usuario = (usuario or "").strip().lower()
    nombre = (nombre or "").strip() or usuario
    if not _PATRON_USUARIO.match(usuario):
        raise ValidacionError(
            "El usuario debe tener de 3 a 32 letras, números, punto o guion bajo."
        )
    _validar_clave_nueva(clave)
    if rol not in listar_roles():
        raise ValidacionError("El rol seleccionado no existe.")
    with transaccion() as conexion:
        if conexion.execute(
            "SELECT 1 FROM usuarios WHERE usuario = %s", (usuario,)
        ).fetchone():
            raise ValidacionError("Ya existe un usuario con ese nombre.")
        conexion.execute(
            "INSERT INTO usuarios (usuario, clave, nombre, rol) VALUES (%s, %s, %s, %s)",
            (usuario, generar_hash_clave(clave), nombre[:255], rol),
        )
    return usuario


def restablecer_clave(usuario: str, clave: str) -> None:
    _requerir_administrador_actual()
    _validar_clave_nueva(clave)
    with transaccion() as conexion:
        cursor = conexion.execute(
            """
            UPDATE usuarios
            SET clave = %s, codigo_recuperacion = NULL, recuperacion_expira_en = NULL
            WHERE usuario = %s
            """,
            (generar_hash_clave(clave), usuario),
        )
        if cursor.rowcount == 0:
            raise ValidacionError("El usuario seleccionado no existe.")


def asignar_rol(usuario: str, rol: str, usuario_sesion: str) -> None:
    _requerir_administrador_actual()
    if rol not in listar_roles():
        raise ValidacionError("El rol seleccionado no existe.")
    if usuario == usuario_sesion and rol != ROL_ADMINISTRADOR:
        raise ValidacionError("No puedes quitarte tu propio rol de administrador.")
    with transaccion() as conexion:
        conexion.execute("UPDATE usuarios SET rol = %s WHERE usuario = %s", (rol, usuario))
