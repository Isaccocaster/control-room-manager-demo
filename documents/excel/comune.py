"""Documentazione della versione portfolio."""
from pathlib import Path

from config.registro import logger

_registro = logger(__name__)


def salva_prospetto(libro, percorso: Path) -> Path:
    """Documentazione della versione portfolio."""
    try:
        libro.save(percorso)
    except Exception as errore:
        _registro.error(
            "Scrittura del prospetto Excel fallita (%s): %s",
            type(errore).__name__, percorso, exc_info=True,
        )
        raise
    return percorso
