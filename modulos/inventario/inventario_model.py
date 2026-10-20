import re
from contextlib import closing
from decimal import Decimal, InvalidOperation
from database.conexion import obtener_conexion, transaccion
from database.errores import RegistroNoEncontradoError, ValidacionError
from servicios.auditoria import registrar_evento, requerir_administrador


class InventarioModel:
    _PATRON_CODIGO = re.compile(r"^[A-Z]{4}-[0-9]{4}$")

    def agregar_producto(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        stock: int,
        stock_minimo: float = 0,
        proveedor: str = "",
        marca: str = "",
        codigo_empresa: str = "",
    ) -> bool:
        """Inserta un nuevo producto estandarizando el código a mayúsculas."""
        requerir_administrador("inventario.modificar")
        codigo_original = (codigo or "").strip().upper()
        codigo_fmt = self.normalizar_codigo_producto(codigo_original)
        nombre_fmt = (nombre or "").strip()
        precio_fmt, stock_fmt = self._validar_datos(nombre_fmt, precio, stock)
        self._validar_codigo(codigo_fmt)
        stock_minimo_fmt = self._validar_stock_minimo(stock_minimo)

        with transaccion() as conn:
            cursor = conn.cursor()
            if self._existe_codigo(cursor, codigo_original, codigo_fmt):
                return False
            cursor.execute(
                """
                INSERT INTO productos (
                    codigo, nombre, precio, precio_centavos, stock, stock_minimo,
                    proveedor, marca, codigo_empresa
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    codigo_fmt,
                    nombre_fmt,
                    precio_fmt,
                    int(Decimal(str(precio_fmt)) * 100),
                    stock_fmt,
                    stock_minimo_fmt,
                    (proveedor or "").strip(),
                    (marca or "").strip(),
                    (codigo_empresa or "").strip(),
                ),
            )
            registrar_evento(cursor, "CREAR", "producto", codigo_fmt, nombre_fmt)
        return True

    @classmethod
    def _validar_codigo(cls, codigo: str):
        if not cls._PATRON_CODIGO.fullmatch(codigo or ""):
            raise ValidacionError(
                "El código interno debe tener el formato AAAA-0000 "
                "(cuatro letras y cuatro números)."
            )

    @staticmethod
    def _validar_stock_minimo(valor) -> float:
        try:
            minimo = Decimal(str(valor)).quantize(Decimal("0.001"))
        except (InvalidOperation, ValueError):
            raise ValidacionError("El stock mínimo debe ser numérico.") from None
        if not minimo.is_finite() or minimo < 0:
            raise ValidacionError("El stock mínimo debe ser finito y no negativo.")
        return float(minimo)

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
            "SELECT 1 FROM productos WHERE codigo IN (%s, %s) LIMIT 1",
            (codigo_original, codigo_normalizado),
        )
        return cursor.fetchone() is not None

    def obtener_todos(self):
        """Devuelve el catálogo completo, incluidos los productos inactivos."""
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT codigo, nombre, precio_centavos / 100.0, stock,
                       COALESCE(marca, ''), COALESCE(proveedor, ''),
                       stock_minimo, COALESCE(codigo_empresa, ''),
                       CASE WHEN activo = 1 THEN 'Activo' ELSE 'Inactivo' END
                FROM productos
                ORDER BY activo DESC, nombre
                """)
            return cursor.fetchall()

    def obtener_detalle_producto(self, codigo: str):
        """Obtiene los datos completos de un producto para su edición."""
        codigo_fmt = self.normalizar_codigo_producto(codigo or "")
        if not codigo_fmt:
            return None
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT codigo, nombre, precio_centavos / 100.0, stock,
                       stock_minimo, COALESCE(proveedor, ''),
                       COALESCE(marca, ''), COALESCE(codigo_empresa, '')
                FROM productos
                WHERE codigo = %s
                """,
                (codigo_fmt,),
            )
            return cursor.fetchone()

    def normalizar_codigo_producto(self, texto: str) -> str:
        """Normaliza códigos sin guion al formato interno AAAA-0000."""
        valor = (texto or "").strip().upper().replace(" ", "")
        if not valor:
            return ""
        if len(valor) == 8 and valor[:4].isalpha() and valor[4:].isdigit():
            return f"{valor[:4]}-{valor[4:]}"
        return valor

    def obtener_por_codigo(self, codigo: str):
        """Busca por código exacto y acepta el formato sin guion."""
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
                WHERE activo = 1 AND codigo IN (%s, %s)
                ORDER BY CASE WHEN codigo = %s THEN 0 ELSE 1 END
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
                WHERE activo = 1 AND (nombre = %s OR nombre LIKE %s)
                ORDER BY CASE WHEN nombre = %s THEN 0 ELSE 1 END
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
                WHERE activo = 1 AND (codigo LIKE %s OR codigo LIKE %s
                    OR nombre LIKE %s
                )
                ORDER BY nombre
                LIMIT %s
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
        stock_minimo: float | None = None,
        proveedor: str | None = None,
        marca: str | None = None,
        codigo_empresa: str | None = None,
    ) -> bool:
        """Actualiza un producto existente en la base de datos."""
        requerir_administrador("inventario.modificar")
        cod_orig_fmt = self.normalizar_codigo_producto(codigo_original or "")
        nuevo_cod_original = (nuevo_codigo or "").strip().upper()
        nuevo_cod_fmt = self.normalizar_codigo_producto(nuevo_cod_original)
        nombre_fmt = (nuevo_nombre or "").strip()
        precio_fmt, stock_fmt = self._validar_datos(
            nombre_fmt, nuevo_precio, nuevo_stock
        )
        stock_minimo_fmt = (
            self._validar_stock_minimo(stock_minimo)
            if stock_minimo is not None
            else None
        )
        if not cod_orig_fmt:
            raise ValidacionError("El código original del producto es obligatorio.")
        self._validar_codigo(nuevo_cod_fmt)

        with transaccion() as conn:
            cursor = conn.cursor()
            valores = [
                "codigo = %s",
                "nombre = %s",
                "precio = %s",
                "precio_centavos = %s",
                "stock = %s",
            ]
            parametros = [
                nuevo_cod_fmt,
                nombre_fmt,
                precio_fmt,
                int(Decimal(str(precio_fmt)) * 100),
                stock_fmt,
            ]
            if stock_minimo is not None:
                valores.append("stock_minimo = %s")
                parametros.append(stock_minimo_fmt)
            for columna, valor in (
                ("proveedor", proveedor),
                ("marca", marca),
                ("codigo_empresa", codigo_empresa),
            ):
                if valor is not None:
                    valores.append(f"{columna} = %s")
                    parametros.append((valor or "").strip())
            cursor.execute(
                """
                SELECT 1 FROM productos
                WHERE codigo IN (%s, %s) AND codigo != %s
                LIMIT 1
                """,
                (nuevo_cod_original, nuevo_cod_fmt, cod_orig_fmt),
            )
            if cursor.fetchone():
                return False

            consulta = (
                "UPDATE productos SET "
                + ", ".join(valores)
                + " WHERE codigo = %s AND activo = 1"
            )
            cursor.execute(
                consulta,
                (*parametros, cod_orig_fmt),
            )
            if cursor.rowcount != 1:
                raise RegistroNoEncontradoError("El producto ya no existe.")
            registrar_evento(
                cursor, "ACTUALIZAR", "producto", nuevo_cod_fmt, nombre_fmt
            )
        return True

    def eliminar_producto(self, codigo: str) -> bool:
        """Desactiva un producto por su código sin borrar su historial."""
        return self.cambiar_estado_producto(codigo, False)

    def cambiar_estado_producto(self, codigo: str, activo: bool) -> bool:
        """Activa o desactiva un producto conservando su registro."""
        requerir_administrador("inventario.modificar")
        codigo_fmt = self.normalizar_codigo_producto(codigo or "")
        if not (
            isinstance(activo, bool)
            or (type(activo) is int and activo in (0, 1))
        ):
            raise ValidacionError("El estado activo debe ser verdadero o falso.")
        estado = int(activo)
        with transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET activo = %s "
                "WHERE codigo = %s AND activo != %s",
                (estado, codigo_fmt, estado),
            )
            actualizado = cursor.rowcount == 1
            if actualizado:
                registrar_evento(
                    cursor,
                    "ACTIVAR" if estado else "DESACTIVAR",
                    "producto",
                    codigo_fmt,
                )
            return actualizado
