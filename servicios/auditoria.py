"""Contexto de sesión y registro de operaciones auditables."""

from contextvars import ContextVar

_usuario_actual = ContextVar("usuario_actual", default="Sistema")
_rol_actual = ContextVar("rol_actual", default="sistema")


def establecer_sesion(usuario: str, rol: str) -> None:
    """Asocia el usuario autenticado con las operaciones de esta sesión."""
    _usuario_actual.set(usuario or "Sistema")
    _rol_actual.set(rol or "sistema")


def registrar_evento(
    cursor, accion: str, entidad: str, referencia: str, detalle: str = ""
) -> None:
    """Registra una acción usando el cursor de la transacción activa."""
    cursor.execute(
        """
        INSERT INTO auditoria (usuario, rol, accion, entidad, referencia, detalle)
        VALUES (?, ?, ?, ?, ?, ?)
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
