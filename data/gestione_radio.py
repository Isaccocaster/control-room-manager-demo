"""Documentazione della versione portfolio."""
from datetime import datetime

from data.comune import normalizza, ordine_cronologico
from data.database import connessione

STATI_RADIO = ("disponibile", "assegnata", "guasta", "in_riparazione", "persa")
STATI_AURICOLARE = ("funzionante", "guasto")


TIPI_APPARATO_RADIO = ("BASE DEMO", "RIPETITORE DEMO", "RADIO DEMO A", "RADIO DEMO B")


CAMPI_TRACCIATI = (
    "tipo_apparato", "selettiva", "matricola", "custodito_da", "assegnata_a", "stato", "note",
)


def crea_tabelle(connessione) -> None:
    connessione.execute(
        f"""
        CREATE TABLE IF NOT EXISTS radio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_apparato TEXT NOT NULL,
            selettiva TEXT,
            matricola TEXT UNIQUE,
            custodito_da TEXT,
            assegnata_a TEXT,
            stato TEXT NOT NULL DEFAULT 'disponibile'
                CHECK (stato IN {STATI_RADIO}),
            note TEXT
        )
        """
    )
    connessione.execute(
        f"""
        CREATE TABLE IF NOT EXISTS auricolari_conteggio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modello TEXT NOT NULL,
            stato TEXT NOT NULL CHECK (stato IN {STATI_AURICOLARE}),
            quantita INTEGER NOT NULL DEFAULT 0,
            UNIQUE (modello, stato)
        )
        """
    )


    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS radio_eventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            radio_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            ora TEXT NOT NULL,
            campo TEXT NOT NULL,
            valore_precedente TEXT,
            valore_nuovo TEXT
        )
        """
    )
    connessione.commit()


def _registra_evento(c, radio_id: int, campo: str, valore_precedente, valore_nuovo) -> None:
    adesso = datetime.now()
    c.execute(
        "INSERT INTO radio_eventi (radio_id, data, ora, campo, valore_precedente, valore_nuovo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (radio_id, adesso.strftime("%d-%m-%Y"), adesso.strftime("%H:%M"), campo,
         valore_precedente, valore_nuovo),
    )


def _riepilogo_radio(radio: dict) -> str:
    parti = [radio["tipo_apparato"]]
    if radio.get("selettiva"):
        parti.append(f"selettiva {radio['selettiva']}")
    if radio.get("matricola"):
        parti.append(f"matricola {radio['matricola']}")
    return " — ".join(parti)


def _riga_a_dizionario(riga) -> dict:
    (id_, tipo_apparato, selettiva, matricola, custodito_da, assegnata_a, stato, note) = riga
    return {
        "id": id_,
        "tipo_apparato": tipo_apparato,
        "selettiva": selettiva,
        "matricola": matricola,
        "custodito_da": custodito_da,
        "assegnata_a": assegnata_a,
        "stato": stato,
        "note": note,
    }


_CAMPI = "id, tipo_apparato, selettiva, matricola, custodito_da, assegnata_a, stato, note"


def stato_effettivo(radio: dict) -> str:
    """Documentazione della versione portfolio."""
    if radio["stato"] in ("guasta", "in_riparazione", "persa"):
        return radio["stato"]
    return "assegnata" if radio.get("assegnata_a") else "disponibile"


def e_af_impianti(radio: dict) -> bool:
    """Documentazione della versione portfolio."""
    return normalizza(radio.get("custodito_da") or "").startswith("a.f.")


def cerca_radio(testo_ricerca: str = "", stato: str | None = None,
                tipo_apparato: str | None = None) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(f"SELECT {_CAMPI} FROM radio ORDER BY tipo_apparato, id").fetchall()

    risultati = [_riga_a_dizionario(r) for r in righe]

    if stato is not None:
        risultati = [r for r in risultati if stato_effettivo(r) == stato]
    if tipo_apparato is not None:
        risultati = [r for r in risultati if r["tipo_apparato"] == tipo_apparato]

    query = normalizza(testo_ricerca)
    if query:
        risultati = [
            r for r in risultati
            if query in normalizza(" ".join(str(r.get(k) or "") for k in
                                            ("selettiva", "matricola", "custodito_da",
                                             "assegnata_a", "note")))
        ]
    return risultati


def tutte_le_radio() -> list[dict]:
    """Documentazione della versione portfolio."""
    return cerca_radio()


def raggruppa_per_tipo(radio: list[dict]) -> list[tuple[str, list[dict]]]:
    """Documentazione della versione portfolio."""
    gruppi: dict[str, list[dict]] = {}
    for r in radio:
        gruppi.setdefault(r["tipo_apparato"], []).append(r)
    return list(gruppi.items())


def aggiungi_radio(tipo_apparato: str, selettiva: str | None = None, matricola: str | None = None,
                   custodito_da: str | None = None, assegnata_a: str | None = None,
                   stato: str = "disponibile", note: str | None = None) -> int:
    with connessione(con_backup=True) as c:
        valori = (
            tipo_apparato.strip(),
            (selettiva or "").strip() or None,
            (matricola or "").strip() or None,
            (custodito_da or "").strip() or None,
            (assegnata_a or "").strip() or None,
            stato,
            (note or "").strip() or None,
        )
        cursore = c.execute(
            "INSERT INTO radio (tipo_apparato, selettiva, matricola, custodito_da, "
            "assegnata_a, stato, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            valori,
        )
        id_radio = cursore.lastrowid
        nuovo = dict(zip(CAMPI_TRACCIATI, valori))
        _registra_evento(c, id_radio, "creazione", None, _riepilogo_radio(nuovo))
        return id_radio


def modifica_radio(id_radio: int, tipo_apparato: str, selettiva: str | None = None,
                   matricola: str | None = None, custodito_da: str | None = None,
                   assegnata_a: str | None = None, stato: str = "disponibile",
                   note: str | None = None) -> None:
    nuovo = {
        "tipo_apparato": tipo_apparato.strip(),
        "selettiva": (selettiva or "").strip() or None,
        "matricola": (matricola or "").strip() or None,
        "custodito_da": (custodito_da or "").strip() or None,
        "assegnata_a": (assegnata_a or "").strip() or None,
        "stato": stato,
        "note": (note or "").strip() or None,
    }
    with connessione(con_backup=True) as c:
        riga = c.execute(f"SELECT {_CAMPI} FROM radio WHERE id = ?", (id_radio,)).fetchone()
        if riga is None:
            return
        precedente = _riga_a_dizionario(riga)

        c.execute(
            "UPDATE radio SET tipo_apparato = ?, selettiva = ?, matricola = ?, "
            "custodito_da = ?, assegnata_a = ?, stato = ?, note = ? WHERE id = ?",
            (nuovo["tipo_apparato"], nuovo["selettiva"], nuovo["matricola"], nuovo["custodito_da"],
             nuovo["assegnata_a"], nuovo["stato"], nuovo["note"], id_radio),
        )


        for campo in CAMPI_TRACCIATI:
            if precedente[campo] != nuovo[campo]:
                _registra_evento(c, id_radio, campo, precedente[campo], nuovo[campo])


def cambia_stato_radio(id_radio: int, stato: str) -> None:
    with connessione(con_backup=True) as c:
        riga = c.execute("SELECT stato FROM radio WHERE id = ?", (id_radio,)).fetchone()
        precedente = riga[0] if riga else None

        c.execute("UPDATE radio SET stato = ? WHERE id = ?", (stato, id_radio))

        if precedente is not None and precedente != stato:
            _registra_evento(c, id_radio, "stato", precedente, stato)


def rimuovi_radio(id_radio: int) -> None:
    with connessione(con_backup=True) as c:
        riga = c.execute(f"SELECT {_CAMPI} FROM radio WHERE id = ?", (id_radio,)).fetchone()
        if riga is not None:
            radio = _riga_a_dizionario(riga)
            _registra_evento(c, id_radio, "rimozione", _riepilogo_radio(radio), None)

        c.execute("DELETE FROM radio WHERE id = ?", (id_radio,))


def conteggi_per_stato() -> dict[str, int]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(f"SELECT {_CAMPI} FROM radio").fetchall()
    conteggi = {stato: 0 for stato in STATI_RADIO}
    for r in (_riga_a_dizionario(riga) for riga in righe):
        conteggi[stato_effettivo(r)] += 1
    return conteggi


def conteggi_per_tipo() -> dict[str, int]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            "SELECT tipo_apparato, COUNT(*) FROM radio GROUP BY tipo_apparato ORDER BY tipo_apparato"
        ).fetchall()
    return dict(righe)


def elenco_auricolari() -> list[dict]:
    with connessione() as c:
        righe = c.execute(
            "SELECT modello, stato, quantita FROM auricolari_conteggio ORDER BY modello, stato"
        ).fetchall()
    return [{"modello": m, "stato": s, "quantita": q} for m, s, q in righe]


def imposta_conteggio_auricolare(modello: str, stato: str, quantita: int) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO auricolari_conteggio (modello, stato, quantita) VALUES (?, ?, ?) "
            "ON CONFLICT (modello, stato) DO UPDATE SET quantita = excluded.quantita",
            (modello.strip(), stato, quantita),
        )


def eventi_radio(testo_ricerca: str = "", anno: int | None = None,
                 mese: int | None = None) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"""
            SELECT ev.id, ev.radio_id, ev.data, ev.ora, ev.campo,
                   ev.valore_precedente, ev.valore_nuovo, r.tipo_apparato, r.selettiva
            FROM radio_eventi ev
            LEFT JOIN radio r ON r.id = ev.radio_id
            ORDER BY {ordine_cronologico('ev.data')} DESC, ev.ora DESC, ev.id DESC
            """
        ).fetchall()

    eventi = [
        {
            "id": id_, "radio_id": radio_id, "data": data, "ora": ora, "campo": campo,
            "valore_precedente": vp, "valore_nuovo": vn,
            "tipo_apparato": tipo_apparato, "selettiva": selettiva,
        }
        for id_, radio_id, data, ora, campo, vp, vn, tipo_apparato, selettiva in righe
    ]

    if anno is not None:
        eventi = [e for e in eventi if e["data"][6:10] == str(anno)]
    if mese is not None:
        eventi = [e for e in eventi if e["data"][3:5] == f"{mese:02d}"]

    query = normalizza(testo_ricerca)
    if not query:
        return eventi
    return [
        e for e in eventi
        if query in normalizza(" ".join(str(e.get(k) or "") for k in (
            "campo", "valore_precedente", "valore_nuovo", "tipo_apparato", "selettiva")))
    ]


def periodi_eventi_radio() -> list[tuple[int, int]]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            "SELECT DISTINCT substr(data, 7, 4), substr(data, 4, 2) FROM radio_eventi "
            "ORDER BY 1 DESC, 2 DESC"
        ).fetchall()
    return [(int(a), int(m)) for a, m in righe if a and m]
