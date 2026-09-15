"""Documentazione della versione portfolio."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config.impostazioni import cartella_dati_applicazione
from config.registro import logger
from data import backup as _backup

_registro = logger(__name__)

NOME_FILE_DATABASE = "control_room_demo.db"


NOME_FILE_BACKUP = _backup.NOME_FILE_BACKUP
NOME_FILE_BACKUP_IMPOSTAZIONI = _backup.NOME_FILE_BACKUP_IMPOSTAZIONI


class ErroreDati(Exception):
    """Documentazione della versione portfolio."""


def versione_schema_corrente() -> int:
    """Documentazione della versione portfolio."""
    percorso = percorso_database()
    if not percorso.is_file():
        return 0
    conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
    try:
        (valore,) = conn.execute("PRAGMA user_version").fetchone()
    finally:
        conn.close()
    return int(valore)


def percorso_database() -> Path:
    return cartella_dati_applicazione() / NOME_FILE_DATABASE


def ottieni_connessione() -> sqlite3.Connection:
    """Documentazione della versione portfolio."""
    connessione = sqlite3.connect(percorso_database())
    connessione.execute("PRAGMA foreign_keys = ON")
    return connessione


@contextmanager
def connessione(con_backup: bool = False):
    """Documentazione della versione portfolio."""
    from data.schema import verifica_compatibilita

    conn = sqlite3.connect(percorso_database())
    conn.execute("PRAGMA foreign_keys = ON")
    try:


        verifica_compatibilita(conn)
        yield conn
        conn.commit()
    except sqlite3.Error as errore:
        conn.rollback()


        _registro.error("Errore SQLite, transazione annullata: %s", errore, exc_info=True)
        raise ErroreDati(str(errore)) from errore
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


    if con_backup:
        esegui_backup()


def inizializza_database() -> None:
    """Documentazione della versione portfolio."""
    from data.cassaforte import crea_tabelle as crea_tabelle_cassaforte
    from data.chiavi import crea_tabelle as crea_tabelle_chiavi
    from data.consegne_radio import crea_tabella as crea_tabella_consegne_radio
    from data.gestione_radio import crea_tabelle as crea_tabelle_gestione_radio
    from data.oggetti_smarriti import crea_tabella as crea_tabella_oggetti_smarriti
    from data.operatori import crea_tabella as crea_tabella_operatori
    from data.passaggio_consegne import crea_tabella as crea_tabella_passaggio_consegne
    from data.rapporti_giornalieri import crea_tabella as crea_tabella_rapporti_giornalieri

    from data.schema import allinea_versione_schema, verifica_compatibilita

    _registro.info("Verifica dello schema del database: %s", percorso_database())
    connessione = ottieni_connessione()


    verifica_compatibilita(connessione)
    crea_tabella_passaggio_consegne(connessione)
    crea_tabelle_chiavi(connessione)
    crea_tabella_consegne_radio(connessione)
    crea_tabelle_gestione_radio(connessione)
    crea_tabella_oggetti_smarriti(connessione)
    crea_tabelle_cassaforte(connessione)
    crea_tabella_rapporti_giornalieri(connessione)
    crea_tabella_operatori(connessione)


    allinea_versione_schema(connessione)
    connessione.close()
    _registro.info("Schema del database verificato")


def esegui_backup() -> bool:
    """Documentazione della versione portfolio."""
    return _backup.esegui_backup()
