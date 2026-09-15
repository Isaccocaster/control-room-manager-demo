"""Documentazione della versione portfolio."""
import re
from datetime import datetime

from data.database import ErroreDati, connessione

FORMATO_CREATO_IL = "%d-%m-%Y %H:%M"


CATEGORIE_OPERATORE = ("sala_controllo", "mr", "gpg", "struttura", "manutenzione", "altro")

ETICHETTE_CATEGORIE_OPERATORE = {
    "sala_controllo": "Control Room",
    "mr": "MR",
    "gpg": "G.P.G.",
    "struttura": "Demo",
    "manutenzione": "Manutenzione",
    "altro": "Altro",
}


def crea_tabella(connessione) -> None:
    _migra_schema_precedente_se_vuoto(connessione)
    connessione.execute(
        f"""
        CREATE TABLE IF NOT EXISTS operatori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_canonico TEXT NOT NULL DEFAULT '',
            cognome_canonico TEXT NOT NULL,
            chiave_normalizzata TEXT NOT NULL UNIQUE,
            categoria_operatore TEXT NOT NULL
                CHECK (categoria_operatore IN {CATEGORIE_OPERATORE}),
            creato_il TEXT NOT NULL,
            attivo INTEGER NOT NULL DEFAULT 1 CHECK (attivo IN (0, 1))
        )
        """
    )
    _aggiungi_colonna_attivo_se_assente(connessione)
    connessione.commit()


def _aggiungi_colonna_attivo_se_assente(connessione) -> None:
    """Documentazione della versione portfolio."""
    colonne = {r[1] for r in connessione.execute("PRAGMA table_info(operatori)").fetchall()}
    if "attivo" not in colonne:
        connessione.execute("ALTER TABLE operatori ADD COLUMN attivo INTEGER NOT NULL DEFAULT 1")


def _migra_schema_precedente_se_vuoto(connessione) -> None:
    """Documentazione della versione portfolio."""
    colonne = {
        riga[1] for riga in connessione.execute("PRAGMA table_info(operatori)").fetchall()
    }
    if not colonne or "categoria_operatore" in colonne:
        return

    (conteggio,) = connessione.execute("SELECT COUNT(*) FROM operatori").fetchone()
    if conteggio:
        raise ErroreDati(
            f"La tabella 'operatori' esiste nello schema precedente e contiene {conteggio} "
            "righe: la migrazione automatica alla nuova struttura (nome/cognome separati, "
            "categoria) è stata bloccata per non perdere dati reali. Serve un intervento "
            "manuale prima di procedere."
        )
    connessione.execute("DROP TABLE operatori")


def _normalizza_singolo(testo: str) -> str:
    """Documentazione della versione portfolio."""
    return re.sub(r"\s+", " ", (testo or "").strip()).casefold()


def chiave_operatore(nome: str, cognome: str) -> str:
    """Documentazione della versione portfolio."""
    parti = [_normalizza_singolo(nome), _normalizza_singolo(cognome)]
    return " ".join(p for p in parti if p)


def nome_completo(operatore: dict) -> str:
    """Documentazione della versione portfolio."""
    return " ".join(p for p in (operatore["nome_canonico"], operatore["cognome_canonico"]) if p)


def _riga_a_dizionario(riga) -> dict:
    (id_, nome_canonico, cognome_canonico, chiave_normalizzata, categoria_operatore,
     creato_il, attivo) = riga
    return {
        "id": id_,
        "nome_canonico": nome_canonico,
        "cognome_canonico": cognome_canonico,
        "chiave_normalizzata": chiave_normalizzata,
        "categoria_operatore": categoria_operatore,
        "creato_il": creato_il,
        "attivo": bool(attivo),
    }


_CAMPI = "id, nome_canonico, cognome_canonico, chiave_normalizzata, categoria_operatore, creato_il, attivo"

STATI_OPERATORE = ("attivi", "disattivati", "tutti")


def _tabella_assente(errore: ErroreDati) -> bool:
    return "no such table" in str(errore) and "operatori" in str(errore)


def elenco_operatori(stato: str = "attivi") -> list[dict]:
    """Documentazione della versione portfolio."""
    if stato not in STATI_OPERATORE:
        raise ValueError(f"Stato non valido: {stato!r} (atteso uno tra {STATI_OPERATORE})")

    condizione = ""
    if stato == "attivi":
        condizione = "WHERE attivo = 1"
    elif stato == "disattivati":
        condizione = "WHERE attivo = 0"

    try:
        with connessione() as c:
            righe = c.execute(
                f"SELECT {_CAMPI} FROM operatori {condizione} "
                f"ORDER BY cognome_canonico, nome_canonico"
            ).fetchall()
    except ErroreDati as errore:
        if _tabella_assente(errore):
            return []
        raise
    return [_riga_a_dizionario(r) for r in righe]


def trova_operatore(nome_digitato: str, cognome_digitato: str = "") -> dict | None:
    """Documentazione della versione portfolio."""
    chiave = chiave_operatore(nome_digitato or "", cognome_digitato or "")
    if not chiave:
        return None
    try:
        with connessione() as c:
            riga = c.execute(
                f"SELECT {_CAMPI} FROM operatori WHERE chiave_normalizzata = ?", (chiave,)
            ).fetchone()
    except ErroreDati as errore:
        if _tabella_assente(errore):
            return None
        raise
    return _riga_a_dizionario(riga) if riga else None


def trova_operatore_per_nome_completo(testo_libero: str) -> dict | None:
    """Documentazione della versione portfolio."""
    return trova_operatore(testo_libero or "")


def registra_operatore(nome_canonico: str, cognome_canonico: str, categoria_operatore: str) -> dict:
    """Documentazione della versione portfolio."""
    nome_canonico = re.sub(r"\s+", " ", (nome_canonico or "").strip())
    cognome_canonico = re.sub(r"\s+", " ", (cognome_canonico or "").strip())
    if not cognome_canonico:
        raise ValueError("Il cognome dell'operatore è obbligatorio.")
    if categoria_operatore not in CATEGORIE_OPERATORE:
        raise ValueError(f"Categoria operatore non valida: {categoria_operatore!r}")

    esistente = trova_operatore(nome_canonico, cognome_canonico)
    if esistente is not None:
        return esistente

    chiave = chiave_operatore(nome_canonico, cognome_canonico)
    creato_il = datetime.now().strftime(FORMATO_CREATO_IL)
    with connessione(con_backup=True) as c:
        cursore = c.execute(
            "INSERT INTO operatori "
            "(nome_canonico, cognome_canonico, chiave_normalizzata, categoria_operatore, creato_il) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome_canonico, cognome_canonico, chiave, categoria_operatore, creato_il),
        )
        id_ = cursore.lastrowid
    return {
        "id": id_, "nome_canonico": nome_canonico, "cognome_canonico": cognome_canonico,
        "chiave_normalizzata": chiave, "categoria_operatore": categoria_operatore,
        "creato_il": creato_il, "attivo": True,
    }


def modifica_categoria(operatore_id: int, categoria_operatore: str) -> None:
    """Documentazione della versione portfolio."""
    if categoria_operatore not in CATEGORIE_OPERATORE:
        raise ValueError(f"Categoria operatore non valida: {categoria_operatore!r}")
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE operatori SET categoria_operatore = ? WHERE id = ?",
            (categoria_operatore, operatore_id),
        )


def modifica_nome_canonico(operatore_id: int, nome_canonico: str, cognome_canonico: str) -> None:
    """Documentazione della versione portfolio."""
    nome_canonico = re.sub(r"\s+", " ", (nome_canonico or "").strip())
    cognome_canonico = re.sub(r"\s+", " ", (cognome_canonico or "").strip())
    if not cognome_canonico:
        raise ValueError("Il cognome dell'operatore è obbligatorio.")
    chiave = chiave_operatore(nome_canonico, cognome_canonico)
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE operatori SET nome_canonico = ?, cognome_canonico = ?, chiave_normalizzata = ? "
            "WHERE id = ?",
            (nome_canonico, cognome_canonico, chiave, operatore_id),
        )


def _una_parola_inizia_con(testo: str, prefisso: str) -> bool:
    """Documentazione della versione portfolio."""
    return any(
        parola.startswith(prefisso)
        for parola in _normalizza_singolo(testo).split(" ")
        if parola
    )


def cerca_operatori(testo: str = "", categoria: str | None = None, stato: str = "attivi") -> list[dict]:
    """Documentazione della versione portfolio."""
    chiave = _normalizza_singolo(testo)
    risultati = elenco_operatori(stato=stato)
    if chiave:
        risultati = [
            o for o in risultati
            if (
                _una_parola_inizia_con(o["nome_canonico"], chiave)
                or _una_parola_inizia_con(o["cognome_canonico"], chiave)
                or chiave_operatore(o["nome_canonico"], o["cognome_canonico"]).startswith(chiave)
            )
        ]
    if categoria is not None:
        risultati = [o for o in risultati if o["categoria_operatore"] == categoria]
    return risultati


def disattiva_operatore(operatore_id: int) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute("UPDATE operatori SET attivo = 0 WHERE id = ?", (operatore_id,))


def riattiva_operatore(operatore_id: int) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute("UPDATE operatori SET attivo = 1 WHERE id = ?", (operatore_id,))
