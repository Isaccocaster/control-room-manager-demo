"""Documentazione della versione portfolio."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from data.passaggio_consegne import comunicazioni_del_mese
from documents.excel.comune import salva_prospetto

INTESTAZIONE = ["DATA E ORA", "COMUNICAZIONE", "IMPORTANTE", "TOLTA DAL BLOCCO NOTE IL"]

NOMI_MESI_ITALIANI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]


def nome_file(anno: int, mese: int) -> str:
    return f"Passaggio_Consegne_{NOMI_MESI_ITALIANI[mese - 1]}_{anno}.xlsx"


def genera_prospetto_mese(anno: int, mese: int, cartella_destinazione: str) -> Path:
    """Documentazione della versione portfolio."""
    libro = Workbook()
    foglio = libro.active
    foglio.title = "Foglio1"

    foglio.append(INTESTAZIONE)
    for cella in foglio[1]:
        cella.font = Font(bold=True)

    for comunicazione in comunicazioni_del_mese(anno, mese):
        foglio.append([
            comunicazione["creato_il"],
            comunicazione["testo"],
            "SI" if comunicazione["fissato"] else "",
            comunicazione["archiviato_il"] or "",
        ])

    percorso = Path(cartella_destinazione) / nome_file(anno, mese)
    salva_prospetto(libro, percorso)
    return percorso
