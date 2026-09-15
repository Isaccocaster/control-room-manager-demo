"""Documentazione della versione portfolio."""


from data.comune import (
    data_valida,
    giorni_trascorsi,
    normalizza,
    ordine_cronologico,
)
from data.database import connessione

CATEGORIE = ("chiavi", "fondo_cassa", "valori", "documenti", "altro")

ETICHETTE_CATEGORIE = {
    "chiavi": "Chiavi",
    "fondo_cassa": "Fondo cassa",
    "valori": "Valori",
    "documenti": "Documenti",
    "altro": "Altro",
}

TIPO_DEPOSITO = "deposito"
TIPO_USCITA = "uscita"
TIPO_RIENTRO = "rientro"
TIPI = (TIPO_DEPOSITO, TIPO_USCITA, TIPO_RIENTRO)

FORMATO_DATA = "%d-%m-%Y"

_CAMPI_MOVIMENTO = [
    "id", "operazione_id", "elemento_id", "tipo", "data", "ora",
    "persona", "numero_busta", "data_busta", "note",
]


def crea_tabelle(connessione) -> None:
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS cassaforte_elementi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descrizione TEXT NOT NULL,
            categoria TEXT NOT NULL
                CHECK (categoria IN ('chiavi', 'fondo_cassa', 'valori', 'documenti', 'altro')),
            note TEXT
        )
        """
    )
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS cassaforte_movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operazione_id INTEGER NOT NULL,
            elemento_id INTEGER NOT NULL REFERENCES cassaforte_elementi(id),
            tipo TEXT NOT NULL CHECK (tipo IN ('deposito', 'uscita', 'rientro')),
            data TEXT,
            ora TEXT,
            persona TEXT,
            numero_busta TEXT,
            data_busta TEXT,
            note TEXT,
            CHECK (tipo = 'deposito' OR (data IS NOT NULL AND persona IS NOT NULL))
        )
        """
    )
    connessione.commit()


def _pulisci(valore):
    return (valore or "").strip() or None


def aggiungi_elemento(descrizione: str, categoria: str, note: str | None = None) -> int:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        cursore = c.execute(
            "INSERT INTO cassaforte_elementi (descrizione, categoria, note) VALUES (?, ?, ?)",
            (descrizione.strip(), categoria, _pulisci(note)),
        )
        id_elemento = cursore.lastrowid
    return id_elemento


def _prossima_operazione(connessione) -> int:
    massimo = connessione.execute(
        "SELECT COALESCE(MAX(operazione_id), 0) FROM cassaforte_movimenti"
    ).fetchone()[0]
    return massimo + 1


def _inserisci_movimenti(righe) -> int:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        operazione_id = _prossima_operazione(c)
        for riga in righe:
            c.execute(
                """
                INSERT INTO cassaforte_movimenti (
                    operazione_id, elemento_id, tipo, data, ora, persona,
                    numero_busta, data_busta, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    operazione_id, riga["elemento_id"], riga["tipo"],
                    _pulisci(riga.get("data")), _pulisci(riga.get("ora")),
                    _pulisci(riga.get("persona")), _pulisci(riga.get("numero_busta")),
                    _pulisci(riga.get("data_busta")), _pulisci(riga.get("note")),
                ),
            )
    return operazione_id


def registra_deposito(
    elemento_id: int,
    numero_busta: str | None = None,
    data_busta: str | None = None,
    data: str | None = None,
    ora: str | None = None,
    persona: str | None = None,
    note: str | None = None,
) -> int:
    """Documentazione della versione portfolio."""
    return _inserisci_movimenti([{
        "elemento_id": elemento_id, "tipo": TIPO_DEPOSITO,
        "data": data, "ora": ora, "persona": persona,
        "numero_busta": numero_busta, "data_busta": data_busta, "note": note,
    }])


def registra_uscita(elementi: list[dict], persona: str, data: str, ora: str,
                    note: str | None = None) -> int:
    """Documentazione della versione portfolio."""
    return _inserisci_movimenti([
        {
            "elemento_id": e["elemento_id"], "tipo": TIPO_USCITA,
            "data": data, "ora": ora, "persona": persona,
            "numero_busta": e.get("numero_busta"), "data_busta": e.get("data_busta"),
            "note": note,
        }
        for e in elementi
    ])


def registra_rientro(elemento_id: int, persona: str, data: str, ora: str,
                     numero_busta: str | None = None, data_busta: str | None = None,
                     note: str | None = None) -> int:
    """Documentazione della versione portfolio."""
    return _inserisci_movimenti([{
        "elemento_id": elemento_id, "tipo": TIPO_RIENTRO,
        "data": data, "ora": ora, "persona": persona,
        "numero_busta": numero_busta, "data_busta": data_busta, "note": note,
    }])


_SELECT_ELEMENTI = f"""
    SELECT e.id, e.descrizione, e.categoria, e.note,
           m.tipo, m.data, m.ora, m.persona, m.numero_busta, m.data_busta
    FROM cassaforte_elementi e
    LEFT JOIN cassaforte_movimenti m ON m.id = (
        SELECT m2.id FROM cassaforte_movimenti m2
        WHERE m2.elemento_id = e.id
        ORDER BY m2.id DESC LIMIT 1
    )
"""


def _elemento_a_dizionario(riga) -> dict:
    (id_, descrizione, categoria, note,
     tipo, data, ora, persona, numero_busta, data_busta) = riga
    return {
        "id": id_,
        "descrizione": descrizione,
        "categoria": categoria,
        "note": note,

        "ultimo_tipo": tipo,
        "ultima_data": data,
        "ultima_ora": ora,
        "ultima_persona": persona,
        "numero_busta": numero_busta,
        "data_busta": data_busta,
        "fuori": tipo == TIPO_USCITA,
        "in_busta": bool(numero_busta),
    }


def elenco_elementi(fuori: bool | None = None, testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(_SELECT_ELEMENTI + " ORDER BY e.descrizione").fetchall()

    elementi = [_elemento_a_dizionario(r) for r in righe]
    if fuori is not None:
        elementi = [e for e in elementi if e["fuori"] is fuori]

    query = normalizza(testo_ricerca)
    if not query:
        return elementi
    return [
        e for e in elementi
        if query in normalizza(" ".join(str(e.get(c) or "") for c in (
            "descrizione", "categoria", "numero_busta", "ultima_persona", "note")))
    ]


def elemento(id_elemento: int) -> dict | None:
    with connessione() as c:
        riga = c.execute(_SELECT_ELEMENTI + " WHERE e.id = ?", (id_elemento,)).fetchone()
    return _elemento_a_dizionario(riga) if riga else None


def movimenti(testo_ricerca: str = "", elemento_id: int | None = None,
              anno: int | None = None, mese: int | None = None) -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        condizione = "WHERE m.elemento_id = ?" if elemento_id else ""
        parametri = (elemento_id,) if elemento_id else ()
        righe = c.execute(
            f"SELECT {', '.join('m.' + c for c in _CAMPI_MOVIMENTO)}, "
            f"       e.descrizione, e.categoria "
            f"FROM cassaforte_movimenti m "
            f"JOIN cassaforte_elementi e ON e.id = m.elemento_id "
            f"{condizione} "
            f"ORDER BY {ordine_cronologico('m.data')} DESC, m.id DESC",
            parametri,
        ).fetchall()

    elenco = []
    for riga in righe:
        movimento = dict(zip(_CAMPI_MOVIMENTO, riga))
        movimento["descrizione"] = riga[len(_CAMPI_MOVIMENTO)]
        movimento["categoria"] = riga[len(_CAMPI_MOVIMENTO) + 1]
        elenco.append(movimento)

    if anno is not None:
        elenco = [m for m in elenco if m["data"] and m["data"][6:10] == str(anno)]
    if mese is not None:
        elenco = [m for m in elenco if m["data"] and m["data"][3:5] == f"{mese:02d}"]

    query = normalizza(testo_ricerca)
    if not query:
        return elenco
    return [
        m for m in elenco
        if query in normalizza(" ".join(str(m.get(c) or "") for c in (
            "descrizione", "categoria", "tipo", "persona", "numero_busta", "note")))
    ]


def movimenti_senza_data(testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    return [m for m in movimenti(testo_ricerca) if not m["data"]]


def periodi_storico_cassaforte() -> list[tuple[int, int]]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            "SELECT DISTINCT substr(data, 7, 4), substr(data, 4, 2) FROM cassaforte_movimenti "
            "WHERE data IS NOT NULL ORDER BY 1 DESC, 2 DESC"
        ).fetchall()
    return [(int(a), int(m)) for a, m in righe if a and m]


def cicli_cassaforte(testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            """
            SELECT m.elemento_id, m.tipo, m.data, m.ora, m.persona,
                   m.numero_busta, m.data_busta, e.descrizione, e.categoria
            FROM cassaforte_movimenti m
            JOIN cassaforte_elementi e ON e.id = m.elemento_id
            WHERE m.tipo IN ('uscita', 'rientro')
            ORDER BY m.elemento_id, m.id
            """
        ).fetchall()

    cicli = []
    aperti: dict[int, dict] = {}
    for elemento_id, tipo, data, ora, persona, busta, data_busta, descrizione, categoria in righe:
        if tipo == TIPO_USCITA:
            if elemento_id in aperti:
                cicli.append(aperti.pop(elemento_id))
            aperti[elemento_id] = {
                "elemento": descrizione, "categoria": categoria,
                "uscita_data": data, "uscita_ora": ora, "uscita_persona": persona,
                "uscita_busta": busta,
                "rientro_data": None, "rientro_ora": None, "rientro_persona": None,
                "rientro_busta": None, "stato": "Fuori",
            }
        else:
            ciclo = aperti.pop(elemento_id, None)
            if ciclo is None:
                continue
            ciclo.update(rientro_data=data, rientro_ora=ora, rientro_persona=persona,
                         rientro_busta=busta, stato="Rientrato")
            cicli.append(ciclo)
    cicli.extend(aperti.values())

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
            "elemento", "categoria", "uscita_persona", "rientro_persona",
            "uscita_busta", "rientro_busta")))
    ]
