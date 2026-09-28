from decimal import Decimal, InvalidOperation

from database.conexion import transaccion
from database.errores import InventarioInsuficienteError, ValidacionError


class VentasModel:
    def __init__(self):
        self.carrito = []

    def agregar_item(
        self, codigo: str, producto: str, cantidad: int, precio_unitario: float
    ):
        """Agrega un producto al carrito formateando el código."""
        codigo_fmt = (codigo or "").strip().upper()
        producto_fmt = (producto or "").strip()
        if not codigo_fmt or not producto_fmt:
            raise ValidacionError("El código y nombre del producto son obligatorios.")
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValidacionError("La cantidad debe ser un entero mayor a cero.")
        try:
            precio = Decimal(str(precio_unitario)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValidacionError("El precio del producto no es válido.") from None
        if not precio.is_finite() or precio < 0:
            raise ValidacionError("El precio debe ser finito y no negativo.")
        subtotal = (cantidad * precio).quantize(Decimal("0.01"))
        self.carrito.append(
            {
                "codigo": codigo_fmt,
                "producto": producto_fmt,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal,
            }
        )

    def obtener_items_tabla(self):
        """Devuelve el carrito listo para mostrar en la tabla."""
        return [
            [
                item["codigo"],
                item["producto"],
                item["cantidad"],
                item["precio"],
                item["subtotal"],
            ]
            for item in self.carrito
        ]

    def calcular_total(self) -> Decimal:
        """Devuelve el subtotal acumulado del carrito."""
        return sum(
            (item["subtotal"] for item in self.carrito), start=Decimal("0.00")
        ).quantize(Decimal("0.01"))

    def eliminar_item(self, codigo: str):
        """Elimina un producto del carrito por código."""
        codigo_fmt = (codigo or "").strip().upper()
        if not codigo_fmt:
            return False
        antes = len(self.carrito)
        self.carrito = [item for item in self.carrito if item["codigo"] != codigo_fmt]
        return len(self.carrito) < antes

    def procesar_venta_bd(self, cliente_doc=None, estado="Pagado", dias_credito=30):
        """Descuenta stock y guarda cabecera/detalles, retornando el ID de la venta y datos del cliente."""
        if not self.carrito:
            return None, None
        cliente_fmt = (cliente_doc or "").strip().upper()
        if not cliente_fmt:
            raise ValidacionError(
                "Debe seleccionar un cliente antes de emitir la venta."
            )
        estados_validos = {
            "pagado": "Pagado",
            "contado": "Pagado",
            "pendiente": "Pendiente",
            "a credito": "A Credito",
        }
        estado_fmt = estados_validos.get((estado or "").strip().casefold())
        if estado_fmt is None:
            raise ValidacionError("El estado debe ser Pagado, Pendiente o A Credito.")
        es_credito = estado_fmt != "Pagado"
        if es_credito:
            try:
                dias_credito_decimal = Decimal(str(dias_credito).strip())
            except (InvalidOperation, ValueError):
                raise ValidacionError(
                    "Los días de crédito deben ser un entero mayor a cero."
                ) from None
            if (
                not dias_credito_decimal.is_finite()
                or dias_credito_decimal != dias_credito_decimal.to_integral_value()
                or dias_credito_decimal < 1
            ):
                raise ValidacionError(
                    "Los días de crédito deben ser un entero mayor a cero."
                )
            dias_credito = int(dias_credito_decimal)
        else:
            dias_credito = 0

        total = self.calcular_total()
        with transaccion() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT documento, nombre, telefono, direccion FROM clientes WHERE UPPER(documento) = ?",
                (cliente_fmt,),
            )
            cliente_info = cursor.fetchone()
            if not cliente_info:
                raise ValidacionError(
                    "El cliente seleccionado no existe en el sistema."
                )

            cliente_data = {
                "documento": cliente_info[0],
                "nombre": cliente_info[1],
                "telefono": cliente_info[2],
                "direccion": cliente_info[3],
            }

            for item in self.carrito:
                cursor.execute(
                    """
                    UPDATE productos SET stock = stock - ?
                    WHERE codigo = ? AND stock >= ?
                    """,
                    (item["cantidad"], item["codigo"], item["cantidad"]),
                )
                if cursor.rowcount != 1:
                    cursor.execute(
                        "SELECT stock FROM productos WHERE codigo = ?",
                        (item["codigo"],),
                    )
                    fila = cursor.fetchone()
                    disponible = fila[0] if fila else 0
                    raise InventarioInsuficienteError(item["codigo"], disponible)

            cursor.execute(
                """
                INSERT INTO ventas (
                    cliente_documento, total, total_centavos, estado,
                    dias_credito, fecha_vencimiento
                )
                VALUES (?, ?, ?, ?, ?, CASE WHEN ? THEN DATE('now', '+' || ? || ' days') END)
                """,
                (
                    cliente_fmt,
                    float(total),
                    int(total * 100),
                    estado_fmt,
                    dias_credito,
                    es_credito,
                    dias_credito,
                ),
            )
            venta_id = cursor.lastrowid
            cursor.execute(
                "SELECT fecha, dias_credito, fecha_vencimiento FROM ventas WHERE id = ?",
                (venta_id,),
            )
            venta_info = cursor.fetchone()
            cliente_data["fecha_emision"] = venta_info[0]
            cliente_data["dias_credito"] = venta_info[1]
            cliente_data["fecha_vencimiento"] = venta_info[2]

            for item in self.carrito:
                cursor.execute(
                    """
                    INSERT INTO detalles_venta (
                        venta_id, producto_codigo, cantidad, precio_unitario,
                        subtotal, precio_unitario_centavos, subtotal_centavos
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        venta_id,
                        item["codigo"],
                        item["cantidad"],
                        float(item["precio"]),
                        float(item["subtotal"]),
                        int(item["precio"] * 100),
                        int(item["subtotal"] * 100),
                    ),
                )

            items_procesados = [
                {
                    "codigo": item["codigo"],
                    "nombre": item["producto"],
                    "cantidad": item["cantidad"],
                    "precio": float(item["precio"]),
                    "subtotal": float(item["subtotal"]),
                }
                for item in self.carrito
            ]

        self.vaciar_carrito()
        return venta_id, cliente_data, items_procesados, float(total)

    def vaciar_carrito(self):
        self.carrito.clear()

    @staticmethod
    def obtener_ventas_por_cliente(cliente_id):
        """Devuelve el historial de ventas registradas para un cliente."""
        from database.conexion import obtener_conexion

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, fecha, total, total_centavos, estado
            FROM ventas
            WHERE cliente_documento = ?
            ORDER BY fecha DESC
        """,
            (str(cliente_id).strip().upper(),),
        )
        filas = cursor.fetchall()
        conn.close()
        return [
            {
                "venta_id": f[0],
                "numero_serie": f"{f[0]:05d}",
                "fecha": f[1],
                "total": f[2],
                "estado_pago": f[4],
                "total_centavos": f[3],
            }
            for f in filas
        ]

    @staticmethod
    def obtener_detalle_venta(venta_id):
        """Recupera los datos completos de una venta para reimprimir el PDF o consultar."""
        from database.conexion import obtener_conexion

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
                 SELECT v.id, v.fecha, v.total, v.cliente_documento,
                     c.nombre, c.telefono, c.direccion, v.estado
            FROM ventas v
            JOIN clientes c ON c.documento = v.cliente_documento
            WHERE v.id = ?
        """,
            (venta_id,),
        )
        venta = cursor.fetchone()
        if not venta:
            conn.close()
            return None

        cursor.execute(
            """
            SELECT d.producto_codigo, p.nombre, d.cantidad, d.precio_unitario, d.subtotal
            FROM detalles_venta d
            JOIN productos p ON p.codigo = d.producto_codigo
            WHERE d.venta_id = ?
        """,
            (venta_id,),
        )
        detalles = cursor.fetchall()
        conn.close()

        items = [
            {
                "codigo": d[0],
                "nombre": d[1],
                "cantidad": d[2],
                "precio": d[3],
                "subtotal": d[4],
            }
            for d in detalles
        ]

        return {
            "venta_id": venta[0],
            "numero_serie": f"{venta[0]:05d}",
            "fecha": venta[1],
            "total": venta[2],
            "estado_pago": venta[7],
            "cliente": {
                "documento": venta[3],
                "nombre": venta[4],
                "telefono": venta[5] or "N/A",
                "direccion": venta[6] or "N/A",
            },
            "items": items,
        }
