"""Documentazione della versione portfolio."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from data.cassaforte import ETICHETTE_CATEGORIE, movimenti
from documents.excel.comune import salva_prospetto

NOME_FILE = "Cassaforte_Movimenti.xlsx"

INTESTAZIONE = [
    "Data", "Ora", "Elemento", "Categoria", "Operazione",
    "Persona", "Busta", "Data busta", "Note",
]

_ETICHETTE_TIPO = {
    "deposito": "Deposito",
    "uscita": "Uscita",
    "rientro": "Rientro",
}


def genera_prospetto(cartella_destinazione: str) -> Path:
    libro = Workbook()
    foglio = libro.active
    foglio.title = "Movimenti"

    foglio.append(INTESTAZIONE)
    for cella in foglio[1]:
        cella.font = Font(bold=True)


    for movimento in reversed(movimenti()):
        foglio.append([
            movimento["data"] or "",
            movimento["ora"] or "",
            movimento["descrizione"],
            ETICHETTE_CATEGORIE.get(movimento["categoria"], movimento["categoria"]),
            _ETICHETTE_TIPO.get(movimento["tipo"], movimento["tipo"]),
            movimento["persona"] or "",
            movimento["numero_busta"] or "",
            movimento["data_busta"] or "",
            movimento["note"] or "",
        ])

    percorso = Path(cartella_destinazione) / NOME_FILE
    salva_prospetto(libro, percorso)
    return percorso
