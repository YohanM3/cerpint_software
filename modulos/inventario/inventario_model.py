from contextlib import closing
from decimal import Decimal, InvalidOperation

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


class InventarioModel:
    def __init__(self):
        pass

    def agregar_producto(
        self, codigo: str, nombre: str, precio: float, stock: int
    ) -> bool:
        """Inserta un nuevo producto estandarizando el código a mayúsculas."""
        codigo_original = (codigo or "").strip().upper()
        codigo_fmt = self.normalizar_codigo_producto(codigo_original)
        nombre_fmt = (nombre or "").strip()
        precio_fmt, stock_fmt = self._validar_datos(nombre_fmt, precio, stock)
        if not codigo_fmt:
            raise ValidacionError("El código del producto es obligatorio.")

        with transaccion() as conn:
            cursor = conn.cursor()
            if self._existe_codigo(cursor, codigo_original, codigo_fmt):
                return False
            cursor.execute(
                """
                INSERT INTO productos (codigo, nombre, precio, precio_centavos, stock)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    codigo_fmt,
                    nombre_fmt,
                    precio_fmt,
                    int(Decimal(str(precio_fmt)) * 100),
                    stock_fmt,
                ),
            )
        return True

    @staticmethod
    def _validar_datos(nombre: str, precio, stock) -> tuple[float, int]:
        if not nombre:
            raise ValidacionError("El nombre del producto es obligatorio.")
        try:
            precio_decimal = Decimal(str(precio)).quantize(Decimal("0.01"))
            stock_decimal = Decimal(str(stock))
        except (InvalidOperation, ValueError):
            raise ValidacionError(
                "Precio o stock tienen un formato inválido."
            ) from None

        if not precio_decimal.is_finite() or precio_decimal < 0:
            raise ValidacionError("El precio debe ser un número finito no negativo.")
        if (
            not stock_decimal.is_finite()
            or stock_decimal != stock_decimal.to_integral_value()
        ):
            raise ValidacionError("El stock debe ser un número entero no negativo.")
        if stock_decimal < 0:
            raise ValidacionError("El stock debe ser un número entero no negativo.")
        return float(precio_decimal), int(stock_decimal)

    @staticmethod
    def _existe_codigo(cursor, codigo_original: str, codigo_normalizado: str) -> bool:
        cursor.execute(
            "SELECT 1 FROM productos WHERE UPPER(codigo) IN (?, ?) LIMIT 1",
            (codigo_original, codigo_normalizado),
        )
        return cursor.fetchone() is not None

    def obtener_todos(self):
        """Devuelve todos los productos ordenados por nombre."""
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT codigo, nombre, precio_centavos / 100.0, stock
                FROM productos ORDER BY nombre
                """)
            return cursor.fetchall()

    def normalizar_codigo_producto(self, texto: str) -> str:
        """Normaliza referencias comunes de producto, por ejemplo PROD-001, P001 o 001."""
        valor = (texto or "").strip().upper().replace(" ", "")
        if not valor:
            return ""

        if valor.startswith("PROD-"):
            return valor

        if valor.startswith("PROD"):
            resto = valor[4:]
            if resto.startswith("-"):
                return f"PROD{resto}"
            if resto.isdigit():
                return f"PROD-{resto}"

        if valor.startswith("P") and valor[1:].isdigit():
            return f"PROD-{valor[1:]}"

        if valor.isdigit():
            return f"PROD-{valor}"

        return valor

    def obtener_por_codigo(self, codigo: str):
        """Busca un producto por código exacto, aceptando variantes como P001."""
        codigo_original = (codigo or "").strip().upper()
        codigo_fmt = self.normalizar_codigo_producto(codigo_original)
        if not codigo_original:
            return None

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT codigo, nombre, precio_centavos / 100.0, stock
                FROM productos
                WHERE UPPER(codigo) IN (?, ?)
                ORDER BY CASE WHEN UPPER(codigo) = ? THEN 0 ELSE 1 END
                LIMIT 1
                """,
                (codigo_original, codigo_fmt, codigo_original),
            )
            return cursor.fetchone()

    def obtener_por_codigo_o_nombre(self, texto: str):
        """Busca un producto por código o nombre, de forma simple y clara."""
        valor = (texto or "").strip()
        if not valor:
            return None

        producto = self.obtener_por_codigo(valor)
        if producto:
            return producto

        nombre_fmt = valor.upper()
        nombre_like = f"%{nombre_fmt}%"

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT codigo, nombre, precio_centavos / 100.0, stock FROM productos
                WHERE UPPER(nombre) = ? OR UPPER(nombre) LIKE ?
                ORDER BY CASE WHEN UPPER(nombre) = ? THEN 0 ELSE 1 END
                LIMIT 1
                """,
                (nombre_fmt, nombre_like, nombre_fmt),
            )
            return cursor.fetchone()

    def buscar_sugerencias(self, texto: str, limite: int = 5) -> list:
        """Busca productos coincidentes por código o nombre."""
        valor = (texto or "").strip().upper()
        if not valor:
            return []
        normalizado = self.normalizar_codigo_producto(valor)
        filtro_original = f"%{valor}%"
        filtro_normalizado = f"%{normalizado}%"
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT codigo, nombre, precio_centavos / 100.0, stock FROM productos
                WHERE UPPER(codigo) LIKE ? OR UPPER(codigo) LIKE ?
                    OR UPPER(nombre) LIKE ?
                ORDER BY nombre
                LIMIT ?
                """,
                (
                    filtro_original,
                    filtro_normalizado,
                    filtro_original,
                    max(1, int(limite)),
                ),
            )
            return cursor.fetchall()

    def actualizar_producto(
        self,
        codigo_original: str,
        nuevo_codigo: str,
        nuevo_nombre: str,
        nuevo_precio: float,
        nuevo_stock: int,
    ) -> bool:
        """Actualiza un producto existente en la base de datos."""
        cod_orig_fmt = (codigo_original or "").strip().upper()
        nuevo_cod_original = (nuevo_codigo or "").strip().upper()
        nuevo_cod_fmt = self.normalizar_codigo_producto(nuevo_cod_original)
        nombre_fmt = (nuevo_nombre or "").strip()
        precio_fmt, stock_fmt = self._validar_datos(
            nombre_fmt, nuevo_precio, nuevo_stock
        )
        if not cod_orig_fmt or not nuevo_cod_fmt:
            raise ValidacionError("El código del producto es obligatorio.")

        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM productos
                WHERE UPPER(codigo) IN (?, ?) AND UPPER(codigo) != ?
                LIMIT 1
                """,
                (nuevo_cod_original, nuevo_cod_fmt, cod_orig_fmt),
            )
            if cursor.fetchone():
                return False

            cursor.execute(
                """
                UPDATE productos
                SET codigo = ?, nombre = ?, precio = ?, precio_centavos = ?, stock = ?
                WHERE UPPER(codigo) = ?
                """,
                (
                    nuevo_cod_fmt,
                    nombre_fmt,
                    precio_fmt,
                    int(Decimal(str(precio_fmt)) * 100),
                    stock_fmt,
                    cod_orig_fmt,
                ),
            )
            if cursor.rowcount != 1:
                raise RegistroNoEncontradoError("El producto ya no existe.")
        return True

    def eliminar_producto(self, codigo: str) -> bool:
        """Elimina un producto por su código."""
        codigo_fmt = (codigo or "").strip().upper()
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM productos WHERE UPPER(codigo) = ?", (codigo_fmt,)
            )
            return cursor.rowcount == 1
