"""Documentazione della versione portfolio."""
from datetime import date, datetime

from data.comune import mese_di_riferimento, ordine_cronologico
from data.database import connessione

FORMATO_DATA_ORA = "%d.%m.%Y %H:%M"


_ORDINE_CRONOLOGICO = ordine_cronologico("creato_il", con_ora=True)


_ORDINE = f"fissato DESC, {_ORDINE_CRONOLOGICO} DESC, id DESC"

_CAMPI = "id, testo, creato_il, fissato, archiviato_il, fissato_il"


def crea_tabella(connessione) -> None:
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS passaggio_consegne (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testo TEXT NOT NULL,
            creato_il TEXT NOT NULL,
            fissato INTEGER NOT NULL DEFAULT 0,
            archiviato_il TEXT,
            fissato_il TEXT
        )
        """
    )
    _aggiungi_colonne_mancanti(connessione)
    connessione.commit()


def _aggiungi_colonne_mancanti(connessione) -> None:
    """Documentazione della versione portfolio."""
    esistenti = {riga[1] for riga in connessione.execute("PRAGMA table_info(passaggio_consegne)")}
    if "fissato" not in esistenti:
        connessione.execute(
            "ALTER TABLE passaggio_consegne ADD COLUMN fissato INTEGER NOT NULL DEFAULT 0"
        )
    if "archiviato_il" not in esistenti:
        connessione.execute("ALTER TABLE passaggio_consegne ADD COLUMN archiviato_il TEXT")
    if "fissato_il" not in esistenti:
        connessione.execute("ALTER TABLE passaggio_consegne ADD COLUMN fissato_il TEXT")


def _riga_a_dizionario(riga) -> dict:
    id_, testo, creato_il, fissato, archiviato_il, fissato_il = riga
    return {
        "id": id_,
        "testo": testo,
        "creato_il": creato_il,
        "fissato": bool(fissato),
        "archiviato_il": archiviato_il,
        "archiviata": archiviato_il is not None,
        "fissato_il": fissato_il,
    }


def ottieni_comunicazioni() -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"SELECT {_CAMPI} FROM passaggio_consegne WHERE archiviato_il IS NULL ORDER BY {_ORDINE}"
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def storico_comunicazioni() -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"SELECT {_CAMPI} FROM passaggio_consegne ORDER BY {_ORDINE}"
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def comunicazioni_del_mese(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"SELECT {_CAMPI} FROM passaggio_consegne "
            f"WHERE substr(creato_il, 7, 4) = ? AND substr(creato_il, 4, 2) = ? "
            f"ORDER BY {_ORDINE}",
            (str(anno), f"{mese:02d}"),
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def storico_visibile(oggi: date | None = None) -> list[dict]:
    """Documentazione della versione portfolio."""
    riferimento = oggi or date.today()
    with connessione() as c:
        righe = c.execute(
            f"SELECT {_CAMPI} FROM passaggio_consegne "
            f"WHERE archiviato_il IS NULL "
            f"   OR (substr(creato_il, 7, 4) = ? AND substr(creato_il, 4, 2) = ?) "
            f"ORDER BY {_ORDINE}",
            (str(riferimento.year), f"{riferimento.month:02d}"),
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def comunicazione(id_comunicazione: int) -> dict | None:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        riga = c.execute(
            f"SELECT {_CAMPI} FROM passaggio_consegne WHERE id = ?", (id_comunicazione,)
        ).fetchone()
    return _riga_a_dizionario(riga) if riga else None


def conteggi_attivi() -> dict:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        fissate, normali = c.execute(
            "SELECT COALESCE(SUM(fissato), 0), COALESCE(SUM(1 - fissato), 0) "
            "FROM passaggio_consegne WHERE archiviato_il IS NULL"
        ).fetchone()
    return {"fissate": fissate, "normali": normali}


def aggiungi_comunicazione(testo: str) -> None:
    testo_pulito = testo.strip()
    if not testo_pulito:
        return

    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO passaggio_consegne (testo, creato_il, fissato) VALUES (?, ?, 0)",
            (testo_pulito, datetime.now().strftime(FORMATO_DATA_ORA)),
        )


def modifica_comunicazione(id_comunicazione: int, nuovo_testo: str) -> None:
    """Documentazione della versione portfolio."""
    testo_pulito = nuovo_testo.strip()
    if not testo_pulito:
        return

    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE passaggio_consegne SET testo = ? WHERE id = ?",
            (testo_pulito, id_comunicazione),
        )


def archivia_comunicazione(id_comunicazione: int) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE passaggio_consegne SET archiviato_il = ? WHERE id = ? AND archiviato_il IS NULL",
            (datetime.now().strftime(FORMATO_DATA_ORA), id_comunicazione),
        )


def imposta_fissato(id_comunicazione: int, fissato: bool) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE passaggio_consegne SET fissato = ?, fissato_il = ? WHERE id = ?",
            (
                1 if fissato else 0,
                datetime.now().strftime(FORMATO_DATA_ORA) if fissato else None,
                id_comunicazione,
            ),
        )
