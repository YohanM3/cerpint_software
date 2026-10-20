from unittest.mock import Mock, patch

from modulos.clientes.clientes_model import ClientesModel


def test_obtener_todos_incluye_clientes_inactivos_y_muestra_estado():
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [
        ("V-123", "Cliente activo", "", "", "Activo"),
        ("V-456", "Cliente inactivo", "", "", "Inactivo"),
    ]

    with patch(
        "modulos.clientes.clientes_model.obtener_conexion", return_value=conexion
    ):
        clientes = ClientesModel().obtener_todos()

    consulta = cursor.execute.call_args.args[0]
    assert "CASE WHEN activo = 1 THEN 'Activo' ELSE 'Inactivo' END" in consulta
    assert "FROM clientes ORDER BY nombre" in consulta
    assert clientes[1][0] == "V-456"
    assert clientes[1][4] == "Inactivo"
