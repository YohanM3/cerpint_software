from types import SimpleNamespace
from unittest.mock import Mock

from modulos.consultas.consultas_controller import ConsultasController


def crear_vista_consultas():
    vista = SimpleNamespace()
    vista.btn_pendientes = Mock()
    vista.btn_periodo = Mock()
    vista.btn_cliente = Mock()
    vista.btn_reposicion = Mock()
    vista.btn_cambiar_pago = Mock()
    vista.btn_anular_nota = Mock()
    vista.tabla_reportes = SimpleNamespace(tabla=Mock(), columnas=[])
    vista.tabla_reportes.tabla.selection.return_value = []
    vista.txt_cliente = Mock()
    vista.txt_cliente.obtener_texto.return_value = "CLI"
    vista.txt_fecha_inicio = Mock()
    vista.txt_fecha_inicio.obtener_texto.return_value = ""
    vista.txt_fecha_fin = Mock()
    vista.txt_fecha_fin.obtener_texto.return_value = ""
    vista.txt_dias_analisis = Mock()
    vista.txt_dias_analisis.obtener_texto.return_value = "30"
    vista.mostrar_sugerencias_clientes = Mock()
    vista.resaltar_sugerencia_cliente = Mock()
    vista.ocultar_sugerencias_clientes = Mock()
    vista.mostrar_tabla = Mock()
    vista.ultimo_resultado = None
    return vista


def crear_controlador(modelo=None, clientes_model=None, solo_lectura=False):
    vista = crear_vista_consultas()
    if modelo is None:
        modelo = Mock()
        modelo.notas_pendientes_por_pagar.return_value = []
        modelo.obtener_historial_notas.return_value = []
    clientes_model = clientes_model or Mock()
    controlador = ConsultasController(
        modelo, vista, clientes_model, solo_lectura=solo_lectura
    )
    return controlador, vista, modelo, clientes_model


def test_controlador_carga_pendientes_al_iniciarse():
    controlador, vista, modelo, _ = crear_controlador()

    modelo.notas_pendientes_por_pagar.assert_called_once_with()
    assert vista.ultimo_resultado["filas"] == []
    assert "Situación" in vista.ultimo_resultado["columnas"]


def test_consulta_cliente_selecciona_sugerencia_con_flechas_y_enter():
    clientes_model = Mock()
    clientes_model.buscar_sugerencias.return_value = [
        ("CLI-1", "Cliente Uno"),
        ("CLI-2", "Cliente Dos"),
    ]
    modelo = Mock()
    modelo.notas_pendientes_por_pagar.return_value = []
    modelo.obtener_historial_notas.return_value = []
    controlador, vista, modelo, _ = crear_controlador(modelo, clientes_model)
    vista.txt_fecha_inicio.obtener_texto.return_value = "2026-01-01"
    vista.txt_fecha_fin.obtener_texto.return_value = "2026-01-31"

    controlador._al_escribir_cliente(SimpleNamespace(keysym="i"))
    controlador._mover_sugerencia_cliente(1)
    controlador._mover_sugerencia_cliente(1)
    controlador._al_escribir_cliente(SimpleNamespace(keysym="Down"))
    controlador._confirmar_cliente()

    clientes_model.buscar_sugerencias.assert_called_once_with("CLI", 6)
    vista.resaltar_sugerencia_cliente.assert_called_with(1)
    vista.txt_cliente.establecer_texto.assert_called_once_with("CLI-2")
    modelo.obtener_historial_notas.assert_called_once_with(
        "2026-01-01", "2026-01-31", "CLI-2"
    )
    assert controlador.cliente_seleccionado == "CLI-2"


def test_consulta_global_acepta_fechas_vacias_o_rango_completo():
    controlador, vista, modelo, _ = crear_controlador()

    controlador.consultar_periodo()
    modelo.obtener_historial_notas.assert_called_once_with("", "")

    vista.txt_fecha_inicio.obtener_texto.return_value = "2026-01-01"
    vista.txt_fecha_fin.obtener_texto.return_value = "2026-01-31"
    controlador.consultar_periodo()

    modelo.obtener_historial_notas.assert_called_with("2026-01-01", "2026-01-31")
    vista.txt_cliente.limpiar.assert_called()


def test_consultas_formatea_importes_monetarios_en_la_tabla():
    modelo = Mock()
    modelo.notas_pendientes_por_pagar.return_value = [
        (
            1,
            "2026-01-01",
            "CLI-1",
            "Cliente Uno",
            12.5,
            "A Credito",
            7.5,
            30,
            "2026-01-31",
            3,
            "Vigente",
        )
    ]
    modelo.obtener_historial_notas.return_value = []

    _, vista, _, _ = crear_controlador(modelo)

    filas = vista.mostrar_tabla.call_args.args[1]
    assert filas[0][4] == "12.50"
    assert filas[0][6] == "7.50"


def test_consultor_no_puede_cambiar_o_anular_notas():
    controlador, vista, modelo, _ = crear_controlador(solo_lectura=True)

    with __import__("unittest.mock").mock.patch(
        "modulos.consultas.consultas_controller.messagebox.showwarning"
    ) as advertencia:
        controlador.cambiar_pago_nota_seleccionada()
        controlador.anular_nota_seleccionada()

    vista.btn_cambiar_pago.cambiar_estado.assert_called_with(False)
    vista.btn_anular_nota.cambiar_estado.assert_called_with(False)
    modelo.alternar_pago_nota.assert_not_called()
    modelo.anular_venta.assert_not_called()
    assert advertencia.call_count == 2
