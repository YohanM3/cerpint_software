import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent.parent / "ferreteria.db"


def obtener_conexion():
    """Devuelve una conexión a la base de datos SQLite con timeout para evitar bloqueos."""
    conn = sqlite3.connect(str(DB_NAME), timeout=5)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
    except Exception:
        conn.close()
        raise
    return conn


@contextmanager
def transaccion():
    """Confirma al salir, revierte ante errores y siempre cierra la conexión."""
    conn = obtener_conexion()
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def _asegurar_columna(cursor, tabla: str, columna: str, definicion: str):
    columnas = {fila[1] for fila in cursor.execute(f"PRAGMA table_info({tabla})")}
    if columna not in columnas:
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


def inicializar_base_de_datos():
    """Crea las tablas necesarias si no existen."""
    with closing(obtener_conexion()) as conn:
        with conn:
            cursor = conn.cursor()

            cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT UNIQUE NOT NULL CHECK (length(trim(documento)) > 0),
            nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
            telefono TEXT,
            direccion TEXT
        )
    """)

            cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL CHECK (length(trim(codigo)) > 0),
            nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
            precio REAL NOT NULL CHECK (precio >= 0),
            precio_centavos INTEGER CHECK (precio_centavos IS NULL OR precio_centavos >= 0),
            stock INTEGER NOT NULL CHECK (stock >= 0),
            stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0)
        )
    """)

            cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_documento TEXT NOT NULL,
            total REAL NOT NULL CHECK (total >= 0),
            total_centavos INTEGER CHECK (total_centavos IS NULL OR total_centavos >= 0),
            estado TEXT NOT NULL DEFAULT 'Pagado',
            metodo_pago TEXT NOT NULL DEFAULT 'No especificado',
            FOREIGN KEY (cliente_documento) REFERENCES clientes(documento)
        )
    """)

            cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalles_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_codigo TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
            subtotal REAL NOT NULL CHECK (subtotal >= 0),
            precio_unitario_centavos INTEGER CHECK (precio_unitario_centavos IS NULL OR precio_unitario_centavos >= 0),
            subtotal_centavos INTEGER CHECK (subtotal_centavos IS NULL OR subtotal_centavos >= 0),
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_codigo) REFERENCES productos(codigo)
        )
    """)

            columnas_monetarias = (
                (
                    "productos",
                    "precio_centavos",
                    "INTEGER CHECK (precio_centavos IS NULL OR precio_centavos >= 0)",
                ),
                (
                    "ventas",
                    "total_centavos",
                    "INTEGER CHECK (total_centavos IS NULL OR total_centavos >= 0)",
                ),
                (
                    "detalles_venta",
                    "precio_unitario_centavos",
                    "INTEGER CHECK (precio_unitario_centavos IS NULL OR precio_unitario_centavos >= 0)",
                ),
                (
                    "detalles_venta",
                    "subtotal_centavos",
                    "INTEGER CHECK (subtotal_centavos IS NULL OR subtotal_centavos >= 0)",
                ),
            )
            for tabla, columna, definicion in columnas_monetarias:
                _asegurar_columna(cursor, tabla, columna, definicion)

            _asegurar_columna(
                cursor,
                "productos",
                "stock_minimo",
                "INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0)",
            )
            _asegurar_columna(
                cursor,
                "ventas",
                "estado",
                "TEXT NOT NULL DEFAULT 'Pagado'",
            )
            _asegurar_columna(
                cursor,
                "ventas",
                "metodo_pago",
                "TEXT NOT NULL DEFAULT 'No especificado'",
            )
            _asegurar_columna(
                cursor,
                "ventas",
                "dias_credito",
                "INTEGER NOT NULL DEFAULT 0 CHECK (dias_credito >= 0)",
            )
            _asegurar_columna(cursor, "ventas", "fecha_vencimiento", "TEXT")
            _asegurar_columna(cursor, "ventas", "fecha_anulacion", "TEXT")
            _asegurar_columna(cursor, "ventas", "motivo_anulacion", "TEXT")
            cursor.execute("""
                UPDATE ventas
                SET dias_credito = 30
                WHERE dias_credito < 1
                  AND LOWER(TRIM(estado)) IN ('pendiente', 'a credito', 'a crédito')
                """)
            cursor.execute("""
                UPDATE ventas
                SET fecha_vencimiento = DATE(fecha, '+' || dias_credito || ' days')
                WHERE fecha_vencimiento IS NULL
                  AND LOWER(TRIM(estado)) IN ('pendiente', 'a credito', 'a crédito')
                """)
            cursor.execute("""
                UPDATE ventas
                SET dias_credito = 0, fecha_vencimiento = NULL
                WHERE LOWER(TRIM(estado)) IN ('pagado', 'contado')
                """)
            cursor.execute("""
                UPDATE ventas
                SET estado = 'A Credito'
                WHERE LOWER(TRIM(estado)) IN ('pendiente', 'a crédito')
                """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos_cuentas_por_cobrar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    monto REAL NOT NULL CHECK (monto > 0),
                    metodo_pago TEXT NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ventas_cliente_fecha "
                "ON ventas(cliente_documento, fecha)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ventas_estado_fecha "
                "ON ventas(estado, fecha)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_detalles_producto_venta "
                "ON detalles_venta(producto_codigo, venta_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_pagos_venta_fecha "
                "ON pagos_cuentas_por_cobrar(venta_id, fecha)"
            )

            cursor.execute(
                "UPDATE productos SET precio_centavos = CAST(ROUND(precio * 100) AS INTEGER) WHERE precio_centavos IS NULL"
            )
            cursor.execute(
                "UPDATE ventas SET total_centavos = CAST(ROUND(total * 100) AS INTEGER) WHERE total_centavos IS NULL"
            )
            cursor.execute(
                "UPDATE detalles_venta SET precio_unitario_centavos = CAST(ROUND(precio_unitario * 100) AS INTEGER) WHERE precio_unitario_centavos IS NULL"
            )
            cursor.execute(
                "UPDATE detalles_venta SET subtotal_centavos = CAST(ROUND(subtotal * 100) AS INTEGER) WHERE subtotal_centavos IS NULL"
            )

            cursor.executescript("""
                CREATE TRIGGER IF NOT EXISTS validar_cliente_insert
                BEFORE INSERT ON clientes
                WHEN length(trim(NEW.documento)) = 0 OR length(trim(NEW.nombre)) = 0
                BEGIN SELECT RAISE(ABORT, 'documento y nombre son obligatorios'); END;

                CREATE TRIGGER IF NOT EXISTS validar_cliente_update
                BEFORE UPDATE OF documento, nombre ON clientes
                WHEN length(trim(NEW.documento)) = 0 OR length(trim(NEW.nombre)) = 0
                BEGIN SELECT RAISE(ABORT, 'documento y nombre son obligatorios'); END;

                CREATE TRIGGER IF NOT EXISTS validar_producto_insert
                BEFORE INSERT ON productos
                WHEN length(trim(NEW.codigo)) = 0 OR length(trim(NEW.nombre)) = 0
                    OR NEW.precio < 0 OR NEW.precio_centavos IS NULL
                    OR NEW.precio_centavos < 0
                    OR NEW.precio_centavos != CAST(ROUND(NEW.precio * 100) AS INTEGER)
                    OR NEW.stock < 0
                BEGIN SELECT RAISE(ABORT, 'producto inválido'); END;

                CREATE TRIGGER IF NOT EXISTS validar_producto_update
                BEFORE UPDATE OF codigo, nombre, precio, precio_centavos, stock ON productos
                WHEN length(trim(NEW.codigo)) = 0 OR length(trim(NEW.nombre)) = 0
                    OR NEW.precio < 0 OR NEW.precio_centavos IS NULL
                    OR NEW.precio_centavos < 0
                    OR NEW.precio_centavos != CAST(ROUND(NEW.precio * 100) AS INTEGER)
                    OR NEW.stock < 0
                BEGIN SELECT RAISE(ABORT, 'producto inválido'); END;

                CREATE TRIGGER IF NOT EXISTS validar_venta_insert
                BEFORE INSERT ON ventas
                WHEN NEW.cliente_documento IS NULL OR length(trim(NEW.cliente_documento)) = 0
                    OR NEW.total < 0 OR NEW.total_centavos IS NULL
                    OR NEW.total_centavos < 0
                    OR NEW.total_centavos != CAST(ROUND(NEW.total * 100) AS INTEGER)
                BEGIN SELECT RAISE(ABORT, 'venta inválida'); END;

                CREATE TRIGGER IF NOT EXISTS validar_venta_update
                BEFORE UPDATE OF cliente_documento, total, total_centavos ON ventas
                WHEN NEW.cliente_documento IS NULL OR length(trim(NEW.cliente_documento)) = 0
                    OR NEW.total < 0 OR NEW.total_centavos IS NULL
                    OR NEW.total_centavos < 0
                    OR NEW.total_centavos != CAST(ROUND(NEW.total * 100) AS INTEGER)
                BEGIN SELECT RAISE(ABORT, 'venta inválida'); END;

                CREATE TRIGGER IF NOT EXISTS validar_detalle_insert
                BEFORE INSERT ON detalles_venta
                WHEN NEW.cantidad <= 0 OR NEW.precio_unitario < 0 OR NEW.subtotal < 0
                    OR NEW.precio_unitario_centavos IS NULL OR NEW.precio_unitario_centavos < 0
                    OR NEW.subtotal_centavos IS NULL OR NEW.subtotal_centavos < 0
                    OR NEW.precio_unitario_centavos != CAST(ROUND(NEW.precio_unitario * 100) AS INTEGER)
                    OR NEW.subtotal_centavos != CAST(ROUND(NEW.subtotal * 100) AS INTEGER)
                BEGIN SELECT RAISE(ABORT, 'detalle de venta inválido'); END;

                CREATE TRIGGER IF NOT EXISTS validar_detalle_update
                BEFORE UPDATE OF cantidad, precio_unitario, subtotal,
                    precio_unitario_centavos, subtotal_centavos ON detalles_venta
                WHEN NEW.cantidad <= 0 OR NEW.precio_unitario < 0 OR NEW.subtotal < 0
                    OR NEW.precio_unitario_centavos IS NULL OR NEW.precio_unitario_centavos < 0
                    OR NEW.subtotal_centavos IS NULL OR NEW.subtotal_centavos < 0
                    OR NEW.precio_unitario_centavos != CAST(ROUND(NEW.precio_unitario * 100) AS INTEGER)
                    OR NEW.subtotal_centavos != CAST(ROUND(NEW.subtotal * 100) AS INTEGER)
                BEGIN SELECT RAISE(ABORT, 'detalle de venta inválido'); END;
            """)


def inicializar_bd():
    """Alias de compatibilidad para código antiguo."""
    inicializar_base_de_datos()
