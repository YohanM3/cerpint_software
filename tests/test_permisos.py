import pytest

from database.errores import PermisoError
from servicios.auditoria import establecer_sesion, requerir_administrador
from servicios.permisos import _filas_a_permisos, _permisos_a_filas


def test_permisos_se_mapean_a_indicadores_crud_de_la_base():
    permisos = {
        "inventario.ver",
        "inventario.modificar",
        "clientes.ver",
        "ventas.realizar",
        "consultas.modificar",
    }

    filas = _permisos_a_filas(permisos)

    assert filas["inventario"] == {
        "puede_ver": 1,
        "puede_crear": 1,
        "puede_editar": 1,
        "puede_eliminar": 1,
    }
    assert filas["ventas"]["puede_crear"] == 1
    assert filas["consultas"]["puede_editar"] == 1
    filas_db = [
        (modulo, *[acciones[campo] for campo in (
            "puede_ver",
            "puede_crear",
            "puede_editar",
            "puede_eliminar",
        )])
        for modulo, acciones in filas.items()
    ]
    assert _filas_a_permisos(filas_db) == permisos


def test_un_permiso_de_escritura_no_autoriza_otro_modulo():
    establecer_sesion("vendedor", "vendedor", {"inventario.modificar"})
    try:
        requerir_administrador("inventario.modificar")
        with pytest.raises(PermisoError):
            requerir_administrador("clientes.modificar")
    finally:
        establecer_sesion("Sistema", "sistema")


def test_sin_sesion_se_deniega_por_defecto():
    establecer_sesion("Sistema", "sistema")
    with pytest.raises(PermisoError):
        requerir_administrador("inventario.modificar")


def test_sesion_explicita_de_sistema_administrador_esta_permitida():
    establecer_sesion("Sistema", "administrador")
    try:
        requerir_administrador("inventario.modificar")
    finally:
        establecer_sesion("Sistema", "sistema")
