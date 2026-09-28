import argparse
import os
import sys
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.conexion import inicializar_base_de_datos, transaccion


def sembrar_datos():
    print("Iniciando la siembra de datos de prueba...")

    inicializar_base_de_datos()
    with transaccion() as conn:
        cursor = conn.cursor()

        clientes_prueba = [
            ("V-12345678", "Juan Pérez", "0414-1234567", "Av. Principal Nro 12"),
            ("V-87654321", "María Delgado", "0424-7654321", "Calle 5 de Mayo #45"),
            (
                "J-301234560",
                "Constructora Los Andes C.A.",
                "0276-3334455",
                "Zona Industrial San José",
            ),
            ("V-19555666", "Carlos Rodríguez", "0412-5556677", "Barrio Sucre Sector B"),
            (
                "J-409876541",
                "Ferretería La Solución S.R.L.",
                "0276-9998877",
                "Centro Comercial Plaza",
            ),
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO clientes (documento, nombre, telefono, direccion)
            VALUES (?, ?, ?, ?)
            """,
            clientes_prueba,
        )
        print("Clientes procesados correctamente.")

        productos_prueba = [
            ("PROD-001", "Martillo de Uña 16oz Stanley", 12.50, 25),
            ("PROD-002", "Juego de Alicates 3 pzas Truper", 18.00, 15),
            ("PROD-003", "Destornillador de Estría 1/4x4", 3.50, 50),
            ("PROD-004", "Tubo PVC 1/2 pulgada Pavco 6m", 8.20, 100),
            ("PROD-005", "Saco de Cemento Portland 42.5kg", 9.50, 80),
            ("PROD-006", "Taladro Percutor 1/2 Dewalt 800W", 85.00, 8),
            ("PROD-007", "Disco de Corte para Metal 4-1/2", 1.80, 200),
            ("PROD-008", "Llave Ajustable 10 pulgadas Pretul", 7.00, 30),
        ]

        productos_con_centavos = [
            (codigo, nombre, precio, round(precio * 100), stock)
            for codigo, nombre, precio, stock in productos_prueba
        ]
        cursor.executemany(
            """
            INSERT OR IGNORE INTO productos
                (codigo, nombre, precio, precio_centavos, stock)
            VALUES (?, ?, ?, ?, ?)
            """,
            productos_con_centavos,
        )
        print("Productos procesados correctamente.")

    print("\n¡Siembra completada con éxito! Puedes ejecutar main.py.")


def sembrar_notas_demo():
    """Crea una sola tanda de 20 notas y actualiza el stock de forma transaccional."""
    inicializar_base_de_datos()
    edades_dias = (0, 5, 10, 20, 35, 45, 50, 15, 25, 40)

    with transaccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_seed_runs (
                lote TEXT PRIMARY KEY,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        lote = "consultas_notas_20_v1"
        if cursor.execute(
            "SELECT 1 FROM demo_seed_runs WHERE lote = ?", (lote,)
        ).fetchone():
            print("Las 20 notas demostrativas ya fueron creadas; no se duplicaron.")
            return

        clientes = cursor.execute(
            "SELECT documento FROM clientes ORDER BY documento"
        ).fetchall()
        productos = cursor.execute("""
            SELECT codigo, nombre, precio, precio_centavos, stock
            FROM productos
            WHERE stock > 0
            ORDER BY stock DESC, codigo
            """).fetchall()
        if not clientes:
            raise RuntimeError("Se necesita al menos un cliente para crear las notas.")
        if sum(producto[4] for producto in productos) < 20:
            raise RuntimeError(
                "Se necesitan al menos 20 unidades disponibles para crear las notas."
            )

        stock_disponible = {producto[0]: producto[4] for producto in productos}
        productos_por_codigo = {producto[0]: producto for producto in productos}
        for numero_nota in range(20):
            codigo_producto = max(stock_disponible, key=stock_disponible.get)
            producto = productos_por_codigo[codigo_producto]
            stock_disponible[codigo_producto] -= 1

            precio_centavos = producto[3]
            if precio_centavos is None:
                precio_centavos = round(float(producto[2]) * 100)
            precio = precio_centavos / 100
            es_credito = numero_nota % 2 == 0
            antiguedad = edades_dias[(numero_nota // 2) % len(edades_dias)]
            fecha_venta = date.today() - timedelta(days=antiguedad)
            estado = "A Credito" if es_credito else "Pagado"
            dias_credito = 30 if es_credito else 0
            fecha_vencimiento = (
                (fecha_venta + timedelta(days=dias_credito)).isoformat()
                if es_credito
                else None
            )

            cursor.execute(
                """
                INSERT INTO ventas (
                    fecha, cliente_documento, total, total_centavos, estado,
                    metodo_pago, dias_credito, fecha_vencimiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{fecha_venta.isoformat()} 12:00:00",
                    clientes[numero_nota % len(clientes)][0],
                    precio,
                    precio_centavos,
                    estado,
                    "No especificado" if es_credito else "Efectivo",
                    dias_credito,
                    fecha_vencimiento,
                ),
            )
            venta_id = cursor.lastrowid
            cursor.execute(
                """
                INSERT INTO detalles_venta (
                    venta_id, producto_codigo, cantidad, precio_unitario,
                    subtotal, precio_unitario_centavos, subtotal_centavos
                ) VALUES (?, ?, 1, ?, ?, ?, ?)
                """,
                (
                    venta_id,
                    codigo_producto,
                    precio,
                    precio,
                    precio_centavos,
                    precio_centavos,
                ),
            )
            cursor.execute(
                "UPDATE productos SET stock = stock - 1 WHERE codigo = ? AND stock > 0",
                (codigo_producto,),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    f"No se pudo descontar el stock de {codigo_producto}."
                )

        cursor.execute("INSERT INTO demo_seed_runs(lote) VALUES (?)", (lote,))

    print("Se crearon 20 notas: 10 pagadas y 10 a crédito, sin abonos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carga de datos de Ferretería Cerpint")
    parser.add_argument(
        "--notas-demo",
        action="store_true",
        help="Crea una tanda idempotente de 20 notas demostrativas.",
    )
    argumentos = parser.parse_args()
    if argumentos.notas_demo:
        sembrar_notas_demo()
    else:
        sembrar_datos()
