"""Respaldo local de la base de datos antes de operaciones críticas."""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

RESPALDOS_A_CONSERVAR = 10


def crear_respaldo() -> Path:
    """Genera un respaldo lógico y conserva solo los últimos RESPALDOS_A_CONSERVAR."""
    from database.conexion import MYSQL_DATABASE

    destino = _crear_respaldo_mysql(MYSQL_DATABASE)
    _aplicar_retencion(destino.parent)
    return destino


def _aplicar_retencion(directorio: Path) -> None:
    """Borra los respaldos más antiguos; un fallo al borrar no debe afectar la operación."""
    respaldos = sorted(directorio.glob("*.sql"), key=lambda ruta: ruta.name)
    for antiguo in respaldos[:-RESPALDOS_A_CONSERVAR]:
        try:
            antiguo.unlink()
        except OSError:
            pass


def _crear_respaldo_mysql(nombre_base: str) -> Path:
    """Genera un volcado lógico sin exponer la contraseña en la línea de comandos."""
    raiz = Path(__file__).resolve().parent.parent
    destino_dir = raiz / "respaldos"
    destino_dir.mkdir(parents=True, exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destino = destino_dir / f"{nombre_base}_{sello}.sql"
    ejecutable = os.getenv("FERRETERIA_MYSQLDUMP") or shutil.which("mysqldump")
    if not ejecutable:
        candidatos = list(Path("C:/laragon/bin/mysql").glob("*/bin/mysqldump.exe"))
        ejecutable = str(candidatos[-1]) if candidatos else None
    if not ejecutable:
        raise RuntimeError("No se encontró mysqldump para crear el respaldo MySQL.")

    entorno = os.environ.copy()
    if entorno.get("FERRETERIA_DB_PASSWORD"):
        entorno["MYSQL_PWD"] = entorno["FERRETERIA_DB_PASSWORD"]
    comando = [
        ejecutable,
        "--host",
        entorno.get("FERRETERIA_DB_HOST", "localhost"),
        "--port",
        entorno.get("FERRETERIA_DB_PORT", "3307"),
        "--user",
        entorno.get("FERRETERIA_DB_USER", "ferreteria_app"),
        "--single-transaction",
        "--skip-lock-tables",
        "--no-tablespaces",
        "--triggers",
        nombre_base,
    ]
    try:
        with destino.open("wb") as archivo:
            subprocess.run(
                comando, check=True, stdout=archivo, stderr=subprocess.PIPE, env=entorno
            )
    except subprocess.CalledProcessError as error:
        destino.unlink(missing_ok=True)
        detalle = error.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"No se pudo crear el respaldo MySQL: {detalle}") from error
    return destino
