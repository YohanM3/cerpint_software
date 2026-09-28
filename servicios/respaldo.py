"""Respaldo local de la base de datos antes de operaciones críticas."""

import shutil
from datetime import datetime
from pathlib import Path


def crear_respaldo() -> Path | None:
    """Copia la base actual en la carpeta respaldos y devuelve su ruta."""
    from database.conexion import DB_NAME

    origen = Path(DB_NAME)
    if not origen.exists():
        return None

    destino_dir = origen.parent / "respaldos"
    destino_dir.mkdir(exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destino = destino_dir / f"{origen.stem}_{sello}{origen.suffix}"
    shutil.copy2(origen, destino)
    return destino
