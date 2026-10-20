import os
import threading
from contextlib import contextmanager

from mysql.connector.pooling import MySQLConnectionPool

MYSQL_DATABASE = os.getenv("FERRETERIA_DB_NAME", "ferreteria_cerpint")


TAMANO_POOL = 5
_pool = None
_candado_pool = threading.Lock()


class CursorMySQL:
    """Cursor que devuelve self en execute para poder encadenar fetchone/fetchall."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, parametros=()):
        self._cursor.execute(sql, parametros)
        return self

    def executemany(self, sql, parametros):
        self._cursor.executemany(sql, parametros)
        return self

    def __getattr__(self, nombre):
        return getattr(self._cursor, nombre)


class ConexionMySQL:
    """Conexión con execute() directo; close() devuelve la conexión al pool."""

    def __init__(self, conexion):
        self._conexion = conexion

    def cursor(self):
        return CursorMySQL(self._conexion.cursor())

    def execute(self, sql, parametros=()):
        return self.cursor().execute(sql, parametros)

    def __getattr__(self, nombre):
        return getattr(self._conexion, nombre)


def _obtener_pool():
    global _pool
    with _candado_pool:
        if _pool is None:
            _pool = MySQLConnectionPool(
                pool_name="ferreteria_cerpint",
                pool_size=TAMANO_POOL,
                host=os.getenv("FERRETERIA_DB_HOST", "localhost"),
                port=int(os.getenv("FERRETERIA_DB_PORT", "3307")),
                user=os.getenv("FERRETERIA_DB_USER", "ferreteria_app"),
                password=os.getenv("FERRETERIA_DB_PASSWORD", ""),
                database=MYSQL_DATABASE,
                charset="utf8mb4",
                autocommit=False,
            )
        return _pool


def obtener_conexion():
    """Toma una conexión del pool a MySQL/MariaDB."""
    return ConexionMySQL(_obtener_pool().get_connection())


@contextmanager
def transaccion():
    """Confirma la transacción al salir y revierte ante errores."""
    conn = obtener_conexion()
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_base_de_datos():
    """Comprueba que el esquema MySQL requerido exista."""
    tablas_requeridas = {
        "clientes",
        "productos",
        "ventas",
        "detalles_venta",
        "usuarios",
        "auditoria",
        "pagos_cuentas_por_cobrar",
        "roles",
        "permisos_roles",
    }
    columnas_requeridas = {
        "clientes": {"activo"},
        "productos": {
            "activo",
            "stock_minimo",
            "proveedor",
            "marca",
            "codigo_empresa",
        },
        "usuarios": {"correo", "codigo_recuperacion", "recuperacion_expira_en"},
    }
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s",
            (MYSQL_DATABASE,),
        )
        tablas_existentes = {fila[0] for fila in cursor.fetchall()}
        faltantes = tablas_requeridas - tablas_existentes
        if faltantes:
            raise RuntimeError(
                "Faltan tablas en MySQL/MariaDB: "
                + ", ".join(sorted(faltantes))
                + ". Verifique el esquema de la base de datos."
            )

        for tabla, requeridas in columnas_requeridas.items():
            cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s",
                (MYSQL_DATABASE, tabla),
            )
            existentes = {fila[0] for fila in cursor.fetchall()}
            faltantes = requeridas - existentes
            if faltantes:
                raise RuntimeError(
                    f"Faltan columnas en MySQL/MariaDB, tabla {tabla}: "
                    + ", ".join(sorted(faltantes))
                    + ". Verifique el esquema de la base de datos."
                )
    finally:
        conn.close()
