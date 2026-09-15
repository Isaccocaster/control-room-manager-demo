"""Documentazione della versione portfolio."""
import re
from datetime import date, datetime


FORMATO_DATA = "%d-%m-%Y"


def normalizza(testo: str) -> str:
    """Documentazione della versione portfolio."""
    return re.sub(r"[\s\-]", "", testo).lower()


def ordine_cronologico(colonna: str, con_ora: bool = False) -> str:
    """Documentazione della versione portfolio."""
    espressione = (
        f"substr({colonna}, 7, 4) || substr({colonna}, 4, 2) || substr({colonna}, 1, 2)"
    )
    if con_ora:
        espressione += f" || substr({colonna}, 12, 5)"
    return espressione


def mese_di_riferimento(data_testo: str) -> tuple[int, int]:
    """Documentazione della versione portfolio."""
    return int(data_testo[6:10]), int(data_testo[3:5])


def data_valida(testo: str) -> bool:
    """Documentazione della versione portfolio."""
    testo = testo.strip()
    if not testo:
        return True
    try:
        datetime.strptime(testo, FORMATO_DATA)
        return True
    except ValueError:
        return False


def giorni_trascorsi(data_testo: str | None, oggi: date | None = None) -> int | None:
    """Documentazione della versione portfolio."""
    if not data_testo:
        return None
    try:
        data = datetime.strptime(data_testo.strip(), FORMATO_DATA).date()
    except ValueError:
        return None
    return ((oggi or date.today()) - data).days
