"""Documentazione della versione portfolio."""
import json
import os
from pathlib import Path

from config.registro import logger

_registro = logger(__name__)

NOME_FILE_IMPOSTAZIONI = "config.json"
NOME_CARTELLA_DATI = "demo_data"


VARIABILE_AMBIENTE_CARTELLA_DATI = "CONTROL_ROOM_DEMO_DATA_DIR"


CHIAVE_PROSPETTI_CONSEGNA_RADIO = "cartella_prospetti_consegna_radio"
CHIAVE_STORICA_PROSPETTI_CONSEGNA_RADIO = "cartella_prospetti_radio"


CHIAVE_PROSPETTI_GESTIONE_RADIO = "cartella_prospetti_gestione_radio"


CHIAVE_OGGETTI_SMARRITI = "cartella_oggetti_smarriti"


CHIAVE_CASSAFORTE = "cartella_cassaforte"


CHIAVE_PASSAGGIO_CONSEGNE = "cartella_passaggio_consegne"

CHIAVI_CARTELLE = [
    "cartella_rapporti",
    CHIAVE_PROSPETTI_GESTIONE_RADIO,
    CHIAVE_PROSPETTI_CONSEGNA_RADIO,
    "cartella_prospetti_chiavi",
    CHIAVE_OGGETTI_SMARRITI,
    CHIAVE_CASSAFORTE,
    CHIAVE_PASSAGGIO_CONSEGNE,
    "cartella_backup",
]


def cartella_progetto() -> Path:
    """Documentazione della versione portfolio."""
    return Path(__file__).resolve().parent.parent


def cartella_dati_applicazione() -> Path:
    """Documentazione della versione portfolio."""
    override = os.environ.get(VARIABILE_AMBIENTE_CARTELLA_DATI)
    cartella = Path(override) if override else cartella_progetto() / NOME_CARTELLA_DATI
    cartella.mkdir(parents=True, exist_ok=True)
    return cartella


def percorso_file_impostazioni() -> Path:
    return cartella_dati_applicazione() / NOME_FILE_IMPOSTAZIONI


def carica_impostazioni() -> dict:
    """Documentazione della versione portfolio."""
    percorso = percorso_file_impostazioni()
    if not percorso.exists():
        return {chiave: "" for chiave in CHIAVI_CARTELLE}

    try:
        with open(percorso, "r", encoding="utf-8") as file:
            dati = json.load(file)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as errore:
        _registro.error(
            "File di configurazione illeggibile (%s): riparto con cartelle vuote",
            type(errore).__name__, exc_info=True,
        )
        _salva_da_parte_file_corrotto(percorso)
        return {chiave: "" for chiave in CHIAVI_CARTELLE}

    _migra_cartella_prospetti_consegna_radio(dati)


    for chiave in CHIAVI_CARTELLE:
        dati.setdefault(chiave, "")
    return dati


def _salva_da_parte_file_corrotto(percorso: Path) -> None:
    """Documentazione della versione portfolio."""
    try:
        percorso.replace(percorso.with_suffix(percorso.suffix + ".corrotto"))
        _registro.warning("File corrotto conservato come %s.corrotto", percorso.name)
    except OSError:
        _registro.warning("Non e' stato possibile mettere da parte %s", percorso, exc_info=True)


def _migra_cartella_prospetti_consegna_radio(dati: dict) -> None:
    """Documentazione della versione portfolio."""
    percorso_salvato = dati.pop(CHIAVE_STORICA_PROSPETTI_CONSEGNA_RADIO, "")
    if percorso_salvato and not dati.get(CHIAVE_PROSPETTI_CONSEGNA_RADIO):
        dati[CHIAVE_PROSPETTI_CONSEGNA_RADIO] = percorso_salvato


def salva_impostazioni(impostazioni: dict) -> None:
    """Documentazione della versione portfolio."""
    percorso = percorso_file_impostazioni()
    percorso_temporaneo = percorso.with_suffix(percorso.suffix + ".tmp")

    with open(percorso_temporaneo, "w", encoding="utf-8") as file:
        json.dump(impostazioni, file, indent=2, ensure_ascii=False)
        file.flush()
        os.fsync(file.fileno())

    os.replace(percorso_temporaneo, percorso)


def cartella_esiste(percorso: str) -> bool:
    return bool(percorso) and Path(percorso).is_dir()
