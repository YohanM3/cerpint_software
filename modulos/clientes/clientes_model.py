from contextlib import closing

try:
    from database.conexion import obtener_conexion, transaccion
    from database.errores import RegistroNoEncontradoError, ValidacionError
except ModuleNotFoundError:
    import os
    import sys

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )
    from database.conexion import obtener_conexion, transaccion
    from database.errores import RegistroNoEncontradoError, ValidacionError


class ClientesModel:
    """Modelo para gestionar clientes."""

    def __init__(self):
        pass

    def agregar_cliente(
        self, documento: str, nombre: str, telefono: str = "", direccion: str = ""
    ) -> bool:
        """Guarda un cliente nuevo en la base de datos."""
        doc_fmt = (documento or "").strip().upper()
        nombre_fmt = (nombre or "").strip()
        if not doc_fmt or not nombre_fmt:
            raise ValidacionError("Documento y nombre son obligatorios.")

        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM clientes WHERE UPPER(documento) = ? LIMIT 1",
                (doc_fmt,),
            )
            if cursor.fetchone():
                return False

            cursor.execute(
                "INSERT INTO clientes (documento, nombre, telefono, direccion) VALUES (?, ?, ?, ?)",
                (
                    doc_fmt,
                    nombre_fmt,
                    (telefono or "").strip(),
                    (direccion or "").strip(),
                ),
            )
        return True

    def obtener_todos(self):
        """Devuelve todos los clientes ordenados por nombre."""
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT documento, nombre, telefono, direccion FROM clientes ORDER BY nombre"
            )
            return cursor.fetchall()

    def buscar_sugerencias(self, texto: str, limite: int = 5) -> list:
        """Busca clientes por documento o nombre."""
        valor = (texto or "").strip()
        if not valor:
            return []

        filtro = f"%{valor.upper()}%"
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT documento, nombre
                FROM clientes
                WHERE UPPER(documento) LIKE ? OR UPPER(nombre) LIKE ?
                ORDER BY nombre
                LIMIT ?
                """,
                (filtro, filtro, max(1, int(limite))),
            )
            return cursor.fetchall()

    def actualizar_cliente(
        self,
        doc_original: str,
        nuevo_doc: str,
        nuevo_nombre: str,
        nuevo_tel: str,
        nueva_dir: str,
    ) -> bool:
        """Actualiza los datos de un cliente en la base de datos."""
        doc_orig_fmt = (doc_original or "").strip().upper()
        nuevo_doc_fmt = (nuevo_doc or "").strip().upper()
        nombre_fmt = (nuevo_nombre or "").strip()
        if not doc_orig_fmt or not nuevo_doc_fmt or not nombre_fmt:
            raise ValidacionError("Documento y nombre son obligatorios.")

        with transaccion() as conn:
            cursor = conn.cursor()
            if doc_orig_fmt != nuevo_doc_fmt:
                cursor.execute(
                    "SELECT 1 FROM clientes WHERE UPPER(documento) = ? LIMIT 1",
                    (nuevo_doc_fmt,),
                )
                if cursor.fetchone():
                    return False

            cursor.execute(
                """
                UPDATE clientes
                SET documento = ?, nombre = ?, telefono = ?, direccion = ?
                WHERE UPPER(documento) = ?
                """,
                (
                    nuevo_doc_fmt,
                    nombre_fmt,
                    (nuevo_tel or "").strip(),
                    (nueva_dir or "").strip(),
                    doc_orig_fmt,
                ),
            )
            if cursor.rowcount != 1:
                raise RegistroNoEncontradoError("El cliente ya no existe.")
        return True

    def eliminar_cliente(self, documento: str) -> bool:
        """Elimina un cliente por documento."""
        doc_fmt = (documento or "").strip().upper()
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM clientes WHERE UPPER(documento) = ?", (doc_fmt,)
            )
            return cursor.rowcount == 1
