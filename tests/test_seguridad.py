from servicios.seguridad import (
    ITERACIONES,
    generar_hash_clave,
    necesita_rehash,
    verificar_clave,
)


def test_clave_en_texto_plano_ya_no_se_acepta():
    assert verificar_clave("1234", "1234") is False


def test_hash_nuevo_verifica_y_no_necesita_rehash():
    valor = generar_hash_clave("clave-segura")
    assert valor.split("$")[1] == str(ITERACIONES) == "600000"
    assert verificar_clave("clave-segura", valor)
    assert not verificar_clave("otra", valor)
    assert not necesita_rehash(valor)


def test_hash_con_menos_iteraciones_se_verifica_y_pide_rehash():
    import hashlib

    sal = b"0" * 16
    derivada = hashlib.pbkdf2_hmac("sha256", b"vieja", sal, 310_000)
    valor = "$".join(("pbkdf2_sha256", "310000", sal.hex(), derivada.hex()))
    assert verificar_clave("vieja", valor)
    assert necesita_rehash(valor)
    assert necesita_rehash("texto-plano")
