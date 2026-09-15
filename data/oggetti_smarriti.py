"""Documentazione della versione portfolio."""
from datetime import datetime


from data.comune import (
    giorni_trascorsi,
    normalizza,
    ordine_cronologico,
)
from data.database import connessione

STATO_IN_CUSTODIA = "in_custodia"
STATO_RICONSEGNATO = "riconsegnato"
STATO_SMALTITO = "smaltito"

STATI = (STATO_IN_CUSTODIA, STATO_RICONSEGNATO, STATO_SMALTITO)

FORMATO_DATA = "%d-%m-%Y"


_CAMPI = [
    "id",
    "data_ritiro", "ora_ritiro", "operatore_ritiro",
    "numero_sigillo", "descrizione", "proprietario", "ubicazione",
    "stato",
    "data_riconsegna", "ora_riconsegna", "riconsegnato_a",
    "operatore_riconsegna", "note_riconsegna",
    "data_smaltimento", "ora_smaltimento", "operatore_smaltimento",
    "note_smaltimento",
    "note_import",
]


_DATA_DELLO_STATO = {
    STATO_IN_CUSTODIA: "data_ritiro",
    STATO_RICONSEGNATO: "data_riconsegna",
    STATO_SMALTITO: "data_smaltimento",
}


def crea_tabella(connessione) -> None:
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS oggetti_smarriti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_ritiro TEXT NOT NULL,
            ora_ritiro TEXT,
            operatore_ritiro TEXT,
            numero_sigillo TEXT,
            descrizione TEXT NOT NULL,
            proprietario TEXT,
            ubicazione TEXT,
            stato TEXT NOT NULL
                CHECK (stato IN ('in_custodia', 'riconsegnato', 'smaltito')),
            data_riconsegna TEXT,
            ora_riconsegna TEXT,
            riconsegnato_a TEXT,
            operatore_riconsegna TEXT,
            note_riconsegna TEXT,
            data_smaltimento TEXT,
            ora_smaltimento TEXT,
            operatore_smaltimento TEXT,
            note_smaltimento TEXT,
            note_import TEXT
        )
        """
    )
    connessione.commit()


def _riga_a_dizionario(riga) -> dict:
    return dict(zip(_CAMPI, riga))


def _testo_ricercabile(oggetto: dict) -> str:
    """Documentazione della versione portfolio."""
    return " ".join(
        str(oggetto.get(campo) or "")
        for campo in ("descrizione", "proprietario", "numero_sigillo", "ubicazione")
    )


def registra_oggetto(
    data_ritiro: str,
    descrizione: str,
    ora_ritiro: str | None = None,
    operatore_ritiro: str | None = None,
    numero_sigillo: str | None = None,
    proprietario: str | None = None,
    ubicazione: str | None = None,
    note_import: str | None = None,
) -> int:
    """Documentazione della versione portfolio."""
    def pulisci(valore):
        return (valore or "").strip() or None

    with connessione(con_backup=True) as c:
        cursore = c.execute(
            """
            INSERT INTO oggetti_smarriti (
                data_ritiro, ora_ritiro, operatore_ritiro, numero_sigillo,
                descrizione, proprietario, ubicazione, stato, note_import
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data_ritiro.strip(), pulisci(ora_ritiro), pulisci(operatore_ritiro),
                pulisci(numero_sigillo), descrizione.strip(), pulisci(proprietario),
                pulisci(ubicazione), STATO_IN_CUSTODIA, pulisci(note_import),
            ),
        )
        id_oggetto = cursore.lastrowid
    return id_oggetto


def registra_riconsegna(
    id_oggetto: int,
    data_riconsegna: str,
    ora_riconsegna: str,
    riconsegnato_a: str | None = None,
    operatore_riconsegna: str | None = None,
    note_riconsegna: str | None = None,
) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            """
            UPDATE oggetti_smarriti
            SET stato = ?, data_riconsegna = ?, ora_riconsegna = ?,
                riconsegnato_a = ?, operatore_riconsegna = ?, note_riconsegna = ?
            WHERE id = ?
            """,
            (
                STATO_RICONSEGNATO, data_riconsegna.strip(), ora_riconsegna.strip(),
                (riconsegnato_a or "").strip() or None,
                (operatore_riconsegna or "").strip() or None,
                (note_riconsegna or "").strip() or None,
                id_oggetto,
            ),
        )


def registra_smaltimento(
    id_oggetto: int,
    data_smaltimento: str,
    ora_smaltimento: str,
    operatore_smaltimento: str | None = None,
    note_smaltimento: str | None = None,
) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            """
            UPDATE oggetti_smarriti
            SET stato = ?, data_smaltimento = ?, ora_smaltimento = ?,
                operatore_smaltimento = ?, note_smaltimento = ?
            WHERE id = ?
            """,
            (
                STATO_SMALTITO, data_smaltimento.strip(), ora_smaltimento.strip(),
                (operatore_smaltimento or "").strip() or None,
                (note_smaltimento or "").strip() or None,
                id_oggetto,
            ),
        )


def elimina_oggetto(id_oggetto: int) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute("DELETE FROM oggetti_smarriti WHERE id = ?", (id_oggetto,))


def oggetti_per_stato(stato: str, testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    colonna_data = _DATA_DELLO_STATO[stato]
    with connessione() as c:
        righe = c.execute(
            f"SELECT {', '.join(_CAMPI)} FROM oggetti_smarriti WHERE stato = ? "
            f"ORDER BY {ordine_cronologico(colonna_data)} DESC, id DESC",
            (stato,),
        ).fetchall()

    oggetti = [_riga_a_dizionario(r) for r in righe]
    query_normalizzata = normalizza(testo_ricerca)
    if not query_normalizzata:
        return oggetti
    return [o for o in oggetti if query_normalizzata in normalizza(_testo_ricercabile(o))]


def conta_in_custodia() -> int:
    with connessione() as c:
        numero = c.execute(
            "SELECT COUNT(*) FROM oggetti_smarriti WHERE stato = ?", (STATO_IN_CUSTODIA,)
        ).fetchone()[0]
    return numero


def storico_eventi(testo_ricerca: str = "", anno: int | None = None, mese: int | None = None,
                   limite: int | None = None, salta: int = 0) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(f"SELECT {', '.join(_CAMPI)} FROM oggetti_smarriti").fetchall()

    eventi = []
    for o in (_riga_a_dizionario(r) for r in righe):
        eventi.append({
            "data": o["data_ritiro"], "ora": o["ora_ritiro"] or "",
            "operazione": "PRESA IN CUSTODIA", "elemento": o["descrizione"],
            "persona": o["operatore_ritiro"] or "",
            "dettagli": f"Sigillo: {o['numero_sigillo'] or 'senza sigillo'}",
            "note": o["note_import"], "id_oggetto": o["id"],
        })
        if o["data_riconsegna"]:
            eventi.append({
                "data": o["data_riconsegna"], "ora": o["ora_riconsegna"] or "",
                "operazione": "RICONSEGNA", "elemento": o["descrizione"],
                "persona": o["operatore_riconsegna"] or "",
                "dettagli": f"A: {o['riconsegnato_a']}" if o["riconsegnato_a"] else "",
                "note": o["note_riconsegna"], "id_oggetto": o["id"],
            })
        if o["data_smaltimento"]:
            eventi.append({
                "data": o["data_smaltimento"], "ora": o["ora_smaltimento"] or "",
                "operazione": "SMALTIMENTO", "elemento": o["descrizione"],
                "persona": o["operatore_smaltimento"] or "",
                "dettagli": o["note_smaltimento"] or "",
                "note": o["note_smaltimento"], "id_oggetto": o["id"],
            })

    if anno is not None:
        eventi = [e for e in eventi if (e["data"] or "")[6:10] == str(anno)]
    if mese is not None:
        eventi = [e for e in eventi if (e["data"] or "")[3:5] == f"{mese:02d}"]

    query = normalizza(testo_ricerca)
    if query:
        eventi = [
            e for e in eventi
            if query in normalizza(" ".join(str(e.get(k) or "") for k in
                                            ("elemento", "persona", "operazione", "dettagli")))
        ]

    eventi.sort(key=lambda e: (f"{(e['data'] or '')[6:10]}{(e['data'] or '')[3:5]}"
                               f"{(e['data'] or '')[0:2]}{e['ora'] or '':>5}"), reverse=True)
    if limite is None:
        return eventi[salta:]
    return eventi[salta:salta + limite]


def periodi_storico() -> list[tuple[int, int]]:
    """Documentazione della versione portfolio."""
    periodi = set()
    for evento in storico_eventi():
        data = evento["data"] or ""
        if len(data) >= 10:
            periodi.add((int(data[6:10]), int(data[3:5])))
    return sorted(periodi, reverse=True)
