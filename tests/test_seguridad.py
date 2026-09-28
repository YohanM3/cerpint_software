from servicios.seguridad import es_hash_clave, generar_hash_clave, verificar_clave


def test_hash_de_clave_valida_solo_la_clave_original():
    clave_guardada = generar_hash_clave("1234")

    assert es_hash_clave(clave_guardada)
    assert verificar_clave("1234", clave_guardada)
    assert not verificar_clave("incorrecta", clave_guardada)


def test_verificar_clave_acepta_registro_legacy_para_migrarlo():
    assert verificar_clave("1234", "1234")
    assert not verificar_clave("incorrecta", "1234")
