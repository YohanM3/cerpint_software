from modulos.consultas.consultas_view import ConsultasView


def test_ordenar_filas_numericas_ascendente_y_descendente_con_vacios_al_final():
    filas = [("10",), ("2",), ("",), ("1",)]

    ascendente = ConsultasView._ordenar_filas(filas, 0)
    descendente = ConsultasView._ordenar_filas(filas, 0, descendente=True)

    assert ascendente == [("1",), ("2",), ("10",), ("",)]
    assert descendente == [("10",), ("2",), ("1",), ("",)]


def test_ordenar_filas_de_fecha_y_texto():
    fechas = [("2026-10-04",), ("2026-02-15",), ("2026-06-03",)]
    nombres = [("María",), ("ana",), ("Carlos",)]

    assert ConsultasView._ordenar_filas(fechas, 0) == [
        ("2026-02-15",),
        ("2026-06-03",),
        ("2026-10-04",),
    ]
    assert ConsultasView._ordenar_filas(nombres, 0) == [
        ("ana",),
        ("Carlos",),
        ("María",),
    ]
