"""Documentazione della versione portfolio."""
from data.cassaforte import movimenti as _movimenti_cassaforte
from data.chiavi import storico_chiavi as _storico_chiavi
from data.comune import data_valida, mese_di_riferimento
from data.consegne_radio import cicli_consegne as _cicli_consegne
from data.gestione_radio import eventi_radio as _eventi_radio
from data.oggetti_smarriti import storico_eventi as _storico_oggetti_smarriti
from data.passaggio_consegne import storico_comunicazioni as _storico_passaggi
from data.rapporti_giornalieri import tutti_i_rapporti as _tutti_i_rapporti

MODULO_GESTIONE_RADIO = "Gestione Radio"
MODULO_CONSEGNA_RADIO = "Consegna Radio"
MODULO_BACHECA_CHIAVI = "Bacheca Chiavi"
MODULO_CASSAFORTE = "Cassaforte"
MODULO_OGGETTI_SMARRITI = "Oggetti Smarriti"
MODULO_RAPPORTO_GIORNALIERO = "Rapporto Giornaliero"
MODULO_PASSAGGIO_CONSEGNE = "Passaggio di Consegne"


MODULI = (
    MODULO_GESTIONE_RADIO,
    MODULO_CONSEGNA_RADIO,
    MODULO_BACHECA_CHIAVI,
    MODULO_CASSAFORTE,
    MODULO_OGGETTI_SMARRITI,
    MODULO_RAPPORTO_GIORNALIERO,
    MODULO_PASSAGGIO_CONSEGNE,
)

ICONE = {
    MODULO_GESTIONE_RADIO: "📻",
    MODULO_CONSEGNA_RADIO: "📡",
    MODULO_BACHECA_CHIAVI: "🔑",
    MODULO_CASSAFORTE: "🔐",
    MODULO_OGGETTI_SMARRITI: "📦",
    MODULO_RAPPORTO_GIORNALIERO: "📋",
    MODULO_PASSAGGIO_CONSEGNE: "📌",
}


def moduli_disponibili() -> list[str]:
    """Documentazione della versione portfolio."""
    return list(MODULI)


def _evento(modulo: str, data: str, ora, tipo_evento: str, titolo: str,
            descrizione: str = "", dettaglio=None, riferimento=None) -> dict:
    """Documentazione della versione portfolio."""
    return {
        "modulo": modulo,
        "data": data,
        "ora": (ora or "").strip(),
        "tipo_evento": tipo_evento,
        "titolo": titolo,
        "descrizione": descrizione,
        "dettaglio": dettaglio or [],
        "riferimento": riferimento,
    }


def _e_del_mese(data, anno: int, mese: int) -> bool:
    """Documentazione della versione portfolio."""
    return bool(data) and len(data) >= 10 and data[6:10] == str(anno) and data[3:5] == f"{mese:02d}"


def _data_ora_da_timestamp(testo) -> tuple[str, str]:
    """Documentazione della versione portfolio."""
    if not testo or len(testo) < 10:
        return "", ""
    data = testo[:10].replace(".", "-")
    if not data.strip() or not data_valida(data):
        return "", ""
    ora = testo[11:16].strip() if len(testo) >= 16 else ""
    return data, ora


_ETICHETTE_CAMPO_RADIO = {
    "creazione": "CREAZIONE",
    "rimozione": "RIMOZIONE",
    "stato": "CAMBIO STATO",
    "assegnata_a": "ASSEGNAZIONE",
}

_NOMI_CAMPO_RADIO = {
    "tipo_apparato": "Tipo apparato",
    "selettiva": "Selettiva",
    "matricola": "Matricola",
    "custodito_da": "Custodito da",
    "assegnata_a": "Assegnata a",
    "stato": "Stato",
    "note": "Note",
}


def _eventi_gestione_radio(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for evento in _eventi_radio(anno=anno, mese=mese):
        campo = evento["campo"]
        tipo = _ETICHETTE_CAMPO_RADIO.get(campo, "MODIFICA ANAGRAFICA")

        if evento["tipo_apparato"] or evento["selettiva"]:
            titolo = " — ".join(
                parte for parte in (
                    evento["tipo_apparato"],
                    f"selettiva {evento['selettiva']}" if evento["selettiva"] else "",
                ) if parte
            )
        else:


            titolo = "Radio non piu' in anagrafica"

        if campo == "creazione":
            descrizione = evento["valore_nuovo"] or ""
        elif campo == "rimozione":
            descrizione = evento["valore_precedente"] or ""
        else:
            nome_campo = _NOMI_CAMPO_RADIO.get(campo, campo)
            descrizione = (
                f"{nome_campo}: {evento['valore_precedente'] or '—'}"
                f" → {evento['valore_nuovo'] or '—'}"
            )

        eventi.append(_evento(
            MODULO_GESTIONE_RADIO, evento["data"], evento["ora"], tipo, titolo, descrizione,
            dettaglio=[
                ("Campo", _NOMI_CAMPO_RADIO.get(campo, campo)),
                ("Valore precedente", evento["valore_precedente"] or ""),
                ("Valore nuovo", evento["valore_nuovo"] or ""),
            ],
        ))
    return eventi


def _eventi_consegna_radio(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for ciclo in _cicli_consegne():
        if _e_del_mese(ciclo["uscita_data"], anno, mese):
            eventi.append(_evento(
                MODULO_CONSEGNA_RADIO, ciclo["uscita_data"], ciclo["uscita_ora"],
                "CONSEGNA", ciclo["elemento"] or "Radio",
                f"Presa da: {ciclo['uscita_persona'] or '—'}",
                dettaglio=[
                    ("Radio", ciclo["elemento"] or ""),
                    ("Presa da", ciclo["uscita_persona"] or ""),
                    ("Note", ciclo["note"] or ""),
                ],
            ))

        if ciclo["rientro_data"] and _e_del_mese(ciclo["rientro_data"], anno, mese):
            eventi.append(_evento(
                MODULO_CONSEGNA_RADIO, ciclo["rientro_data"], ciclo["rientro_ora"],
                "RIENTRO", ciclo["elemento"] or "Radio",
                f"Riportata da: {ciclo['rientro_persona'] or '—'}",
                dettaglio=[
                    ("Radio", ciclo["elemento"] or ""),
                    ("Riportata da", ciclo["rientro_persona"] or ""),
                    ("Note", ciclo["note"] or ""),
                ],
            ))
    return eventi


def _eventi_bacheca_chiavi(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for movimento in _storico_chiavi(anno=anno, mese=mese):
        eventi.append(_evento(
            MODULO_BACHECA_CHIAVI, movimento["data"], movimento["ora"],
            movimento["operazione"], movimento["elemento"],
            f"{movimento['bacheca']} · {movimento['persona'] or '—'}",
            dettaglio=[
                ("Chiave", movimento["elemento"]),
                ("Bacheca", movimento["bacheca"]),
                ("Persona", movimento["persona"] or ""),
                ("Note", movimento["note"] or ""),
            ],
        ))
    return eventi


def _eventi_cassaforte(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for movimento in _movimenti_cassaforte(anno=anno, mese=mese):
        if movimento["tipo"] not in ("uscita", "rientro"):
            continue
        eventi.append(_evento(
            MODULO_CASSAFORTE, movimento["data"], movimento["ora"],
            movimento["tipo"].upper(), movimento["descrizione"],
            f"{movimento['persona'] or '—'}"
            + (f" · busta {movimento['numero_busta']}" if movimento["numero_busta"] else ""),
            dettaglio=[
                ("Elemento", movimento["descrizione"]),
                ("Categoria", movimento["categoria"] or ""),
                ("Persona", movimento["persona"] or ""),
                ("Numero busta", movimento["numero_busta"] or ""),
                ("Data busta", movimento["data_busta"] or ""),
                ("Note", movimento["note"] or ""),
            ],
        ))
    return eventi


def _eventi_oggetti_smarriti(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for evento in _storico_oggetti_smarriti(anno=anno, mese=mese):
        eventi.append(_evento(
            MODULO_OGGETTI_SMARRITI, evento["data"], evento["ora"],
            evento["operazione"], evento["elemento"],
            evento["dettagli"] or "",
            dettaglio=[
                ("Oggetto", evento["elemento"]),
                ("Operatore", evento["persona"] or ""),
                ("Dettagli", evento["dettagli"] or ""),
                ("Note", evento["note"] or ""),
            ],
        ))
    return eventi


def _eventi_rapporto_giornaliero(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for rapporto in _tutti_i_rapporti():
        if not _e_del_mese(rapporto["data_turno"], anno, mese):
            continue
        operatore = f"{rapporto['operatore_nome']} {rapporto['operatore_cognome']}".strip()
        eventi.append(_evento(
            MODULO_RAPPORTO_GIORNALIERO, rapporto["data_turno"], rapporto["ora_inizio"],
            "RAPPORTO DI TURNO", operatore or "Rapporto",
            f"Turno {rapporto['ora_inizio']} - {rapporto['ora_fine']}"
            f" · {'aperto' if rapporto['stato'] == 'aperto' else 'chiuso'}",
            dettaglio=[
                ("Operatore", operatore),
                ("Turno", f"{rapporto['ora_inizio']} - {rapporto['ora_fine']}"),
                ("Stato", rapporto["stato"]),
                ("File", rapporto["nome_file"]),
            ],
            riferimento={"tipo": "rapporto", "rapporto": rapporto},
        ))
    return eventi


def _eventi_passaggio_consegne(anno: int, mese: int) -> list[dict]:
    """Documentazione della versione portfolio."""
    eventi = []
    for comunicazione in _storico_passaggi():
        testo = comunicazione["testo"] or ""
        titolo = testo if len(testo) <= 60 else testo[:57] + "..."

        data, ora = _data_ora_da_timestamp(comunicazione["creato_il"])
        if data and _e_del_mese(data, anno, mese):
            eventi.append(_evento(
                MODULO_PASSAGGIO_CONSEGNE, data, ora,
                "COMUNICAZIONE SCRITTA", titolo,
                "📌 Fissata in alto" if comunicazione["fissato"] else "",
                dettaglio=[
                    ("Comunicazione", testo),
                    ("Scritta il", comunicazione["creato_il"] or ""),
                    ("Fissata", "Sì" if comunicazione["fissato"] else "No"),
                ],
            ))

        data, ora = _data_ora_da_timestamp(comunicazione["archiviato_il"])
        if data and _e_del_mese(data, anno, mese):
            eventi.append(_evento(
                MODULO_PASSAGGIO_CONSEGNE, data, ora,
                "TOLTA DAL BLOCCO NOTE", titolo,
                "Resta consultabile nello storico",
                dettaglio=[
                    ("Comunicazione", testo),
                    ("Scritta il", comunicazione["creato_il"] or ""),
                    ("Tolta il", comunicazione["archiviato_il"] or ""),
                ],
            ))
    return eventi


_ADATTATORI = (
    _eventi_gestione_radio,
    _eventi_consegna_radio,
    _eventi_bacheca_chiavi,
    _eventi_cassaforte,
    _eventi_oggetti_smarriti,
    _eventi_rapporto_giornaliero,
    _eventi_passaggio_consegne,
)


def _chiave_ordinamento(evento: dict) -> tuple:
    """Documentazione della versione portfolio."""
    indice_modulo = MODULI.index(evento["modulo"]) if evento["modulo"] in MODULI else len(MODULI)
    return (indice_modulo, 0 if evento["ora"] else 1, evento["ora"], evento["titolo"] or "")


def _eventi_del_mese(anno: int, mese: int) -> list[dict]:
    eventi = []
    for adattatore in _ADATTATORI:
        eventi.extend(adattatore(anno, mese))
    return eventi


def eventi_del_giorno(data: str, modulo: str | None = None) -> list[dict]:
    """Documentazione della versione portfolio."""
    if not data or not data.strip() or not data_valida(data):
        return []

    anno, mese = mese_di_riferimento(data)
    eventi = [e for e in _eventi_del_mese(anno, mese) if e["data"] == data]
    if modulo:
        eventi = [e for e in eventi if e["modulo"] == modulo]
    eventi.sort(key=_chiave_ordinamento)
    return eventi


def eventi_per_modulo(eventi: list[dict]) -> list[tuple[str, list[dict]]]:
    """Documentazione della versione portfolio."""
    gruppi = []
    for nome in MODULI:
        del_modulo = [e for e in eventi if e["modulo"] == nome]
        if del_modulo:
            gruppi.append((nome, del_modulo))
    return gruppi


def giorni_con_eventi(anno: int, mese: int) -> set[str]:
    """Documentazione della versione portfolio."""
    return {e["data"] for e in _eventi_del_mese(anno, mese) if e["data"]}
