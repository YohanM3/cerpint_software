import csv
import sqlite3
from contextlib import closing
from datetime import date
from decimal import Decimal, InvalidOperation
from servicios.auditoria import registrar_evento
from servicios.respaldo import crear_respaldo

try:
    from database.conexion import obtener_conexion, transaccion
    from database.errores import ValidacionError
except ModuleNotFoundError:
    import os
    import sys

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )
    from database.conexion import obtener_conexion, transaccion
    from database.errores import ValidacionError


class ConsultasModel:
    """Modela las consultas y reportes del sistema."""

    @staticmethod
    def formatear_moneda(monto) -> str:
        """Convierte un importe numérico a la representación usada por la interfaz."""
        try:
            valor = Decimal(str(monto if monto is not None else 0)).quantize(
                Decimal("0.01")
            )
        except (InvalidOperation, ValueError):
            valor = Decimal("0.00")
        return f"{valor:,.2f}"

    @staticmethod
    def _consultar(sql: str, parametros=()):
        """Ejecuta una consulta parametrizada y retorna filas como diccionarios."""
        try:
            with closing(obtener_conexion()) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, parametros)
                columnas = [columna[0] for columna in cursor.description]
                return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        except sqlite3.Error as error:
            raise RuntimeError(f"No se pudo completar la consulta: {error}") from error

    @staticmethod
    def _validar_rango_fechas(fecha_inicio: str, fecha_fin: str):
        inicio = (fecha_inicio or "").strip()
        fin = (fecha_fin or "").strip()
        try:
            inicio_fecha = date.fromisoformat(inicio)
            fin_fecha = date.fromisoformat(fin)
        except (TypeError, ValueError):
            raise ValidacionError(
                "Las fechas deben tener formato YYYY-MM-DD."
            ) from None
        if inicio_fecha > fin_fecha:
            raise ValidacionError("La fecha inicial no puede ser posterior a la final.")
        return inicio, fin

    @staticmethod
    def obtener_notas_pendientes():
        """Lista notas pendientes o a crédito, con pagos acumulados y saldo."""
        return ConsultasModel._consultar("""
            SELECT v.id AS venta_id, v.fecha, v.cliente_documento,
                   c.nombre AS cliente_nombre, c.telefono AS cliente_telefono,
                    c.direccion AS cliente_direccion,
                    CASE WHEN v.dias_credito > 0 THEN 'A Credito' ELSE 'Contado' END AS estado,
                    v.total,
                   v.dias_credito, v.fecha_vencimiento,
                   CAST(julianday(date(v.fecha_vencimiento)) - julianday(date('now')) AS INTEGER)
                       AS dias_restantes,
                   CASE
                       WHEN date(v.fecha_vencimiento) < date('now') THEN 'Vencida'
                       ELSE 'Vigente'
                   END AS estado_vencimiento,
                   COALESCE(SUM(p.monto), 0) AS total_abonado,
                   MAX(v.total - COALESCE(SUM(p.monto), 0), 0) AS saldo_pendiente
            FROM ventas v
            JOIN clientes c ON c.documento = v.cliente_documento
            LEFT JOIN pagos_cuentas_por_cobrar p ON p.venta_id = v.id
                        WHERE LOWER(TRIM(v.estado)) IN ('pendiente', 'a credito', 'a crédito')
                            AND v.fecha_anulacion IS NULL
            GROUP BY v.id, v.fecha, v.cliente_documento, c.nombre, c.telefono,
                     c.direccion, v.estado, v.total, v.dias_credito,
                     v.fecha_vencimiento
            HAVING saldo_pendiente > 0
            ORDER BY v.fecha DESC, v.id DESC
            """)

    @staticmethod
    def marcar_venta_como_pendiente(venta_id):
        """Pasa una venta seleccionada a crédito sin modificar otras notas."""
        try:
            identificador = int(venta_id)
        except (TypeError, ValueError):
            raise ValidacionError("El número de nota no es válido.") from None
        if isinstance(venta_id, bool) or identificador < 1:
            raise ValidacionError("El número de nota no es válido.")

        try:
            crear_respaldo()
            with transaccion() as conn:
                cursor = conn.execute(
                    "UPDATE ventas SET estado = 'A Credito', "
                    "dias_credito = CASE WHEN dias_credito < 1 THEN 30 ELSE dias_credito END, "
                    "fecha_vencimiento = COALESCE(fecha_vencimiento, DATE('now', '+' || "
                    "CASE WHEN dias_credito < 1 THEN 30 ELSE dias_credito END || ' days')) "
                    "WHERE id = ? "
                    "AND fecha_anulacion IS NULL "
                    "AND LOWER(TRIM(estado)) NOT IN ('pendiente', 'a credito', 'a crédito')",
                    (identificador,),
                )
                actualizada = cursor.rowcount == 1
                if actualizada:
                    registrar_evento(
                        cursor,
                        "ACTUALIZAR",
                        "venta",
                        identificador,
                        "Marcada a crédito",
                    )
                return actualizada
        except sqlite3.Error as error:
            raise RuntimeError(f"No se pudo actualizar la nota: {error}") from error

    @staticmethod
    def alternar_pago_nota(venta_id):
        """Marca una nota como pagada o devuelve una pagada a su situación de deuda."""
        try:
            identificador = int(venta_id)
        except (TypeError, ValueError):
            raise ValidacionError("El número de nota no es válido.") from None
        if isinstance(venta_id, bool) or identificador < 1:
            raise ValidacionError("El número de nota no es válido.")

        try:
            crear_respaldo()
            with transaccion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT estado, dias_credito, fecha_vencimiento, fecha_anulacion "
                    "FROM ventas WHERE id = ?",
                    (identificador,),
                )
                venta = cursor.fetchone()
                if venta is None:
                    raise ValidacionError("La nota seleccionada no existe.")
                estado, dias_credito, fecha_vencimiento, fecha_anulacion = venta
                if fecha_anulacion:
                    raise ValidacionError(
                        "No se puede cambiar el pago de una nota anulada."
                    )

                esta_pagada = (estado or "").strip().casefold() in {
                    "pagado",
                    "contado",
                }
                if esta_pagada:
                    if int(dias_credito or 0) == 0:
                        cursor.execute(
                            "UPDATE ventas SET estado = 'A Credito', "
                            "fecha_vencimiento = DATE('now', '-1 day') WHERE id = ?",
                            (identificador,),
                        )
                    else:
                        cursor.execute(
                            "UPDATE ventas SET estado = 'A Credito', "
                            "fecha_vencimiento = COALESCE(fecha_vencimiento, "
                            "DATE(fecha, '+' || dias_credito || ' days')) WHERE id = ?",
                            (identificador,),
                        )
                    registrar_evento(
                        cursor,
                        "ACTUALIZAR",
                        "venta",
                        identificador,
                        "Estado: A Credito",
                    )
                    return "A Credito"

                if (estado or "").strip().casefold() not in {
                    "pendiente",
                    "a credito",
                    "a crédito",
                }:
                    raise ValidacionError(
                        "La situación de pago de la nota no es válida."
                    )
                cursor.execute(
                    "UPDATE ventas SET estado = 'Pagado' WHERE id = ?",
                    (identificador,),
                )
                registrar_evento(
                    cursor, "ACTUALIZAR", "venta", identificador, "Estado: Pagado"
                )
                return "Pagado"
        except sqlite3.Error as error:
            raise RuntimeError(
                f"No se pudo cambiar el estado de pago: {error}"
            ) from error

    @staticmethod
    def anular_venta(venta_id, motivo):
        """Anula una nota, conserva el historial y repone todo su inventario."""
        try:
            identificador = int(venta_id)
        except (TypeError, ValueError):
            raise ValidacionError("El número de nota no es válido.") from None
        if isinstance(venta_id, bool) or identificador < 1:
            raise ValidacionError("El número de nota no es válido.")
        motivo = (motivo or "").strip()
        if not motivo:
            raise ValidacionError("Debes indicar el motivo de la anulación.")

        try:
            crear_respaldo()
            with transaccion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT fecha_anulacion FROM ventas WHERE id = ?",
                    (identificador,),
                )
                venta = cursor.fetchone()
                if venta is None:
                    raise ValidacionError("La nota seleccionada no existe.")
                if venta[0]:
                    return False

                detalles = cursor.execute(
                    "SELECT producto_codigo, cantidad FROM detalles_venta "
                    "WHERE venta_id = ?",
                    (identificador,),
                ).fetchall()
                for codigo, cantidad in detalles:
                    cursor.execute(
                        "UPDATE productos SET stock = stock + ? WHERE codigo = ?",
                        (cantidad, codigo),
                    )
                    if cursor.rowcount != 1:
                        raise ValidacionError(
                            f"No se pudo reponer el producto {codigo}."
                        )

                cursor.execute(
                    "UPDATE ventas SET fecha_anulacion = CURRENT_TIMESTAMP, "
                    "motivo_anulacion = ? WHERE id = ? AND fecha_anulacion IS NULL",
                    (motivo, identificador),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("La nota ya fue anulada por otro proceso.")
                registrar_evento(cursor, "ANULAR", "venta", identificador, motivo)
                return True
        except sqlite3.Error as error:
            raise RuntimeError(f"No se pudo anular la nota: {error}") from error

    @staticmethod
    def obtener_historial_pagos_cliente(cliente_documento: str):
        """Lista abonos de cuentas por cobrar de un cliente."""
        cliente = (cliente_documento or "").strip().upper()
        if not cliente:
            raise ValidacionError("Debes indicar el documento del cliente.")
        return ConsultasModel._consultar(
            """
            SELECT p.id AS pago_id, p.venta_id, p.fecha, p.monto,
                   p.metodo_pago, v.cliente_documento
            FROM pagos_cuentas_por_cobrar p
            JOIN ventas v ON v.id = p.venta_id
            WHERE UPPER(v.cliente_documento) = ?
            ORDER BY p.fecha DESC, p.id DESC
            """,
            (cliente,),
        )

    @staticmethod
    def obtener_ventas_por_cliente(cliente_documento: str):
        """Devuelve todas las ventas de un cliente, de la más reciente a la más antigua."""
        cliente = (cliente_documento or "").strip().upper()
        if not cliente:
            raise ValidacionError("Debes indicar el documento del cliente.")
        return ConsultasModel._consultar(
            """
            SELECT v.id AS venta_id, v.fecha, v.cliente_documento,
                    c.nombre AS cliente_nombre, v.total,
                    CASE WHEN v.fecha_anulacion IS NOT NULL THEN 'Anulada'
                        WHEN LOWER(TRIM(v.estado)) IN ('pendiente', 'a credito', 'a crédito')
                        THEN 'A Credito' ELSE 'Contado' END AS estado,
                    v.metodo_pago
            FROM ventas v
            JOIN clientes c ON c.documento = v.cliente_documento
            WHERE UPPER(v.cliente_documento) = ?
            ORDER BY v.fecha DESC, v.id DESC
            """,
            (cliente,),
        )

    @staticmethod
    def obtener_top_clientes(limit: int = 5):
        """Devuelve clientes ordenados por monto acumulado de compras."""
        try:
            limite = int(limit)
        except (TypeError, ValueError):
            raise ValidacionError("El límite debe ser un entero positivo.") from None
        if isinstance(limit, bool) or limite < 1:
            raise ValidacionError("El límite debe ser un entero positivo.")
        return ConsultasModel._consultar(
            """
            SELECT c.documento, c.nombre, SUM(v.total) AS total_comprado,
                   COUNT(v.id) AS cantidad_ventas
            FROM clientes c
            JOIN ventas v ON v.cliente_documento = c.documento
                 WHERE v.fecha_anulacion IS NULL
            GROUP BY c.documento, c.nombre
            ORDER BY total_comprado DESC, c.nombre COLLATE NOCASE
            LIMIT ?
            """,
            (limite,),
        )

    @staticmethod
    def obtener_productos_bajo_stock():
        """Lista productos cuyo stock actual alcanza o cae bajo el mínimo."""
        return ConsultasModel._consultar("""
            SELECT codigo, nombre, stock, stock_minimo
            FROM productos
            WHERE stock <= stock_minimo
            ORDER BY stock ASC, nombre COLLATE NOCASE
            """)

    @staticmethod
    def obtener_productos_urgentes_reponer(
        dias_analisis: int = 30, dias_cobertura: int = 14
    ):
        """Prioriza agotados, bajo mínimo y productos con poca cobertura por ventas."""
        try:
            periodo = int(dias_analisis)
            cobertura_maxima = int(dias_cobertura)
        except (TypeError, ValueError):
            raise ValidacionError(
                "Los períodos deben ser números enteros positivos."
            ) from None
        if (
            isinstance(dias_analisis, bool)
            or isinstance(dias_cobertura, bool)
            or periodo < 1
            or cobertura_maxima < 1
        ):
            raise ValidacionError("Los períodos deben ser números enteros positivos.")

        return ConsultasModel._consultar(
            """
            WITH ventas_periodo AS (
                SELECT d.producto_codigo, SUM(d.cantidad) AS unidades_vendidas
                FROM detalles_venta d
                JOIN ventas v ON v.id = d.venta_id
                                WHERE v.fecha_anulacion IS NULL
                                    AND DATE(v.fecha) BETWEEN DATE('now', ?) AND DATE('now')
                GROUP BY d.producto_codigo
            ), indicadores AS (
                SELECT p.codigo, p.nombre, p.stock, p.stock_minimo,
                       COALESCE(vp.unidades_vendidas, 0) AS unidades_vendidas,
                       ROUND(COALESCE(vp.unidades_vendidas, 0) * 1.0 / ?, 2)
                           AS promedio_diario,
                       CASE WHEN COALESCE(vp.unidades_vendidas, 0) > 0
                            THEN ROUND(p.stock * ? * 1.0 / vp.unidades_vendidas, 1)
                       END AS dias_cobertura
                FROM productos p
                LEFT JOIN ventas_periodo vp ON vp.producto_codigo = p.codigo
            )
            SELECT *,
                   CASE WHEN stock = 0 THEN 'AGOTADO'
                        WHEN stock <= stock_minimo THEN 'BAJO MÍNIMO'
                        ELSE 'ALTA ROTACIÓN' END AS prioridad
            FROM indicadores
            WHERE stock = 0
               OR stock <= stock_minimo
               OR (unidades_vendidas > 0 AND dias_cobertura <= ?)
            ORDER BY CASE WHEN stock = 0 THEN 0
                          WHEN stock <= stock_minimo THEN 1
                          ELSE 2 END,
                     dias_cobertura ASC, unidades_vendidas DESC,
                     nombre COLLATE NOCASE
            """,
            (f"-{periodo - 1} days", periodo, periodo, cobertura_maxima),
        )

    @staticmethod
    def obtener_productos_mas_vendidos(limit: int = 5):
        """Agrupa las cantidades vendidas por producto y retorna las más altas."""
        try:
            limite = int(limit)
        except (TypeError, ValueError):
            raise ValidacionError("El límite debe ser un entero positivo.") from None
        if isinstance(limit, bool) or limite < 1:
            raise ValidacionError("El límite debe ser un entero positivo.")
        return ConsultasModel._consultar(
            """
            SELECT p.codigo, p.nombre, SUM(d.cantidad) AS cantidad_vendida,
                   SUM(d.subtotal) AS total_generado
            FROM detalles_venta d
            JOIN productos p ON p.codigo = d.producto_codigo
            JOIN ventas v ON v.id = d.venta_id AND v.fecha_anulacion IS NULL
            GROUP BY p.codigo, p.nombre
            ORDER BY cantidad_vendida DESC, p.nombre COLLATE NOCASE
            LIMIT ?
            """,
            (limite,),
        )

    @staticmethod
    def obtener_productos_sin_movimiento(dias: int = 30):
        """Lista productos sin ventas dentro del número de días indicado."""
        try:
            periodo = int(dias)
        except (TypeError, ValueError):
            raise ValidacionError("Los días deben ser un entero no negativo.") from None
        if isinstance(dias, bool) or periodo < 0:
            raise ValidacionError("Los días deben ser un entero no negativo.")
        return ConsultasModel._consultar(
            """
            SELECT p.codigo, p.nombre, p.stock, MAX(v.fecha) AS ultima_venta
            FROM productos p
            LEFT JOIN detalles_venta d ON d.producto_codigo = p.codigo
            LEFT JOIN ventas v ON v.id = d.venta_id AND v.fecha_anulacion IS NULL
            GROUP BY p.codigo, p.nombre, p.stock
            HAVING MAX(v.fecha) IS NULL
                OR DATE(MAX(v.fecha)) < DATE('now', ?)
            ORDER BY ultima_venta ASC, p.nombre COLLATE NOCASE
            """,
            (f"-{periodo} days",),
        )

    @staticmethod
    def obtener_ventas_por_fechas(fecha_inicio: str, fecha_fin: str):
        """Lista las ventas emitidas entre dos fechas inclusivas."""
        inicio, fin = ConsultasModel._validar_rango_fechas(fecha_inicio, fecha_fin)
        return ConsultasModel._consultar(
            """
            SELECT v.id AS venta_id, v.fecha, v.cliente_documento,
                    c.nombre AS cliente_nombre, v.total,
                        CASE WHEN v.dias_credito > 0 THEN 'A Credito' ELSE 'Contado' END AS estado,
                    v.metodo_pago
            FROM ventas v
            JOIN clientes c ON c.documento = v.cliente_documento
                        WHERE DATE(v.fecha) BETWEEN ? AND ?
                            AND v.fecha_anulacion IS NULL
            ORDER BY v.fecha DESC, v.id DESC
            """,
            (inicio, fin),
        )

    @staticmethod
    def obtener_historial_notas(
        fecha_inicio: str = "",
        fecha_fin: str = "",
        cliente_documento: str = "",
    ):
        """Consulta todas las notas con filtros opcionales por fechas y cliente."""
        inicio = (fecha_inicio or "").strip()
        fin = (fecha_fin or "").strip()
        cliente = (cliente_documento or "").strip().upper()
        if bool(inicio) != bool(fin):
            raise ValidacionError(
                "Indica ambas fechas o deja el período vacío para consultar todas las notas."
            )

        condiciones = []
        parametros = []
        if inicio and fin:
            inicio, fin = ConsultasModel._validar_rango_fechas(inicio, fin)
            condiciones.append("DATE(v.fecha) BETWEEN ? AND ?")
            parametros.extend((inicio, fin))
        if cliente:
            condiciones.append("UPPER(v.cliente_documento) = ?")
            parametros.append(cliente)

        where = " AND ".join(condiciones) if condiciones else "1 = 1"
        return ConsultasModel._consultar(
            f"""
              SELECT v.id AS venta_id, v.fecha, v.cliente_documento,
                    c.nombre AS cliente_nombre, v.total,
                    CASE WHEN v.dias_credito > 0 THEN 'A Credito' ELSE 'Contado' END AS estado,
                    COALESCE(v.dias_credito, 0) AS dias_credito,
                    CASE WHEN v.dias_credito > 0 THEN v.fecha_vencimiento END AS fecha_vencimiento,
                    CASE WHEN v.fecha_vencimiento IS NOT NULL
                        THEN CAST(julianday(date(v.fecha_vencimiento)) - julianday(date('now')) AS INTEGER)
                    END AS dias_restantes,
                    CASE WHEN LOWER(TRIM(v.estado)) = 'pagado' THEN 'Pagada'
                         WHEN date(v.fecha_vencimiento) < date('now') THEN 'Vencida'
                         ELSE 'Vigente' END AS estado_vencimiento,
                    CASE WHEN v.fecha_anulacion IS NULL THEN 'Activa' ELSE 'Anulada' END AS registro,
                    COALESCE(v.motivo_anulacion, '') AS motivo_anulacion
            FROM ventas v
            JOIN clientes c ON c.documento = v.cliente_documento
            WHERE {where}
            ORDER BY
                CASE WHEN v.fecha_anulacion IS NOT NULL THEN 2
                     WHEN LOWER(TRIM(v.estado)) IN ('pendiente', 'a credito', 'a crédito')
                     THEN 0 ELSE 1 END,
                CASE
                    WHEN LOWER(TRIM(v.estado)) IN ('pendiente', 'a credito', 'a crédito')
                         AND date(v.fecha_vencimiento) < date('now') THEN 0
                    WHEN LOWER(TRIM(v.estado)) IN ('pendiente', 'a credito', 'a crédito')
                         AND date(v.fecha_vencimiento) = date('now') THEN 1
                    ELSE 2
                END,
                v.fecha DESC, v.id DESC
            """,
            parametros,
        )

    @staticmethod
    def obtener_resumen_metodos_pago(fecha_inicio: str, fecha_fin: str):
        """Suma ingresos por método, sin contar dos veces ventas a crédito y abonos."""
        inicio, fin = ConsultasModel._validar_rango_fechas(fecha_inicio, fecha_fin)
        return ConsultasModel._consultar(
            """
            SELECT metodo_pago, SUM(monto) AS total_ingresos
            FROM (
                SELECT COALESCE(NULLIF(TRIM(metodo_pago), ''), 'No especificado') AS metodo_pago,
                       total AS monto
                FROM ventas
                WHERE DATE(fecha) BETWEEN ? AND ?
                                    AND fecha_anulacion IS NULL
                  AND LOWER(TRIM(estado)) = 'pagado'
                UNION ALL
                SELECT COALESCE(NULLIF(TRIM(metodo_pago), ''), 'No especificado') AS metodo_pago,
                       monto
                FROM pagos_cuentas_por_cobrar
                WHERE DATE(fecha) BETWEEN ? AND ?
            ) ingresos
            GROUP BY metodo_pago
            ORDER BY total_ingresos DESC, metodo_pago
            """,
            (inicio, fin, inicio, fin),
        )

    @staticmethod
    def notas_pendientes_por_pagar():
        """Adaptador de compatibilidad para la vista de notas pendientes."""
        return [
            (
                nota["venta_id"],
                nota["fecha"],
                nota["cliente_documento"],
                nota["cliente_nombre"],
                ConsultasModel.formatear_moneda(nota["total"]),
                nota["estado"],
                ConsultasModel.formatear_moneda(nota["saldo_pendiente"]),
                nota["dias_credito"],
                nota["fecha_vencimiento"],
                nota["dias_restantes"],
                nota["estado_vencimiento"],
            )
            for nota in ConsultasModel.obtener_notas_pendientes()
        ]

    @staticmethod
    def notas_por_cliente(cliente_documento: str):
        """Adaptador de compatibilidad para la vista de notas por cliente."""
        return [
            (
                venta["venta_id"],
                venta["fecha"],
                venta["cliente_documento"],
                venta["cliente_nombre"],
                venta["total"],
                venta["estado"],
            )
            for venta in ConsultasModel.obtener_ventas_por_cliente(cliente_documento)
        ]

    @staticmethod
    def ventas_por_rango(
        fecha_inicio: str, fecha_fin: str, cliente_documento: str = ""
    ):
        """Devuelve ventas por rango de fechas, opcionalmente filtradas por cliente."""
        inicio = (fecha_inicio or "").strip()
        fin = (fecha_fin or "").strip()
        cliente = (cliente_documento or "").strip().upper()
        if not inicio or not fin:
            raise ValidacionError("Debes indicar fecha de inicio y fecha final.")

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            if cliente:
                cursor.execute(
                    """
                    SELECT v.id, v.fecha, v.cliente_documento, c.nombre, v.total
                    FROM ventas v
                    JOIN clientes c ON c.documento = v.cliente_documento
                    WHERE DATE(v.fecha) BETWEEN ? AND ?
                                            AND v.fecha_anulacion IS NULL
                      AND UPPER(v.cliente_documento) = ?
                    ORDER BY v.fecha DESC
                    """,
                    (inicio, fin, cliente),
                )
            else:
                cursor.execute(
                    """
                    SELECT v.id, v.fecha, v.cliente_documento, c.nombre, v.total
                    FROM ventas v
                    JOIN clientes c ON c.documento = v.cliente_documento
                    WHERE DATE(v.fecha) BETWEEN ? AND ?
                                            AND v.fecha_anulacion IS NULL
                    ORDER BY v.fecha DESC
                    """,
                    (inicio, fin),
                )
            return cursor.fetchall()

    @staticmethod
    def historial_ventas_cliente(
        cliente_documento: str, fecha_inicio: str = "", fecha_fin: str = ""
    ):
        """Devuelve el historial de una nota por cliente, con filtro opcional por fecha."""
        cliente = (cliente_documento or "").strip().upper()
        if not cliente:
            raise ValidacionError(
                "Debes indicar un cliente para consultar su historial."
            )

        params = [cliente]
        query = """
            SELECT v.id, v.fecha, v.cliente_documento, c.nombre, v.total
            FROM ventas v
            JOIN clientes c ON c.documento = v.cliente_documento
            WHERE UPPER(v.cliente_documento) = ?
        """
        if fecha_inicio and fecha_fin:
            query += " AND DATE(v.fecha) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        query += " ORDER BY v.fecha DESC"

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def productos_bajo_stock(stock_maximo: int = 5):
        """Lista productos con stock menor o igual al valor indicado."""
        try:
            limite = int(stock_maximo)
        except (TypeError, ValueError):
            raise ValidacionError(
                "El stock máximo debe ser un número entero."
            ) from None

        if limite < 0:
            raise ValidacionError("El stock máximo no puede ser negativo.")

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT codigo, nombre, precio, stock
                FROM productos
                WHERE stock <= ?
                ORDER BY stock ASC
                """,
                (limite,),
            )
            return cursor.fetchall()

    @staticmethod
    def valor_total_inventario():
        """Calcula el valor total del inventario en pesos según el stock actual."""
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM((precio_centavos / 100.0) * stock), 0)
                FROM productos
                """)
            valor = cursor.fetchone()[0]
            return ConsultasModel.formatear_moneda(valor)

    @staticmethod
    def total_productos_distintos():
        """Devuelve la cantidad de productos distintos registrados en inventario."""
        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos")
            return int(cursor.fetchone()[0] or 0)

    @staticmethod
    def total_facturado(fecha_inicio: str, fecha_fin: str):
        """Suma total de ventas emitidas en un rango de fechas."""
        inicio = (fecha_inicio or "").strip()
        fin = (fecha_fin or "").strip()
        if not inicio or not fin:
            raise ValidacionError("Debes indicar fecha de inicio y fecha final.")

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(total), 0)
                FROM ventas
                                WHERE DATE(fecha) BETWEEN ? AND ?
                                    AND fecha_anulacion IS NULL
                """,
                (inicio, fin),
            )
            total = cursor.fetchone()[0]
            return ConsultasModel.formatear_moneda(total)

    @staticmethod
    def productos_mas_vendidos(limit: int = 5):
        """Devuelve los productos con mejor rendimiento por cantidad vendida."""
        try:
            top = max(1, int(limit))
        except (TypeError, ValueError):
            raise ValidacionError(
                "El límite debe ser un número entero válido."
            ) from None

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.codigo, p.nombre, SUM(d.cantidad) as total_vendido, SUM(d.subtotal) as total_generado
                FROM detalles_venta d
                JOIN productos p ON p.codigo = d.producto_codigo
                JOIN ventas v ON v.id = d.venta_id AND v.fecha_anulacion IS NULL
                GROUP BY p.codigo, p.nombre
                ORDER BY total_vendido DESC
                LIMIT ?
                """,
                (top,),
            )
            return cursor.fetchall()

    @staticmethod
    def top_clientes_mayor_compra(limit: int = 5):
        """Muestra los clientes con mayores compras acumuladas."""
        try:
            top = max(1, int(limit))
        except (TypeError, ValueError):
            raise ValidacionError(
                "El límite debe ser un número entero válido."
            ) from None

        with closing(obtener_conexion()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.cliente_documento, c.nombre, SUM(v.total) as total_comprado
                FROM ventas v
                JOIN clientes c ON c.documento = v.cliente_documento
                WHERE v.fecha_anulacion IS NULL
                GROUP BY v.cliente_documento, c.nombre
                ORDER BY total_comprado DESC
                LIMIT ?
                """,
                (top,),
            )
            return cursor.fetchall()

    @staticmethod
    def exportar_csv(nombre_archivo: str, columnas: list, filas: list) -> str:
        """Exporta una lista de filas a un archivo CSV."""
        if not nombre_archivo:
            raise ValidacionError("Debes indicar un nombre de archivo para exportar.")

        try:
            with open(nombre_archivo, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(columnas)
                for fila in filas:
                    escritor.writerow(fila)
        except OSError as error:
            raise RuntimeError(
                f"No se pudo exportar el archivo CSV: {error}"
            ) from error
        return nombre_archivo
