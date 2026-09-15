"""Documentazione della versione portfolio."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from data.consegne_radio import consegne_del_mese
from documents.excel.comune import salva_prospetto

INTESTAZIONE = [
    "DATA", "NUMERO RADIO", "ORARIO RITIRO", "COGNOME RITIRO",
    "AURICOLARE SI/NO", "ORARIO RICONSEGNA", "COGNOME RICONSEGNA", "NOTE",
]

NOMI_MESI_ITALIANI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]


def genera_prospetto_mese(anno: int, mese: int, cartella_destinazione: str) -> Path:
    consegne = consegne_del_mese(anno, mese)

    libro = Workbook()
    foglio = libro.active
    foglio.title = "Foglio1"
    foglio.append(INTESTAZIONE)
    for cella in foglio[1]:
        cella.font = Font(bold=True)

    for consegna in consegne:
        foglio.append([
            consegna["data"],
            consegna["radio_identificativo"],
            consegna["ora_consegna"],
            consegna["cognome_consegna"],
            consegna["auricolare"] or "",
            consegna["ora_riconsegna"] or "",
            consegna["cognome_riconsegna"] or "",
            consegna["note"] or "",
        ])

    nome_mese = NOMI_MESI_ITALIANI[mese - 1]
    percorso = Path(cartella_destinazione) / f"Consegna_Radio_{nome_mese}_{anno}.xlsx"
    salva_prospetto(libro, percorso)
    return percorso
