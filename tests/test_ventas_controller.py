from unittest.mock import Mock

from modulos.ventas.ventas_controller import VentasController
from modulos.ventas.ventas_model import VentasModel


class VistaVentaDummy:
    def __init__(self):
        self.txt_cliente_buscar = Mock()
        self.txt_cliente_buscar.obtener_texto.return_value = "cli"
        self.txt_codigo = Mock()
        self.txt_codigo.obtener_texto.return_value = "PROD-1"
        self.txt_cantidad = Mock()
        self.lbl_cliente_activo = Mock()
        self.mostrar_sugerencias = Mock()
        self.ocultar_sugerencias = Mock()
        self.desbloquear_articulos = Mock()


def test_ventas_controller_busca_y_selecciona_cliente():
    clientes_model = Mock()
    clientes_model.buscar_sugerencias.return_value = [("CLI-1", "Cliente Uno")]

    vista = VistaVentaDummy()
    controller = VentasController(
        modelo=VentasModel(),
        vista=vista,
        clientes_model=clientes_model,
        inventario_model=Mock(),
    )

    controller._buscar_cliente()

    clientes_model.buscar_sugerencias.assert_called_once_with("cli", 5)
    vista.mostrar_sugerencias.assert_called_once()

    controller.seleccionar_cliente("CLI-1", "Cliente Uno")

    assert controller.cliente_actual == "CLI-1"
    vista.lbl_cliente_activo.configure.assert_called_once()
    vista.txt_codigo.focus_set.assert_called_once()


def test_ventas_controller_selecciona_cliente_con_flecha_y_enter():
    clientes_model = Mock()
    clientes_model.buscar_sugerencias.return_value = [
        ("CLI-1", "Cliente Uno"),
        ("CLI-2", "Cliente Dos"),
    ]
    vista = VistaVentaDummy()
    vista.resaltar_sugerencia_cliente = Mock()
    controller = VentasController(
        modelo=VentasModel(),
        vista=vista,
        clientes_model=clientes_model,
        inventario_model=Mock(),
    )

    controller._buscar_cliente()
    controller._mover_sugerencia_cliente(-1)
    controller._al_escribir_cliente(Mock(keysym="Down"))
    controller._confirmar_cliente()

    clientes_model.buscar_sugerencias.assert_called_once_with("cli", 5)
    assert controller.cliente_actual == "CLI-2"
    vista.resaltar_sugerencia_cliente.assert_called_with(1)
    vista.txt_codigo.focus_set.assert_called_once()


def test_ventas_controller_selecciona_producto_con_flecha_y_enter():
    vista = VistaVentaDummy()
    vista.txt_nombre = Mock()
    vista.txt_precio = Mock()
    vista.ocultar_sugerencias_productos = Mock()
    vista.mostrar_sugerencias_productos = Mock()
    vista.resaltar_sugerencia_producto = Mock()
    inventario_model = Mock()
    inventario_model.buscar_sugerencias.return_value = [
        ("PROD-1", "Producto Uno", 3.5, 4),
        ("PROD-2", "Producto Dos", 5.0, 2),
    ]
    controller = VentasController(
        modelo=VentasModel(),
        vista=vista,
        clientes_model=Mock(),
        inventario_model=inventario_model,
    )

    controller._buscar_producto()
    controller._mover_sugerencia_producto(1)
    controller._mover_sugerencia_producto(1)
    controller._al_escribir_producto(Mock(keysym="Down"))
    controller._confirmar_producto()

    inventario_model.buscar_sugerencias.assert_called_once_with("PROD-1", 5)
    vista.resaltar_sugerencia_producto.assert_called_with(1)
    vista.txt_codigo.insert.assert_called_once_with(0, "PROD-2")
    vista.txt_cantidad.focus_set.assert_called_once()


def test_ventas_controller_no_agrega_mas_unidades_que_el_stock_disponible():
    vista = VistaVentaDummy()
    vista.txt_codigo.obtener_texto.return_value = "PROD-1"
    vista.txt_cantidad.obtener_texto.return_value = "2"
    modelo = VentasModel()
    modelo.carrito = [
        {
            "codigo": "PROD-1",
            "producto": "Producto Uno",
            "cantidad": 1,
            "precio": 3.5,
            "subtotal": 3.5,
        }
    ]
    inventario_model = Mock()
    inventario_model.obtener_por_codigo_o_nombre.return_value = (
        "PROD-1",
        "Producto Uno",
        3.5,
        2,
    )
    controller = VentasController(
        modelo=modelo,
        vista=vista,
        clientes_model=Mock(),
        inventario_model=inventario_model,
    )

    with __import__("unittest.mock").mock.patch(
        "modulos.ventas.ventas_controller.messagebox.showwarning"
    ) as advertencia:
        controller.agregar_producto_desde_form()

    advertencia.assert_called_once()
    assert len(modelo.carrito) == 1


def test_enter_en_cantidad_agrega_producto_y_regresa_al_codigo():
    vista = VistaVentaDummy()
    vista.txt_codigo.obtener_texto.return_value = "PROD-1"
    vista.txt_cantidad.obtener_texto.return_value = "2"
    vista.limpiar_formulario_articulo = Mock()
    vista.tabla_ventas = Mock()
    vista.lbl_total = Mock()
    modelo = VentasModel()
    inventario_model = Mock()
    inventario_model.obtener_por_codigo_o_nombre.return_value = (
        "PROD-1",
        "Producto Uno",
        3.5,
        2,
    )
    controller = VentasController(
        modelo=modelo,
        vista=vista,
        clientes_model=Mock(),
        inventario_model=inventario_model,
    )

    assert controller._agregar_producto_con_enter() == "break"

    assert modelo.carrito[0]["codigo"] == "PROD-1"
    assert modelo.carrito[0]["cantidad"] == 2
    vista.txt_codigo.focus_set.assert_called_once()


def test_ventas_controller_limpiar_nuevo_pedido_despues_de_pdf():
    vista = VistaVentaDummy()
    vista.txt_cliente_buscar.limpiar = Mock()
    vista.lbl_cliente_activo = Mock()
    vista.limpiar_formulario_articulo = Mock()
    vista.limpiar_formulario_venta = Mock()
    vista.tabla_ventas = Mock()
    vista.tabla_ventas.limpiar_tabla = Mock()
    vista.lbl_total = Mock()
    vista.menu_estado_pago = Mock()

    modelo = Mock()
    modelo.carrito = [{"codigo": "PROD-1", "producto": "Producto", "cantidad": 1}]
    modelo.procesar_venta_bd.return_value = (
        7,
        {"documento": "CLI-1", "nombre": "Cliente Uno"},
        [
            {
                "codigo": "PROD-1",
                "nombre": "Producto",
                "cantidad": 1,
                "precio": 10.0,
                "subtotal": 10.0,
            }
        ],
        10.0,
    )

    controller = VentasController(
        modelo=modelo,
        vista=vista,
        clientes_model=Mock(),
        inventario_model=Mock(),
    )
    controller.cliente_actual = "CLI-1"

    with __import__("unittest.mock").mock.patch.object(
        VentasController,
        "procesar_y_generar_pdf",
        return_value=False,
    ):
        assert controller.procesar_venta() is False

    assert controller.cliente_actual is None
    vista.txt_cliente_buscar.limpiar.assert_called_once()
    vista.tabla_ventas.limpiar_tabla.assert_called_once()
    vista.lbl_total.configure.assert_called_once_with(text="Total: $0.00")
    vista.menu_estado_pago.set.assert_called_once_with("A Credito")


def test_ventas_model_elimina_item_del_carrito():
    modelo = VentasModel()
    modelo.agregar_item("PROD-001", "Tuerca", 2, 3.5)
    modelo.agregar_item("PROD-002", "Tornillo", 1, 5.0)

    modelo.eliminar_item("PROD-001")

    assert [item["codigo"] for item in modelo.carrito] == ["PROD-002"]
    assert modelo.calcular_total() == 5.0
