"""Documentazione della versione portfolio."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from data.oggetti_smarriti import (
    STATO_IN_CUSTODIA,
    STATO_RICONSEGNATO,
    STATO_SMALTITO,
    oggetti_per_stato,
)
from documents.excel.comune import salva_prospetto


TITOLO_REGISTRO = (
    "Registro di inventario degli oggetti ritrovati _ PROCEDURA SULLE MODALITA' "
    "OPERATIVE PER LA GESTIONE DEGLI OGGETTI RINVENUTI ALL'INTERNO DELL'AREA Demo"
)

NOMI_FILE = {
    STATO_IN_CUSTODIA: "Oggetti_Smarriti_In_Custodia.xlsx",
    STATO_RICONSEGNATO: "Oggetti_Smarriti_Riconsegnati.xlsx",
    STATO_SMALTITO: "Oggetti_Smarriti_Smaltiti.xlsx",
}


_INTESTAZIONI = {
    STATO_IN_CUSTODIA: [
        "gg/mese/anno della presa in consegna", "nr. Sigillo", "oggetto",
        "ubicazione", "proprietario", "operatore ritiro",
    ],
    STATO_RICONSEGNATO: [
        "gg/mese/anno della presa in consegna", "nr. Sigillo",
        "gg/mese/anno della riconsegna", "oggetto", "ubicazione", "proprietario",
        "ora riconsegna", "riconsegnato a", "operatore riconsegna", "note",
    ],
    STATO_SMALTITO: [
        "gg/mese/anno della presa in consegna", "nr. Sigillo", "oggetto",
        "ubicazione", "proprietario", "gg/mese/anno dello smaltimento",
        "ora smaltimento", "operatore smaltimento", "motivo/note",
    ],
}


def _vuoto(valore) -> str:
    return valore or ""


def _riga(stato: str, oggetto: dict) -> list:
    if stato == STATO_IN_CUSTODIA:
        return [
            _vuoto(oggetto["data_ritiro"]), _vuoto(oggetto["numero_sigillo"]),
            _vuoto(oggetto["descrizione"]), _vuoto(oggetto["ubicazione"]),
            _vuoto(oggetto["proprietario"]), _vuoto(oggetto["operatore_ritiro"]),
        ]
    if stato == STATO_RICONSEGNATO:
        return [
            _vuoto(oggetto["data_ritiro"]), _vuoto(oggetto["numero_sigillo"]),
            _vuoto(oggetto["data_riconsegna"]), _vuoto(oggetto["descrizione"]),
            _vuoto(oggetto["ubicazione"]), _vuoto(oggetto["proprietario"]),
            _vuoto(oggetto["ora_riconsegna"]), _vuoto(oggetto["riconsegnato_a"]),
            _vuoto(oggetto["operatore_riconsegna"]), _vuoto(oggetto["note_riconsegna"]),
        ]
    return [
        _vuoto(oggetto["data_ritiro"]), _vuoto(oggetto["numero_sigillo"]),
        _vuoto(oggetto["descrizione"]), _vuoto(oggetto["ubicazione"]),
        _vuoto(oggetto["proprietario"]), _vuoto(oggetto["data_smaltimento"]),
        _vuoto(oggetto["ora_smaltimento"]), _vuoto(oggetto["operatore_smaltimento"]),
        _vuoto(oggetto["note_smaltimento"]),
    ]


def genera_prospetto(stato: str, cartella_destinazione: str) -> Path:
    """Documentazione della versione portfolio."""
    libro = Workbook()
    foglio = libro.active
    foglio.title = "Foglio1"

    if stato == STATO_IN_CUSTODIA:
        foglio.append([TITOLO_REGISTRO])
        foglio["A1"].font = Font(bold=True)
        foglio.append([])

    foglio.append(_INTESTAZIONI[stato])
    for cella in foglio[foglio.max_row]:
        cella.font = Font(bold=True)

    for oggetto in oggetti_per_stato(stato):
        foglio.append(_riga(stato, oggetto))

    percorso = Path(cartella_destinazione) / NOMI_FILE[stato]
    salva_prospetto(libro, percorso)
    return percorso


def genera_prospetti(stati, cartella_destinazione: str) -> list[Path]:
    """Documentazione della versione portfolio."""
    return [genera_prospetto(stato, cartella_destinazione) for stato in stati]
