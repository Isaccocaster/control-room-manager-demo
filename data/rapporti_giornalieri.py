"""Documentazione della versione portfolio."""
from pathlib import Path

from data.comune import ordine_cronologico
from data.database import connessione

STATO_APERTO = "aperto"
STATO_CHIUSO = "chiuso"

_CAMPI = [
    "id", "data_turno", "operatore_nome", "operatore_cognome",
    "ora_inizio", "ora_fine", "nome_file", "cartella_corrente",
    "stato", "data_creazione", "data_ultima_modifica", "operatore_id",
]

MESI_ITALIANO = [
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]


_ORDINE_CRONOLOGICO = ordine_cronologico("data_turno")


def crea_tabella(connessione) -> None:
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS rapporti_giornalieri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_turno TEXT NOT NULL,
            operatore_nome TEXT NOT NULL,
            operatore_cognome TEXT NOT NULL,
            ora_inizio TEXT NOT NULL,
            ora_fine TEXT NOT NULL,
            nome_file TEXT NOT NULL,
            cartella_corrente TEXT NOT NULL,
            stato TEXT NOT NULL CHECK (stato IN ('aperto', 'chiuso')),
            data_creazione TEXT NOT NULL,
            data_ultima_modifica TEXT,
            UNIQUE (data_turno, operatore_nome, operatore_cognome, ora_inizio, ora_fine)
        )
        """
    )
    _aggiungi_colonna_operatore_id_se_assente(connessione)
    connessione.commit()


def _aggiungi_colonna_operatore_id_se_assente(connessione) -> None:
    """Documentazione della versione portfolio."""
    colonne = {r[1] for r in connessione.execute("PRAGMA table_info(rapporti_giornalieri)").fetchall()}
    if "operatore_id" not in colonne:
        connessione.execute("ALTER TABLE rapporti_giornalieri ADD COLUMN operatore_id INTEGER")


def _riga_a_dizionario(riga) -> dict:
    return dict(zip(_CAMPI, riga))


def formatta_nome_file(data_turno: str, ora_inizio: str, ora_fine: str, nome: str, cognome: str) -> str:
    """Documentazione della versione portfolio."""
    data_punti = data_turno.strip().replace("-", ".")
    inizio_punti = ora_inizio.strip().replace(":", ".")
    fine_punti = ora_fine.strip().replace(":", ".")
    return f"{data_punti}  {inizio_punti} - {fine_punti}  {nome.strip()} {cognome.strip()}.docx"


def mese_italiano(mese: int) -> str:
    return MESI_ITALIANO[mese - 1]


def cartella_archivio(cartella_rapporti: str, data_turno: str) -> Path:
    """Documentazione della versione portfolio."""
    giorno, mese, anno = data_turno.strip().split("-")
    return Path(cartella_rapporti) / "Archivio" / anno / mese_italiano(int(mese))


def rapporto_esistente(
    data_turno: str, operatore_nome: str, operatore_cognome: str, ora_inizio: str, ora_fine: str,
    escludi_id: int | None = None,
) -> bool:
    """Documentazione della versione portfolio."""
    query = (
        "SELECT 1 FROM rapporti_giornalieri "
        "WHERE data_turno = ? AND operatore_nome = ? AND operatore_cognome = ? "
        "AND ora_inizio = ? AND ora_fine = ?"
    )
    parametri = [
        data_turno.strip(), operatore_nome.strip(), operatore_cognome.strip(),
        ora_inizio.strip(), ora_fine.strip(),
    ]
    if escludi_id is not None:
        query += " AND id != ?"
        parametri.append(escludi_id)

    with connessione() as c:
        riga = c.execute(query, parametri).fetchone()
    return riga is not None


def crea_rapporto(
    data_turno: str, operatore_nome: str, operatore_cognome: str,
    ora_inizio: str, ora_fine: str, nome_file: str, cartella_corrente: str,
    data_creazione: str, operatore_id: int | None = None,
) -> int:
    """Documentazione della versione portfolio."""
    if rapporto_esistente(data_turno, operatore_nome, operatore_cognome, ora_inizio, ora_fine):
        raise ValueError("Esiste già un rapporto per questa data, operatore e turno.")

    with connessione(con_backup=True) as c:
        cursore = c.execute(
            """
            INSERT INTO rapporti_giornalieri (
                data_turno, operatore_nome, operatore_cognome, ora_inizio, ora_fine,
                nome_file, cartella_corrente, stato, data_creazione, operatore_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data_turno.strip(), operatore_nome.strip(), operatore_cognome.strip(),
                ora_inizio.strip(), ora_fine.strip(), nome_file, cartella_corrente,
                STATO_APERTO, data_creazione, operatore_id,
            ),
        )
        id_rapporto = cursore.lastrowid
    return id_rapporto


def rapporti_del_giorno(data_turno: str) -> list[dict]:
    with connessione() as c:
        righe = c.execute(
            f"SELECT {', '.join(_CAMPI)} FROM rapporti_giornalieri WHERE data_turno = ? "
            f"ORDER BY ora_inizio, id",
            (data_turno.strip(),),
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def tutti_i_rapporti(testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"SELECT {', '.join(_CAMPI)} FROM rapporti_giornalieri "
            f"ORDER BY {_ORDINE_CRONOLOGICO} DESC, ora_inizio DESC, id DESC"
        ).fetchall()

    rapporti = [_riga_a_dizionario(r) for r in righe]
    query = testo_ricerca.strip().lower()
    if not query:
        return rapporti
    return [
        r for r in rapporti
        if query in " ".join([
            r["data_turno"], r["operatore_nome"], r["operatore_cognome"],
            r["ora_inizio"], r["ora_fine"],
        ]).lower()
    ]


def rapporti_aperti_di(data_turno: str) -> list[dict]:
    """Documentazione della versione portfolio."""
    return [r for r in rapporti_del_giorno(data_turno) if r["stato"] == STATO_APERTO]


def conta_rapporti_aperti() -> int:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        (numero,) = c.execute(
            "SELECT COUNT(*) FROM rapporti_giornalieri WHERE stato = ?", (STATO_APERTO,)
        ).fetchone()
    return numero


def segna_chiuso(id_rapporto: int, data_ultima_modifica: str) -> None:
    _aggiorna_stato(id_rapporto, STATO_CHIUSO, data_ultima_modifica)


def segna_aperto(id_rapporto: int, data_ultima_modifica: str) -> None:
    _aggiorna_stato(id_rapporto, STATO_APERTO, data_ultima_modifica)


def _aggiorna_stato(id_rapporto: int, stato: str, data_ultima_modifica: str) -> None:
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE rapporti_giornalieri SET stato = ?, data_ultima_modifica = ? WHERE id = ?",
            (stato, data_ultima_modifica, id_rapporto),
        )


def modifica_dati_operatore(
    id_rapporto: int, operatore_nome: str, operatore_cognome: str,
    ora_inizio: str, ora_fine: str, nome_file: str, data_ultima_modifica: str,
    operatore_id: int | None = None,
) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            """
            UPDATE rapporti_giornalieri
            SET operatore_nome = ?, operatore_cognome = ?, ora_inizio = ?, ora_fine = ?,
                nome_file = ?, data_ultima_modifica = ?, operatore_id = ?
            WHERE id = ?
            """,
            (
                operatore_nome.strip(), operatore_cognome.strip(),
                ora_inizio.strip(), ora_fine.strip(), nome_file, data_ultima_modifica,
                operatore_id, id_rapporto,
            ),
        )


def rapporto_e_archiviato(rapporto: dict, cartella_rapporti: str) -> bool:
    """Documentazione della versione portfolio."""
    if not cartella_rapporti:
        return False
    base_archivio = str(Path(cartella_rapporti) / "Archivio")
    return str(Path(rapporto["cartella_corrente"])).startswith(base_archivio)


def rapporti_non_archiviati(cartella_rapporti: str, testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    return [r for r in tutti_i_rapporti(testo_ricerca) if not rapporto_e_archiviato(r, cartella_rapporti)]


def tutti_i_rapporti_archiviati(cartella_rapporti: str) -> list[dict]:
    """Documentazione della versione portfolio."""
    return [r for r in tutti_i_rapporti() if rapporto_e_archiviato(r, cartella_rapporti)]


def anni_mesi_archiviati(cartella_rapporti: str) -> list[tuple[int, int]]:
    """Documentazione della versione portfolio."""
    coppie = set()
    for rapporto in tutti_i_rapporti():
        if not rapporto_e_archiviato(rapporto, cartella_rapporti):
            continue
        _, mese, anno = rapporto["data_turno"].split("-")
        coppie.add((int(anno), int(mese)))
    return sorted(coppie, reverse=True)


def rapporti_archiviati_di(cartella_rapporti: str, anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    risultato = []
    for rapporto in tutti_i_rapporti():
        if not rapporto_e_archiviato(rapporto, cartella_rapporti):
            continue
        _, mese_rapporto, anno_rapporto = rapporto["data_turno"].split("-")
        if int(anno_rapporto) == anno and int(mese_rapporto) == mese:
            risultato.append(rapporto)
    return risultato


def aggiorna_cartella(id_rapporto: int, nuova_cartella: str) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE rapporti_giornalieri SET cartella_corrente = ? WHERE id = ?",
            (nuova_cartella, id_rapporto),
        )
