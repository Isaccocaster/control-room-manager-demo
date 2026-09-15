"""Documentazione della versione portfolio."""
import sqlite3

from config.registro import logger
from config.versione import (
    SCHEMA_DATABASE,
    SCHEMA_MASSIMO_SUPPORTATO,
    SCHEMA_NON_NUMERATO,
)

_registro = logger(__name__)


TABELLE_SCHEMA_1 = (
    "passaggio_consegne",
    "bacheche",
    "chiavi",
    "cassaforte_chiavi",
    "chiavi_movimenti",
    "consegne_radio",
    "radio",
    "auricolari_conteggio",
    "radio_eventi",
    "oggetti_smarriti",
    "cassaforte_elementi",
    "cassaforte_movimenti",
    "rapporti_giornalieri",
    "operatori",
)


COLONNE_SCHEMA_1 = {
    "passaggio_consegne": ("fissato", "archiviato_il", "fissato_il"),
    "consegne_radio": ("data_riconsegna",),
    "rapporti_giornalieri": ("operatore_id",),
    "operatori": ("attivo", "categoria_operatore", "nome_canonico", "cognome_canonico"),
}


class ErroreSchemaNonSupportato(Exception):
    """Documentazione della versione portfolio."""

    def __init__(self, trovata: int, massima: int):
        self.trovata = trovata
        self.massima = massima
        super().__init__(
            f"Schema del database non supportato: trovato {trovata}, "
            f"massimo supportato {massima}"
        )

    @property
    def messaggio_operatore(self) -> str:
        return (
            "Questo database è stato aggiornato da una versione più recente di "
            "Control Room Manager Demo e non può essere usato in sicurezza con la versione "
            "installata su questo computer.\n\n"
            "I dati non sono stati toccati. Per continuare occorre installare la "
            "versione aggiornata del programma: contatta l'ufficio IT."
        )


def versione_schema(connessione: sqlite3.Connection) -> int:
    (valore,) = connessione.execute("PRAGMA user_version").fetchone()
    return int(valore)


def stato_compatibilita(versione_trovata: int) -> str:
    """Documentazione della versione portfolio."""
    if versione_trovata > SCHEMA_MASSIMO_SUPPORTATO:
        return "non supportato"
    if versione_trovata == SCHEMA_NON_NUMERATO:
        return "non numerato"
    if versione_trovata < SCHEMA_DATABASE:
        return "da migrare"
    return "allineato"


def verifica_compatibilita(connessione: sqlite3.Connection) -> int:
    """Documentazione della versione portfolio."""
    trovata = versione_schema(connessione)
    if trovata > SCHEMA_MASSIMO_SUPPORTATO:
        _registro.critical(
            "Schema del database non supportato: trovato %d, massimo supportato %d. "
            "Nessuna scrittura verra' eseguita.",
            trovata, SCHEMA_MASSIMO_SUPPORTATO,
        )
        raise ErroreSchemaNonSupportato(trovata, SCHEMA_MASSIMO_SUPPORTATO)
    return trovata


def _tabelle_presenti(connessione: sqlite3.Connection) -> set[str]:
    return {
        riga[0] for riga in connessione.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }


def _colonne_di(connessione: sqlite3.Connection, tabella: str) -> set[str]:
    return {riga[1] for riga in connessione.execute(f'PRAGMA table_info("{tabella}")')}


def forma_dello_schema_1(connessione: sqlite3.Connection) -> tuple[bool, list[str]]:
    """Documentazione della versione portfolio."""
    mancanti: list[str] = []
    presenti = _tabelle_presenti(connessione)
    for tabella in TABELLE_SCHEMA_1:
        if tabella not in presenti:
            mancanti.append(f"tabella assente: {tabella}")

    for tabella, colonne in COLONNE_SCHEMA_1.items():
        if tabella not in presenti:
            continue
        esistenti = _colonne_di(connessione, tabella)
        for colonna in colonne:
            if colonna not in esistenti:
                mancanti.append(f"colonna assente: {tabella}.{colonna}")

    return not mancanti, mancanti


def allinea_versione_schema(connessione: sqlite3.Connection) -> int:
    """Documentazione della versione portfolio."""
    trovata = verifica_compatibilita(connessione)

    if trovata == SCHEMA_DATABASE:
        return trovata

    va_bene, mancanti = forma_dello_schema_1(connessione)
    if not va_bene:


        _registro.error(
            "Schema del database incompleto: non viene numerato. Mancano: %s",
            "; ".join(mancanti),
        )
        return trovata

    _registro.info(
        "Schema del database: %s -> %d (%s)",
        "non numerato" if trovata == SCHEMA_NON_NUMERATO else trovata,
        SCHEMA_DATABASE,
        "prima numerazione, nessun dato modificato"
        if trovata == SCHEMA_NON_NUMERATO else "migrazione",
    )


    connessione.execute(f"PRAGMA user_version = {int(SCHEMA_DATABASE)}")
    connessione.commit()
    return SCHEMA_DATABASE
