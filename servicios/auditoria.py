"""Contexto de sesión y registro de operaciones auditables."""

from contextvars import ContextVar

from database.errores import PermisoError
from servicios.permisos import PERMISOS_ESCRITURA

_permisos_actuales = ContextVar("permisos_actuales", default=None)
_usuario_actual = ContextVar("usuario_actual", default="Sistema")
_rol_actual = ContextVar("rol_actual", default="sistema")


def establecer_sesion(usuario: str, rol: str, permisos=None) -> None:
    """Asocia el usuario autenticado con las operaciones de esta sesión."""
    _usuario_actual.set(usuario or "Sistema")
    _rol_actual.set(rol or "sistema")
    _permisos_actuales.set(frozenset(permisos) if permisos is not None else None)


def obtener_rol_actual() -> str:
    return _rol_actual.get()


def requerir_administrador(permiso: str | None = None) -> None:
    """Evita escrituras cuando el rol de la sesión no tiene permisos de modificación."""
    if _rol_actual.get() == "administrador":
        return
    permisos = _permisos_actuales.get()
    if permisos is None:
        raise PermisoError("No hay una sesión establecida para esta operación.")
    permitido = (
        permiso in permisos
        if permiso is not None
        else bool(permisos & PERMISOS_ESCRITURA)
    )
    if not permitido:
        raise PermisoError(
            f"El rol {_rol_actual.get()} no tiene permiso para esta operación."
        )


def registrar_evento(
    cursor, accion: str, entidad: str, referencia: str, detalle: str = ""
) -> None:
    """Registra una acción usando el cursor de la transacción activa."""
    cursor.execute(
        """
        INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            _usuario_actual.get(),
            _rol_actual.get(),
            accion,
            entidad,
            str(referencia),
            detalle,
        ),
    )
