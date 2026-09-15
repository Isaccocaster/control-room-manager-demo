"""Documentazione della versione portfolio."""
from data.comune import (
    mese_di_riferimento,
    normalizza,
    ordine_cronologico,
)
from data.database import connessione


_ORDINE_CRONOLOGICO = ordine_cronologico("data")


def crea_tabella(connessione) -> None:
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS consegne_radio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            radio_identificativo TEXT NOT NULL,
            ora_consegna TEXT NOT NULL,
            cognome_consegna TEXT NOT NULL,
            auricolare TEXT,
            ora_riconsegna TEXT,
            cognome_riconsegna TEXT,
            note TEXT,
            data_riconsegna TEXT
        )
        """
    )
    _aggiungi_colonne_mancanti(connessione)
    connessione.commit()


def _aggiungi_colonne_mancanti(connessione) -> None:
    """Documentazione della versione portfolio."""
    esistenti = {riga[1] for riga in connessione.execute("PRAGMA table_info(consegne_radio)")}
    if "data_riconsegna" not in esistenti:
        connessione.execute("ALTER TABLE consegne_radio ADD COLUMN data_riconsegna TEXT")


_CAMPI = (
    "id, data, radio_identificativo, ora_consegna, cognome_consegna, "
    "auricolare, ora_riconsegna, cognome_riconsegna, note, data_riconsegna"
)


def _riga_a_dizionario(riga) -> dict:
    (id_, data, radio_identificativo, ora_consegna, cognome_consegna,
     auricolare, ora_riconsegna, cognome_riconsegna, note, data_riconsegna) = riga
    return {
        "id": id_,
        "data": data,
        "radio_identificativo": radio_identificativo,
        "ora_consegna": ora_consegna,
        "cognome_consegna": cognome_consegna,
        "auricolare": auricolare,
        "ora_riconsegna": ora_riconsegna,
        "cognome_riconsegna": cognome_riconsegna,
        "note": note,
        "data_riconsegna": data_riconsegna,
    }


def registra_consegna(
    data: str, radio_identificativo: str, ora_consegna: str, cognome_consegna: str,
    auricolare: str = "No", note: str = "",
) -> None:
    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO consegne_radio "
            "(data, radio_identificativo, ora_consegna, cognome_consegna, auricolare, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (data, radio_identificativo.strip(), ora_consegna.strip(), cognome_consegna.strip(),
             auricolare, note.strip()),
        )


def registra_riconsegna(id_consegna: int, ora_riconsegna: str, cognome_riconsegna: str,
                        data_riconsegna: str | None = None) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE consegne_radio SET ora_riconsegna = ?, cognome_riconsegna = ?, "
            "data_riconsegna = ? WHERE id = ?",
            (ora_riconsegna.strip(), cognome_riconsegna.strip(),
             (data_riconsegna or "").strip() or None, id_consegna),
        )


def radio_fuori() -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"SELECT {_CAMPI} FROM consegne_radio "
            f"WHERE ora_riconsegna IS NULL OR ora_riconsegna = '' "
            f"ORDER BY {_ORDINE_CRONOLOGICO}, id"
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def conta_radio_fuori() -> int:
    with connessione() as c:
        numero = c.execute(
            "SELECT COUNT(*) FROM consegne_radio WHERE ora_riconsegna IS NULL OR ora_riconsegna = ''"
        ).fetchone()[0]
    return numero


def consegne_del_mese(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"SELECT {_CAMPI} FROM consegne_radio "
            f"WHERE substr(data, 4, 2) = ? AND substr(data, 7, 4) = ? "
            f"ORDER BY {_ORDINE_CRONOLOGICO}, id",
            (f"{mese:02d}", str(anno)),
        ).fetchall()
    return [_riga_a_dizionario(r) for r in righe]


def storico_movimentazioni(testo_ricerca: str = "", anno: int | None = None,
                           mese: int | None = None, limite: int | None = None,
                           salta: int = 0) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(f"SELECT {_CAMPI} FROM consegne_radio").fetchall()

    eventi = []
    for consegna in (_riga_a_dizionario(r) for r in righe):
        eventi.append({
            "data": consegna["data"],
            "ora": consegna["ora_consegna"],
            "operazione": "CONSEGNA",
            "elemento": consegna["radio_identificativo"],
            "persona": consegna["cognome_consegna"],
            "dettagli": f"Auricolare: {consegna['auricolare'] or 'No'}",
            "note": consegna["note"],
            "id_consegna": consegna["id"],
        })
        if consegna["ora_riconsegna"]:
            eventi.append({


                "data": consegna["data_riconsegna"] or consegna["data"],
                "data_incerta": consegna["data_riconsegna"] is None,
                "ora": consegna["ora_riconsegna"],
                "operazione": "RIENTRO",
                "elemento": consegna["radio_identificativo"],
                "persona": consegna["cognome_riconsegna"],
                "dettagli": "" if consegna["data_riconsegna"] else "data del rientro non registrata",
                "note": consegna["note"],
                "id_consegna": consegna["id"],
            })

    eventi = _filtra_eventi(eventi, testo_ricerca, anno, mese)
    eventi.sort(key=_chiave_cronologica, reverse=True)
    if limite is None:
        return eventi[salta:]
    return eventi[salta:salta + limite]


def conta_storico(testo_ricerca: str = "", anno: int | None = None,
                  mese: int | None = None) -> int:
    return len(storico_movimentazioni(testo_ricerca, anno, mese))


def _chiave_cronologica(evento: dict) -> str:
    data = evento["data"] or ""
    anno_mese_giorno = f"{data[6:10]}{data[3:5]}{data[0:2]}"
    return f"{anno_mese_giorno}{(evento['ora'] or ''):>5}"


def _filtra_eventi(eventi: list[dict], testo_ricerca: str, anno: int | None,
                   mese: int | None) -> list[dict]:
    if anno is not None:
        eventi = [e for e in eventi if (e["data"] or "")[6:10] == str(anno)]
    if mese is not None:
        eventi = [e for e in eventi if (e["data"] or "")[3:5] == f"{mese:02d}"]
    query = normalizza(testo_ricerca)
    if not query:
        return eventi
    return [
        e for e in eventi
        if query in normalizza(" ".join(str(e.get(k) or "") for k in
                                        ("elemento", "persona", "operazione", "note")))
    ]


def periodi_storico() -> list[tuple[int, int]]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            "SELECT DISTINCT substr(data, 7, 4), substr(data, 4, 2) FROM consegne_radio "
            "ORDER BY 1 DESC, 2 DESC"
        ).fetchall()
    return [(int(a), int(m)) for a, m in righe if a and m]


def cicli_consegne(testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(f"SELECT {_CAMPI} FROM consegne_radio").fetchall()

    cicli = []
    for consegna in (_riga_a_dizionario(r) for r in righe):
        cicli.append({
            "elemento": consegna["radio_identificativo"],
            "uscita_data": consegna["data"], "uscita_ora": consegna["ora_consegna"],
            "uscita_persona": consegna["cognome_consegna"],
            "rientro_data": consegna["data_riconsegna"], "rientro_ora": consegna["ora_riconsegna"],
            "rientro_persona": consegna["cognome_riconsegna"],
            "stato": "Rientrata" if consegna["ora_riconsegna"] else "Ancora fuori",
            "note": consegna["note"],
        })

    cicli.sort(key=lambda cc: (
        f"{(cc['uscita_data'] or '')[6:10]}{(cc['uscita_data'] or '')[3:5]}"
        f"{(cc['uscita_data'] or '')[0:2]}{(cc['uscita_ora'] or ''):>5}"
    ), reverse=True)

    query = normalizza(testo_ricerca)
    if not query:
        return cicli
    return [
        cc for cc in cicli
        if query in normalizza(" ".join(str(cc.get(k) or "") for k in (
            "elemento", "uscita_persona", "rientro_persona", "note")))
    ]
