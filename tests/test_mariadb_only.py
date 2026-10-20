from unittest.mock import Mock

from database.conexion import TAMANO_POOL, CursorMySQL
from modulos.inventario.inventario_model import InventarioModel


def test_el_cursor_envia_el_sql_con_marcadores_de_mariadb_sin_cambios():
    cursor_real = Mock()
    cursor = CursorMySQL(cursor_real)

    assert cursor.execute("SELECT * FROM productos WHERE codigo = %s", ("A",)) is cursor
    cursor_real.execute.assert_called_once_with(
        "SELECT * FROM productos WHERE codigo = %s", ("A",)
    )


def test_el_pool_de_conexiones_tiene_tamano_cinco():
    assert TAMANO_POOL == 5


def test_el_codigo_de_producto_debe_usar_el_formato_cerpint():
    inventario = InventarioModel()

    assert inventario.normalizar_codigo_producto("abcd1234") == "ABCD-1234"
    inventario._validar_codigo("ABCD-1234")
