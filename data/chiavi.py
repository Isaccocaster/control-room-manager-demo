"""Documentazione della versione portfolio."""
from data.comune import normalizza, ordine_cronologico
from data.database import connessione

TIPO_USCITA = "uscita"
TIPO_RIENTRO = "rientro"


def crea_tabelle(connessione) -> None:
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS bacheche (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
        """
    )
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS chiavi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bacheca_id INTEGER NOT NULL REFERENCES bacheche(id),
            numero INTEGER NOT NULL,
            descrizione TEXT NOT NULL,
            blocco TEXT
        )
        """
    )
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS cassaforte_chiavi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            piano TEXT,
            targhetta INTEGER,
            area_ufficio TEXT NOT NULL,
            numero_chiavi INTEGER,
            colore_targhetta TEXT
        )
        """
    )


    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS chiavi_movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chiave_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('uscita', 'rientro')),
            data TEXT NOT NULL,
            ora TEXT NOT NULL,
            persona TEXT NOT NULL,
            note TEXT
        )
        """
    )
    _rimuovi_vincolo_fk_chiavi_movimenti(connessione)
    connessione.commit()


def _rimuovi_vincolo_fk_chiavi_movimenti(connessione) -> None:
    """Documentazione della versione portfolio."""
    ha_vincolo = any(
        riga[2] == "chiavi"
        for riga in connessione.execute("PRAGMA foreign_key_list(chiavi_movimenti)")
    )
    if not ha_vincolo:
        return

    connessione.execute("PRAGMA foreign_keys = OFF")
    connessione.execute("ALTER TABLE chiavi_movimenti RENAME TO chiavi_movimenti_vecchia")
    connessione.execute(
        """
        CREATE TABLE chiavi_movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chiave_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('uscita', 'rientro')),
            data TEXT NOT NULL,
            ora TEXT NOT NULL,
            persona TEXT NOT NULL,
            note TEXT
        )
        """
    )
    connessione.execute(
        "INSERT INTO chiavi_movimenti (id, chiave_id, tipo, data, ora, persona, note) "
        "SELECT id, chiave_id, tipo, data, ora, persona, note FROM chiavi_movimenti_vecchia"
    )
    connessione.execute("DROP TABLE chiavi_movimenti_vecchia")
    connessione.execute("PRAGMA foreign_keys = ON")


def elenco_bacheche() -> list[dict]:
    with connessione() as c:
        righe = c.execute("SELECT id, nome FROM bacheche ORDER BY id").fetchall()
    return [{"id": id_, "nome": nome} for id_, nome in righe]


def cerca_chiavi(bacheca_id: int, testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            "SELECT id, numero, descrizione, blocco FROM chiavi WHERE bacheca_id = ? ORDER BY numero",
            (bacheca_id,),
        ).fetchall()

    query_normalizzata = normalizza(testo_ricerca)
    risultati = [
        {"id": id_, "numero": numero, "descrizione": descrizione, "blocco": blocco}
        for id_, numero, descrizione, blocco in righe
        if query_normalizzata in normalizza(descrizione)
        or query_normalizzata in normalizza(str(numero))
        or query_normalizzata in normalizza(blocco or "")
    ]
    return risultati


def raggruppa_per_blocco(chiavi: list[dict]) -> list[tuple[str | None, list[dict]]]:
    """Documentazione della versione portfolio."""
    gruppi: dict[str | None, list[dict]] = {}
    for chiave in chiavi:
        gruppi.setdefault(chiave.get("blocco"), []).append(chiave)
    return list(gruppi.items())


def tutte_le_chiavi_bacheca(bacheca_id: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    return cerca_chiavi(bacheca_id, "")


def aggiungi_chiave(bacheca_id: int, numero: int, descrizione: str, blocco: str | None = None) -> None:
    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO chiavi (bacheca_id, numero, descrizione, blocco) VALUES (?, ?, ?, ?)",
            (bacheca_id, numero, descrizione.strip(), (blocco or "").strip() or None),
        )


def modifica_chiave(id_chiave: int, numero: int, descrizione: str, blocco: str | None = None) -> None:
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE chiavi SET numero = ?, descrizione = ?, blocco = ? WHERE id = ?",
            (numero, descrizione.strip(), (blocco or "").strip() or None, id_chiave),
        )


def rimuovi_chiave(id_chiave: int) -> None:
    with connessione(con_backup=True) as c:
        c.execute("DELETE FROM chiavi WHERE id = ?", (id_chiave,))


def cerca_cassaforte(testo_ricerca: str = "") -> list[dict]:
    with connessione() as c:
        righe = c.execute(
            "SELECT id, piano, targhetta, area_ufficio, numero_chiavi, colore_targhetta "
            "FROM cassaforte_chiavi ORDER BY targhetta"
        ).fetchall()

    query_normalizzata = normalizza(testo_ricerca)
    risultati = []
    for id_, piano, targhetta, area_ufficio, numero_chiavi, colore_targhetta in righe:
        if query_normalizzata in normalizza(area_ufficio) or query_normalizzata in normalizza(str(targhetta)):
            risultati.append(
                {
                    "id": id_,
                    "piano": piano,
                    "targhetta": targhetta,
                    "area_ufficio": area_ufficio,
                    "numero_chiavi": numero_chiavi,
                    "colore_targhetta": colore_targhetta,
                }
            )
    return risultati


def tutta_la_cassaforte() -> list[dict]:
    return cerca_cassaforte("")


def aggiungi_cassaforte(piano: str, targhetta: int, area_ufficio: str, numero_chiavi: int, colore_targhetta: str) -> None:
    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO cassaforte_chiavi (piano, targhetta, area_ufficio, numero_chiavi, colore_targhetta) "
            "VALUES (?, ?, ?, ?, ?)",
            (piano, targhetta, area_ufficio.strip(), numero_chiavi, colore_targhetta),
        )


def modifica_cassaforte(
    id_voce: int, piano: str, targhetta: int, area_ufficio: str, numero_chiavi: int, colore_targhetta: str
) -> None:
    with connessione(con_backup=True) as c:
        c.execute(
            "UPDATE cassaforte_chiavi SET piano = ?, targhetta = ?, area_ufficio = ?, numero_chiavi = ?, "
            "colore_targhetta = ? WHERE id = ?",
            (piano, targhetta, area_ufficio.strip(), numero_chiavi, colore_targhetta, id_voce),
        )


def rimuovi_cassaforte(id_voce: int) -> None:
    with connessione(con_backup=True) as c:
        c.execute("DELETE FROM cassaforte_chiavi WHERE id = ?", (id_voce,))


_ULTIMO_MOVIMENTO = """
    SELECT m.* FROM chiavi_movimenti m
    WHERE m.id = (SELECT MAX(m2.id) FROM chiavi_movimenti m2 WHERE m2.chiave_id = m.chiave_id)
"""


def registra_uscita_chiave(chiave_id: int, persona: str, data: str, ora: str,
                           note: str | None = None) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO chiavi_movimenti (chiave_id, tipo, data, ora, persona, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (chiave_id, TIPO_USCITA, data.strip(), ora.strip(), persona.strip(),
             (note or "").strip() or None),
        )


def registra_rientro_chiave(chiave_id: int, persona: str, data: str, ora: str,
                            note: str | None = None) -> None:
    """Documentazione della versione portfolio."""
    with connessione(con_backup=True) as c:
        c.execute(
            "INSERT INTO chiavi_movimenti (chiave_id, tipo, data, ora, persona, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (chiave_id, TIPO_RIENTRO, data.strip(), ora.strip(), persona.strip(),
             (note or "").strip() or None),
        )


def chiavi_fuori() -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            f"""
            SELECT k.id, k.numero, k.descrizione, b.nome,
                   u.data, u.ora, u.persona, u.note
            FROM ({_ULTIMO_MOVIMENTO}) u
            JOIN chiavi k ON k.id = u.chiave_id
            JOIN bacheche b ON b.id = k.bacheca_id
            WHERE u.tipo = ?
            ORDER BY {ordine_cronologico('u.data')} DESC, u.ora DESC
            """,
            (TIPO_USCITA,),
        ).fetchall()
    return [
        {
            "chiave_id": id_, "numero": numero, "descrizione": descrizione,
            "bacheca": bacheca, "data": data, "ora": ora, "persona": persona, "note": note,
        }
        for id_, numero, descrizione, bacheca, data, ora, persona, note in righe
    ]


def conta_chiavi_fuori() -> int:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        return c.execute(
            f"SELECT COUNT(*) FROM ({_ULTIMO_MOVIMENTO}) u WHERE u.tipo = ?", (TIPO_USCITA,)
        ).fetchone()[0]


def chiave_e_fuori(chiave_id: int) -> bool:
    with connessione() as c:
        riga = c.execute(
            "SELECT tipo FROM chiavi_movimenti WHERE chiave_id = ? ORDER BY id DESC LIMIT 1",
            (chiave_id,),
        ).fetchone()
    return bool(riga) and riga[0] == TIPO_USCITA


def storico_chiavi(testo_ricerca: str = "", anno: int | None = None, mese: int | None = None,
                   limite: int | None = None, salta: int = 0,
                   chiave_id: int | None = None) -> list[dict]:
    """Documentazione della versione portfolio."""
    condizioni = []
    parametri: list = []
    if anno is not None:
        condizioni.append("substr(m.data, 7, 4) = ?")
        parametri.append(str(anno))
    if mese is not None:
        condizioni.append("substr(m.data, 4, 2) = ?")
        parametri.append(f"{mese:02d}")
    if chiave_id is not None:
        condizioni.append("m.chiave_id = ?")
        parametri.append(chiave_id)
    dove = ("WHERE " + " AND ".join(condizioni)) if condizioni else ""

    limitazione = ""
    if limite is not None:
        limitazione = "LIMIT ? OFFSET ?"
        parametri += [limite, salta]

    with connessione() as c:
        righe = c.execute(
            f"""
            SELECT m.data, m.ora, m.tipo, k.numero, k.descrizione, b.nome, m.persona, m.note
            FROM chiavi_movimenti m
            LEFT JOIN chiavi k ON k.id = m.chiave_id
            LEFT JOIN bacheche b ON b.id = k.bacheca_id
            {dove}
            ORDER BY {ordine_cronologico('m.data')} DESC, m.ora DESC, m.id DESC
            {limitazione}
            """,
            tuple(parametri),
        ).fetchall()


    eventi = [
        {
            "data": data, "ora": ora, "operazione": tipo.upper(),
            "elemento": f"{numero} — {descrizione}" if numero is not None else "[chiave rimossa dall'anagrafica]",
            "bacheca": bacheca or "—",
            "persona": persona, "note": note, "dettagli": bacheca or "—",
        }
        for data, ora, tipo, numero, descrizione, bacheca, persona, note in righe
    ]

    query = normalizza(testo_ricerca)
    if not query:
        return eventi
    return [
        e for e in eventi
        if query in normalizza(" ".join(str(e.get(k) or "") for k in
                                        ("elemento", "persona", "operazione", "bacheca", "note")))
    ]


def periodi_storico_chiavi() -> list[tuple[int, int]]:
    with connessione() as c:
        righe = c.execute(
            "SELECT DISTINCT substr(data, 7, 4), substr(data, 4, 2) FROM chiavi_movimenti "
            "ORDER BY 1 DESC, 2 DESC"
        ).fetchall()
    return [(int(a), int(m)) for a, m in righe if a and m]


def cicli_chiavi(testo_ricerca: str = "") -> list[dict]:
    """Documentazione della versione portfolio."""
    with connessione() as c:
        righe = c.execute(
            """
            SELECT m.chiave_id, m.tipo, m.data, m.ora, m.persona,
                   k.numero, k.descrizione, b.nome
            FROM chiavi_movimenti m
            JOIN chiavi k ON k.id = m.chiave_id
            JOIN bacheche b ON b.id = k.bacheca_id
            ORDER BY m.chiave_id, m.id
            """
        ).fetchall()

    cicli = []
    aperti: dict[int, dict] = {}
    for chiave_id, tipo, data, ora, persona, numero, descrizione, bacheca in righe:
        if tipo == TIPO_USCITA:
            if chiave_id in aperti:


                cicli.append(aperti.pop(chiave_id))
            aperti[chiave_id] = {
                "elemento": f"{numero} — {descrizione}", "bacheca": bacheca,
                "uscita_data": data, "uscita_ora": ora, "uscita_persona": persona,
                "rientro_data": None, "rientro_ora": None, "rientro_persona": None,
                "stato": "Ancora fuori",
            }
        else:
            ciclo = aperti.pop(chiave_id, None)
            if ciclo is None:
                continue
            ciclo.update(rientro_data=data, rientro_ora=ora, rientro_persona=persona,
                         stato="Rientrata")
            cicli.append(ciclo)
    cicli.extend(aperti.values())

    cicli.sort(key=_chiave_ordinamento_ciclo, reverse=True)

    query = normalizza(testo_ricerca)
    if not query:
        return cicli
    return [
        cc for cc in cicli
        if query in normalizza(" ".join(str(cc.get(k) or "") for k in (
            "elemento", "bacheca", "uscita_persona", "rientro_persona")))
    ]


def _chiave_ordinamento_ciclo(ciclo: dict) -> str:
    data = ciclo["uscita_data"] or ""
    return f"{data[6:10]}{data[3:5]}{data[0:2]}{(ciclo['uscita_ora'] or ''):>5}"
