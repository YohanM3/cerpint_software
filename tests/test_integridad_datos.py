import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from database import conexion
from database.errores import InventarioInsuficienteError
from modulos.clientes.clientes_model import ClientesModel
from modulos.consultas.consultas_model import ConsultasModel
from modulos.inventario.inventario_model import InventarioModel
from modulos.ventas.ventas_controller import VentasController
from modulos.ventas.ventas_model import VentasModel
from sembrar_datos import sembrar_notas_demo


class IntegridadDatosTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "ferreteria.db"
        self.database_patch = patch.object(conexion, "DB_NAME", self.database_path)
        self.database_patch.start()
        self.addCleanup(self.database_patch.stop)
        conexion.inicializar_base_de_datos()
        self.clientes = ClientesModel()
        self.inventario = InventarioModel()

    def test_codigo_alias_se_guarda_y_busca_normalizado(self):
        self.assertTrue(self.inventario.agregar_producto("P004", "Tubo PVC", 2.50, 8))
        self.assertEqual(self.inventario.obtener_por_codigo("P004")[0], "PROD-004")
        self.assertEqual(self.inventario.buscar_sugerencias("P004")[0][0], "PROD-004")
        self.assertFalse(
            self.inventario.agregar_producto("PROD-004", "Duplicado", 1, 1)
        )

    def test_modelos_rechazan_campos_vacios_y_valores_negativos(self):
        with self.assertRaises(ValueError):
            self.clientes.agregar_cliente("   ", "Nombre")
        with self.assertRaises(ValueError):
            self.inventario.agregar_producto("P005", "   ", 1, 1)
        with self.assertRaises(ValueError):
            self.inventario.agregar_producto("P005", "Producto", -1, 1)
        with self.assertRaises(ValueError):
            self.inventario.agregar_producto("P005", "Producto", 1, -1)

    def test_venta_descuenta_stock_y_falta_de_stock_revierte_todo(self):
        self.clientes.agregar_cliente("CLI-1", "Cliente Uno")
        self.inventario.agregar_producto("P010", "Producto Diez", 3.25, 2)
        venta = VentasModel()
        venta.agregar_item("PROD-010", "Producto Diez", 3, 3.25)

        with self.assertRaises(InventarioInsuficienteError):
            venta.procesar_venta_bd("CLI-1")

        with conexion.transaccion() as conn:
            stock = conn.execute(
                "SELECT stock FROM productos WHERE codigo = 'PROD-010'"
            ).fetchone()[0]
            ventas = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
            detalles = conn.execute("SELECT COUNT(*) FROM detalles_venta").fetchone()[0]
        self.assertEqual((stock, ventas, detalles), (2, 0, 0))
        self.assertEqual(len(venta.carrito), 1)

        venta.vaciar_carrito()
        venta.agregar_item("PROD-010", "Producto Diez", 2, 3.25)
        _, cliente_data, _, _ = venta.procesar_venta_bd("CLI-1")
        self.assertRegex(
            cliente_data["fecha_emision"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        )
        with conexion.transaccion() as conn:
            stock = conn.execute(
                "SELECT stock FROM productos WHERE codigo = 'PROD-010'"
            ).fetchone()[0]
            precio_centavos = conn.execute(
                "SELECT precio_centavos FROM productos WHERE codigo = 'PROD-010'"
            ).fetchone()[0]
        self.assertEqual(stock, 0)
        self.assertEqual(precio_centavos, 325)
        self.assertEqual(venta.carrito, [])
        with conexion.transaccion() as conn:
            self.assertEqual(
                conn.execute("SELECT total_centavos FROM ventas").fetchone()[0], 650
            )
            self.assertEqual(
                conn.execute(
                    "SELECT precio_unitario_centavos, subtotal_centavos FROM detalles_venta"
                ).fetchone(),
                (325, 650),
            )

        self.inventario.agregar_producto("P011", "Producto Once", 3.25, 5)
        venta = VentasModel()
        venta.agregar_item("PROD-011", "Producto Once", 1, 3.25)
        _, datos_credito, items_procesados, _ = venta.procesar_venta_bd(
            "CLI-1", estado="A Credito", dias_credito=12
        )
        self.assertEqual(items_procesados[0]["nombre"], "Producto Once")
        self.assertNotIn("producto", items_procesados[0])
        self.assertEqual(datos_credito["dias_credito"], 12)
        self.assertTrue(datos_credito["fecha_vencimiento"])
        self.assertEqual(
            VentasModel.obtener_ventas_por_cliente("CLI-1")[0]["estado_pago"],
            "A Credito",
        )
        self.assertEqual(
            VentasModel.obtener_detalle_venta(2)["estado_pago"], "A Credito"
        )

    def test_venta_contado_no_guarda_plazo_ni_vencimiento(self):
        self.clientes.agregar_cliente("CLI-CONTADO", "Cliente Contado")
        self.inventario.agregar_producto("P-CONTADO", "Producto Contado", 2, 1)
        venta = VentasModel()
        venta.agregar_item("P-CONTADO", "Producto Contado", 1, 2)

        venta_id = venta.procesar_venta_bd("CLI-CONTADO", estado="Contado")[0]

        with conexion.transaccion() as conn:
            estado, dias_credito, fecha_vencimiento = conn.execute(
                "SELECT estado, dias_credito, fecha_vencimiento FROM ventas WHERE id = ?",
                (venta_id,),
            ).fetchone()
        self.assertEqual(estado, "Pagado")
        self.assertEqual(dias_credito, 0)
        self.assertIsNone(fecha_vencimiento)

    def test_procesar_venta_emite_pdf_desde_el_controlador(self):
        venta = VentasModel()
        venta.agregar_item("PROD-010", "Producto Diez", 2, 3.25)
        vista = MagicMock()
        vista.txt_cliente_buscar = MagicMock()
        vista.txt_codigo = MagicMock()
        vista.btn_agregar = MagicMock()
        vista.btn_cancelar = MagicMock()
        vista.btn_procesar = MagicMock()
        vista.menu_estado_pago = MagicMock()
        vista.menu_estado_pago.get.return_value = "Pendiente"
        vista.txt_dias_credito = MagicMock()
        vista.txt_dias_credito.obtener_texto.return_value = "18"
        vista.tabla_ventas = MagicMock()
        vista.lbl_total = MagicMock()
        vista.winfo_toplevel.return_value = MagicMock()
        controller = VentasController(
            venta,
            vista,
            clientes_model=MagicMock(),
            inventario_model=MagicMock(),
        )
        controller.cliente_actual = "CLI-1"
        venta_id = 15
        cliente_data = {"documento": "CLI-1", "nombre": "Cliente Uno"}
        items_proc = [
            {
                "codigo": "PROD-010",
                "nombre": "Producto Diez",
                "cantidad": 2,
                "precio": 3.25,
                "subtotal": 6.5,
            }
        ]
        total_proc = 6.5

        with patch.object(
            venta,
            "procesar_venta_bd",
            return_value=(venta_id, cliente_data, items_proc, total_proc),
        ) as procesar_bd, patch.object(
            VentasController,
            "procesar_y_generar_pdf",
            return_value=True,
        ) as generar_pdf:
            self.assertTrue(controller.procesar_venta())

        procesar_bd.assert_called_once_with(
            "CLI-1", estado="Pendiente", dias_credito="18"
        )
        generar_pdf.assert_called_once_with(
            "CLI-1",
            items_proc,
            total_proc,
            parent_widget=vista.winfo_toplevel.return_value,
            venta_id=venta_id,
            cliente_data=cliente_data,
        )

    def test_consultas_model_devuelve_notas_pendientes_y_por_cliente(self):
        self.clientes.agregar_cliente("CLI-2", "Cliente Dos")
        self.clientes.agregar_cliente("CLI-3", "Cliente Tres")
        self.inventario.agregar_producto("P020", "Producto Veinte", 12.5, 2)
        self.inventario.agregar_producto("P021", "Producto Veintiuno", 30, 1)

        venta = VentasModel()
        venta.agregar_item("PROD-020", "Producto Veinte", 2, 12.5)
        venta.procesar_venta_bd("CLI-2", estado="Pendiente")

        venta_2 = VentasModel()
        venta_2.agregar_item("PROD-021", "Producto Veintiuno", 1, 30)
        venta_2.procesar_venta_bd("CLI-3", estado="A Credito", dias_credito=10)

        with conexion.transaccion() as conn:
            conn.execute(
                "UPDATE ventas SET metodo_pago = 'Transferencia' WHERE cliente_documento = ?",
                ("CLI-2",),
            )
            conn.execute(
                "INSERT INTO pagos_cuentas_por_cobrar (venta_id, monto, metodo_pago) "
                "SELECT id, 5, 'Transferencia' FROM ventas WHERE cliente_documento = ?",
                ("CLI-2",),
            )
            conn.execute(
                "UPDATE ventas SET metodo_pago = 'Efectivo' WHERE cliente_documento = ?",
                ("CLI-3",),
            )
            conn.execute(
                "UPDATE ventas SET fecha_vencimiento = DATE('now', '-3 days') "
                "WHERE cliente_documento = ?",
                ("CLI-3",),
            )
            conn.execute("UPDATE productos SET stock_minimo = 1")
        self.inventario.agregar_producto("P022", "Producto Sin Ventas", 8, 3)

        consultor = ConsultasModel()
        pendientes = consultor.obtener_notas_pendientes()
        pagos = consultor.obtener_historial_pagos_cliente("CLI-2")
        notas_cliente = consultor.obtener_ventas_por_cliente("CLI-2")
        top_clientes = consultor.obtener_top_clientes(5)
        stock_bajo = consultor.obtener_productos_bajo_stock()
        top_productos = consultor.obtener_productos_mas_vendidos(5)
        sin_movimiento = consultor.obtener_productos_sin_movimiento(30)
        ventas_rango = consultor.obtener_ventas_por_fechas("2020-01-01", "2099-12-31")
        metodos_pago = consultor.obtener_resumen_metodos_pago(
            "2020-01-01", "2099-12-31"
        )

        self.assertEqual(len(pendientes), 2)
        self.assertEqual(
            {nota["cliente_documento"] for nota in pendientes}, {"CLI-2", "CLI-3"}
        )
        nota_cli2 = next(
            nota for nota in pendientes if nota["cliente_documento"] == "CLI-2"
        )
        nota_cli3 = next(
            nota for nota in pendientes if nota["cliente_documento"] == "CLI-3"
        )
        self.assertEqual(nota_cli2["total_abonado"], 5)
        self.assertEqual(nota_cli2["saldo_pendiente"], 20)
        self.assertEqual(nota_cli2["dias_credito"], 30)
        self.assertEqual(nota_cli3["dias_credito"], 10)
        self.assertEqual(nota_cli3["dias_restantes"], -3)
        self.assertEqual(nota_cli3["estado_vencimiento"], "Vencida")
        self.assertEqual(pagos[0]["monto"], 5)
        self.assertEqual(len(notas_cliente), 1)
        self.assertEqual(notas_cliente[0]["cliente_nombre"], "Cliente Dos")
        self.assertEqual(top_clientes[0]["total_comprado"], 30)
        self.assertTrue(
            any(
                producto["stock"] <= producto["stock_minimo"] for producto in stock_bajo
            )
        )
        self.assertEqual(top_productos[0]["cantidad_vendida"], 2)
        self.assertTrue(
            any(producto["codigo"] == "PROD-022" for producto in sin_movimiento)
        )
        self.assertEqual(len(ventas_rango), 2)
        self.assertEqual(
            {fila["metodo_pago"] for fila in metodos_pago},
            {"Transferencia"},
        )

    def test_historial_notas_admite_periodo_vacio_y_prioriza_pendientes(self):
        self.clientes.agregar_cliente("CLI-HIST-1", "Cliente Historial Uno")
        self.clientes.agregar_cliente("CLI-HIST-2", "Cliente Historial Dos")
        self.inventario.agregar_producto("P-HIST-1", "Producto Historial Uno", 5, 2)
        self.inventario.agregar_producto("P-HIST-2", "Producto Historial Dos", 7, 2)

        venta_pendiente = VentasModel()
        venta_pendiente.agregar_item("P-HIST-1", "Producto Historial Uno", 1, 5)
        id_pendiente = venta_pendiente.procesar_venta_bd(
            "CLI-HIST-1", estado="A Credito"
        )[0]

        venta_pagada = VentasModel()
        venta_pagada.agregar_item("P-HIST-2", "Producto Historial Dos", 1, 7)
        venta_pagada.procesar_venta_bd("CLI-HIST-2", estado="Contado")

        with conexion.transaccion() as conn:
            conn.execute(
                "UPDATE ventas SET fecha = DATE('now', '-2 days'), "
                "fecha_vencimiento = DATE('now', '-1 day') WHERE id = ?",
                (id_pendiente,),
            )

        consultor = ConsultasModel()
        todas = consultor.obtener_historial_notas()
        periodo = consultor.obtener_historial_notas("2020-01-01", "2099-12-31")
        cliente = consultor.obtener_historial_notas(cliente_documento="CLI-HIST-2")

        self.assertEqual(len(todas), 2)
        self.assertEqual(todas[0]["venta_id"], id_pendiente)
        self.assertEqual(todas[0]["estado"], "A Credito")
        self.assertEqual(todas[0]["estado_vencimiento"], "Vencida")
        self.assertEqual(
            [nota["venta_id"] for nota in periodo], [nota["venta_id"] for nota in todas]
        )
        self.assertEqual(len(cliente), 1)
        self.assertEqual(cliente[0]["estado"], "Contado")
        self.assertEqual(cliente[0]["dias_credito"], 0)
        self.assertIsNone(cliente[0]["fecha_vencimiento"])
        with self.assertRaises(ValueError):
            consultor.obtener_historial_notas("2026-01-01", "")

    def test_sembrar_20_notas_es_transaccional_y_no_duplica(self):
        self.clientes.agregar_cliente("CLI-DEMO", "Cliente Demo")
        self.inventario.agregar_producto("P-DEMO", "Producto Demo", 4.5, 30)

        sembrar_notas_demo()
        sembrar_notas_demo()

        with conexion.transaccion() as conn:
            cantidad, pagadas, credito = conn.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN estado = 'A Credito' THEN 1 ELSE 0 END)
                FROM ventas
                """).fetchone()
            stock = conn.execute(
                "SELECT stock FROM productos WHERE codigo = 'P-DEMO'"
            ).fetchone()[0]

        self.assertEqual((cantidad, pagadas, credito), (20, 10, 10))
        self.assertEqual(stock, 10)

    def test_reposicion_prioriza_agotados_minimo_y_ventas_rapidas(self):
        self.clientes.agregar_cliente("CLI-STOCK", "Cliente Stock")
        self.inventario.agregar_producto("P-FAST", "Producto Alta Rotación", 5, 100)
        self.inventario.agregar_producto("P-LOW", "Producto Bajo Mínimo", 3, 10)
        self.inventario.agregar_producto("P-OUT", "Producto Agotado", 2, 1)

        venta = VentasModel()
        venta.agregar_item("P-FAST", "Producto Alta Rotación", 80, 5)
        venta.procesar_venta_bd("CLI-STOCK", estado="Contado")
        venta = VentasModel()
        venta.agregar_item("P-OUT", "Producto Agotado", 1, 2)
        venta.procesar_venta_bd("CLI-STOCK", estado="Contado")

        with conexion.transaccion() as conn:
            conn.execute(
                "UPDATE productos SET stock_minimo = 12 WHERE codigo = 'P-LOW'"
            )

        urgentes = ConsultasModel.obtener_productos_urgentes_reponer()
        self.assertEqual(
            [producto["codigo"] for producto in urgentes],
            ["P-OUT", "P-LOW", "P-FAST"],
        )
        producto_rapido = urgentes[2]
        self.assertEqual(producto_rapido["stock"], 20)
        self.assertEqual(producto_rapido["unidades_vendidas"], 80)
        self.assertEqual(producto_rapido["dias_cobertura"], 7.5)
        self.assertEqual(producto_rapido["prioridad"], "ALTA ROTACIÓN")

    def test_nota_pagada_puede_reclasificarse_individualmente_como_pendiente(self):
        self.clientes.agregar_cliente("CLI-4", "Cliente Cuatro")
        self.inventario.agregar_producto("P040", "Producto Cuarenta", 15, 1)
        venta = VentasModel()
        venta.agregar_item("PROD-040", "Producto Cuarenta", 1, 15)
        venta_id = venta.procesar_venta_bd("CLI-4")[0]

        consultor = ConsultasModel()
        self.assertEqual(consultor.obtener_notas_pendientes(), [])
        self.assertTrue(consultor.marcar_venta_como_pendiente(venta_id))
        self.assertFalse(consultor.marcar_venta_como_pendiente(venta_id))
        pendientes = consultor.obtener_notas_pendientes()

        self.assertEqual(pendientes[0]["venta_id"], venta_id)
        with conexion.transaccion() as conn:
            estado_interno = conn.execute(
                "SELECT estado FROM ventas WHERE id = ?", (venta_id,)
            ).fetchone()[0]
        self.assertEqual(estado_interno, "A Credito")
        self.assertEqual(pendientes[0]["saldo_pendiente"], 15)
        self.assertEqual(pendientes[0]["dias_credito"], 30)
        self.assertEqual(pendientes[0]["estado_vencimiento"], "Vigente")

    def test_alternar_pago_recalcula_situacion_sin_perder_vencimiento(self):
        self.clientes.agregar_cliente("CLI-PAGO", "Cliente Pago")
        self.inventario.agregar_producto("P-PAGO", "Producto Pago", 10, 2)
        venta_credito = VentasModel()
        venta_credito.agregar_item("P-PAGO", "Producto Pago", 1, 10)
        id_credito = venta_credito.procesar_venta_bd(
            "CLI-PAGO", estado="A Credito", dias_credito=30
        )[0]
        with conexion.transaccion() as conn:
            conn.execute(
                "UPDATE ventas SET fecha_vencimiento = DATE('now', '+5 days') "
                "WHERE id = ?",
                (id_credito,),
            )
            vencimiento_original = conn.execute(
                "SELECT fecha_vencimiento FROM ventas WHERE id = ?", (id_credito,)
            ).fetchone()[0]

        consultor = ConsultasModel()
        self.assertEqual(consultor.alternar_pago_nota(id_credito), "Pagado")
        nota_pagada = next(
            nota
            for nota in consultor.obtener_historial_notas()
            if nota["venta_id"] == id_credito
        )
        self.assertEqual(nota_pagada["estado_vencimiento"], "Pagada")

        self.assertEqual(consultor.alternar_pago_nota(id_credito), "A Credito")
        nota_reabierta = next(
            nota
            for nota in consultor.obtener_historial_notas()
            if nota["venta_id"] == id_credito
        )
        self.assertEqual(nota_reabierta["estado_vencimiento"], "Vigente")
        self.assertEqual(nota_reabierta["fecha_vencimiento"], vencimiento_original)

        venta_contado = VentasModel()
        venta_contado.agregar_item("P-PAGO", "Producto Pago", 1, 10)
        id_contado = venta_contado.procesar_venta_bd("CLI-PAGO", estado="Contado")[0]
        consultor.alternar_pago_nota(id_contado)
        nota_contado = next(
            nota
            for nota in consultor.obtener_historial_notas()
            if nota["venta_id"] == id_contado
        )
        self.assertEqual(nota_contado["estado_vencimiento"], "Vencida")

    def test_anular_nota_repone_stock_una_vez_y_la_excluye_de_deuda(self):
        self.clientes.agregar_cliente("CLI-ANUL", "Cliente Anulación")
        self.inventario.agregar_producto("P-ANUL", "Producto Anulado", 8, 5)
        venta = VentasModel()
        venta.agregar_item("P-ANUL", "Producto Anulado", 2, 8)
        venta_id = venta.procesar_venta_bd("CLI-ANUL", estado="A Credito")[0]

        consultor = ConsultasModel()
        self.assertTrue(consultor.anular_venta(venta_id, "Devolución completa"))
        self.assertFalse(consultor.anular_venta(venta_id, "Repetición"))

        with conexion.transaccion() as conn:
            stock = conn.execute(
                "SELECT stock FROM productos WHERE codigo = 'P-ANUL'"
            ).fetchone()[0]
        nota = next(
            fila
            for fila in consultor.obtener_historial_notas()
            if fila["venta_id"] == venta_id
        )
        self.assertEqual(stock, 5)
        self.assertEqual(nota["registro"], "Anulada")
        self.assertEqual(nota["motivo_anulacion"], "Devolución completa")
        self.assertNotIn(
            venta_id, {fila["venta_id"] for fila in consultor.obtener_notas_pendientes()}
        )
        self.assertEqual(consultor.obtener_productos_mas_vendidos(), [])

    def test_foreign_keys_protegen_historial(self):
        self.clientes.agregar_cliente("CLI-2", "Cliente Dos")
        self.inventario.agregar_producto("P020", "Producto Veinte", 1, 2)
        venta = VentasModel()
        venta.agregar_item("PROD-020", "Producto Veinte", 1, 1)
        venta.procesar_venta_bd("CLI-2")

        with self.assertRaises(sqlite3.IntegrityError):
            self.clientes.eliminar_cliente("CLI-2")
        with self.assertRaises(sqlite3.IntegrityError):
            self.inventario.eliminar_producto("PROD-020")

    def test_triggers_se_instalan_en_esquema_existente_sin_borrar_filas(self):
        legacy_path = Path(self.temp_dir.name) / "legacy.db"
        with patch.object(conexion, "DB_NAME", legacy_path):
            conn = sqlite3.connect(legacy_path)
            conn.execute("""CREATE TABLE productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL
                )""")
            conn.execute("""CREATE TABLE clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    documento TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    direccion TEXT
                )""")
            conn.execute(
                "INSERT INTO clientes(documento, nombre) VALUES('CLI-OLD', 'Cliente Antiguo')"
            )
            conn.execute("""CREATE TABLE ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cliente_documento TEXT NOT NULL,
                    total REAL NOT NULL,
                    total_centavos INTEGER,
                    estado TEXT NOT NULL DEFAULT 'Pendiente',
                    metodo_pago TEXT NOT NULL DEFAULT 'No especificado'
                )""")
            conn.execute(
                "INSERT INTO ventas(fecha, cliente_documento, total, total_centavos, estado) "
                "VALUES (datetime('now', '-40 days'), 'CLI-OLD', 5, 500, 'Pendiente')"
            )
            conn.execute(
                "INSERT INTO ventas(fecha, cliente_documento, total, total_centavos, estado) "
                "VALUES (CURRENT_TIMESTAMP, 'CLI-OLD', 7, 700, 'Pagado')"
            )
            conn.execute(
                "INSERT INTO productos(codigo,nombre,precio,stock) VALUES('OLD-1','Viejo',1,4)"
            )
            conn.commit()
            conn.close()

            conexion.inicializar_base_de_datos()
            with self.assertRaises(sqlite3.IntegrityError):
                with conexion.transaccion() as migrated:
                    migrated.execute(
                        "INSERT INTO productos(codigo,nombre,precio,stock) VALUES('BAD','Inválido',1,-1)"
                    )
            with conexion.transaccion() as migrated:
                remaining = migrated.execute(
                    "SELECT codigo, precio_centavos FROM productos"
                ).fetchall()
                old_credit = migrated.execute(
                    "SELECT dias_credito, fecha_vencimiento FROM ventas WHERE id = 1"
                ).fetchone()
                old_paid = migrated.execute(
                    "SELECT dias_credito, fecha_vencimiento FROM ventas WHERE id = 2"
                ).fetchone()
                old_credit_state = migrated.execute(
                    "SELECT estado FROM ventas WHERE id = 1"
                ).fetchone()[0]
                expected_due_date = migrated.execute(
                    "SELECT DATE('now', '-10 days')"
                ).fetchone()[0]
            self.assertEqual(remaining, [("OLD-1", 100)])
            self.assertEqual(old_credit, (30, expected_due_date))
            self.assertEqual(old_paid, (0, None))
            self.assertEqual(old_credit_state, "A Credito")
            with patch.object(conexion, "DB_NAME", legacy_path):
                old_pending = ConsultasModel.obtener_notas_pendientes()
            self.assertEqual(old_pending[0]["estado_vencimiento"], "Vencida")


if __name__ == "__main__":
    unittest.main()
