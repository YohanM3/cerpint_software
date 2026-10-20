"""Utilidades para almacenar y comprobar contraseñas de forma segura."""

import hashlib
import hmac
import secrets

ALGORITMO = "pbkdf2_sha256"
ITERACIONES = 600_000


def generar_hash_clave(clave: str) -> str:
    """Genera una representación PBKDF2 de la contraseña."""
    sal = secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, ITERACIONES)
    return "$".join((ALGORITMO, str(ITERACIONES), sal.hex(), derivada.hex()))


def es_hash_clave(valor: str) -> bool:
    return isinstance(valor, str) and valor.startswith(f"{ALGORITMO}$")


def necesita_rehash(valor_guardado: str) -> bool:
    """Indica si el hash usa menos iteraciones que las actuales."""
    if not es_hash_clave(valor_guardado):
        return True
    try:
        return int(valor_guardado.split("$")[1]) < ITERACIONES
    except (IndexError, ValueError):
        return True


def verificar_clave(clave: str, valor_guardado: str) -> bool:
    """Compara una contraseña con un hash PBKDF2; cualquier otro valor se rechaza."""
    if not es_hash_clave(valor_guardado):
        return False

    try:
        algoritmo, iteraciones, sal_hex, hash_hex = valor_guardado.split("$")
        if algoritmo != ALGORITMO:
            return False
        derivada = hashlib.pbkdf2_hmac(
            "sha256",
            clave.encode("utf-8"),
            bytes.fromhex(sal_hex),
            int(iteraciones),
        )
        return hmac.compare_digest(derivada.hex(), hash_hex)
    except (TypeError, ValueError):
        return False
