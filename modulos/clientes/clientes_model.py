from contextlib import closing
from database.conexion import obtener_conexion, transaccion
from database.errores import RegistroNoEncontradoError, ValidacionError
from servicios.auditoria import registrar_evento, requerir_administrador


class ClientesModel:
    """Modelo para gestionar clientes."""

    def agregar_cliente(
        self, documento: str, nombre: str, telefono: str = "", direccion: str = ""
    ) -> bool:
        """Guarda un cliente nuevo en la base de datos."""
        requerir_administrador("clientes.modificar")
        doc_fmt = (documento or "").strip().upper()
        nombre_fmt = (nombre or "").strip()
        if not doc_fmt or not nombre_fmt:
            raise ValidacionError("Documento y nombre son obligatorios.")

        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM clientes WHERE documento = %s LIMIT 1",
                (doc_fmt,),
            )
            if cursor.fetchone():
                return False

            cursor.execute(
                "INSERT INTO clientes (documento, nombre, telefono, direccion) VALUES (%s, %s, %s, %s)",
                (
                    doc_fmt,
                    nombre_fmt,
                    (telefono or "").strip(),
                    (direccion or "").strip(),
                ),
            )
            registrar_evento(cursor, "CREAR", "cliente", doc_fmt, nombre_fmt)
        return True

    def obtener_todos(self):
        """Devuelve clientes activos e inactivos con su estado."""
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT documento, nombre, telefono, direccion, "
                "CASE WHEN activo = 1 THEN 'Activo' ELSE 'Inactivo' END "
                "FROM clientes ORDER BY nombre"
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
                WHERE activo = 1 AND (documento LIKE %s OR nombre LIKE %s)
                ORDER BY nombre
                LIMIT %s
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
        requerir_administrador("clientes.modificar")
        doc_orig_fmt = (doc_original or "").strip().upper()
        nuevo_doc_fmt = (nuevo_doc or "").strip().upper()
        nombre_fmt = (nuevo_nombre or "").strip()
        if not doc_orig_fmt or not nuevo_doc_fmt or not nombre_fmt:
            raise ValidacionError("Documento y nombre son obligatorios.")

        with transaccion() as conn:
            cursor = conn.cursor()
            if doc_orig_fmt != nuevo_doc_fmt:
                cursor.execute(
                    "SELECT 1 FROM clientes WHERE documento = %s LIMIT 1",
                    (nuevo_doc_fmt,),
                )
                if cursor.fetchone():
                    return False

            cursor.execute(
                """
                UPDATE clientes
                SET documento = %s, nombre = %s, telefono = %s, direccion = %s
                WHERE documento = %s AND activo = 1
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
            registrar_evento(cursor, "ACTUALIZAR", "cliente", nuevo_doc_fmt, nombre_fmt)
        return True

    def eliminar_cliente(self, documento: str) -> bool:
        """Desactiva un cliente por documento sin borrar su historial."""
        return self.cambiar_estado_cliente(documento, False)

    def cambiar_estado_cliente(self, documento: str, activo: bool) -> bool:
        """Activa o desactiva un cliente conservando su historial."""
        requerir_administrador("clientes.modificar")
        doc_fmt = (documento or "").strip().upper()
        if not (
            isinstance(activo, bool)
            or type(activo) is int and activo in (0, 1)
        ):
            raise ValidacionError("El estado activo debe ser verdadero o falso.")
        estado = int(activo)
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET activo = %s "
                "WHERE documento = %s AND activo != %s",
                (estado, doc_fmt, estado),
            )
            actualizado = cursor.rowcount == 1
            if actualizado:
                registrar_evento(
                    cursor,
                    "ACTIVAR" if estado else "DESACTIVAR",
                    "cliente",
                    doc_fmt,
                )
            return actualizado
