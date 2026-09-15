"""Documentazione della versione portfolio."""
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from config.impostazioni import (
    CHIAVI_CARTELLE,
    cartella_dati_applicazione,
    carica_impostazioni,
    percorso_file_impostazioni,
)
from config.registro import (
    conteggi_registro,
    motivo_fallback,
    percorso_file_log,
)
from config.versione import (
    ETICHETTA_VERSIONE,
    SCHEMA_DATABASE,
    SCHEMA_MASSIMO_SUPPORTATO,
    VERSIONE_APP,
)


OK = "OK"
ATTENZIONE = "ATTENZIONE"
ERRORE = "ERRORE"
CRITICO = "CRITICO"
NON_CONFIGURATO = "NON CONFIGURATO"
NON_VERIFICATO = "NON VERIFICATO"


_GRAVITA = {
    OK: 0,
    NON_CONFIGURATO: 1,
    NON_VERIFICATO: 2,
    ATTENZIONE: 3,
    ERRORE: 4,
    CRITICO: 5,
}


def peggiore(stati) -> str:
    """Documentazione della versione portfolio."""
    stati = list(stati)
    return max(stati, key=lambda s: _GRAVITA.get(s, 0)) if stati else OK


ORE_BACKUP_ATTENZIONE = 48


GIORNI_VERSIONE_ATTENZIONE = 7


GIGABYTE_LIBERI_MINIMI_DATI = 5
GIGABYTE_LIBERI_MINIMI_BACKUP = 1

_BYTE_PER_GIGABYTE = 1024 ** 3


_ultimo_controllo: dict | None = None


def ultimo_controllo_approfondito() -> dict | None:
    """Documentazione della versione portfolio."""
    return _ultimo_controllo


def _voce(nome: str, stato: str, valore="", dettaglio="") -> dict:
    return {"nome": nome, "stato": stato, "valore": str(valore), "dettaglio": dettaglio}


def _protetto(nome: str, funzione):
    """Documentazione della versione portfolio."""
    from config.registro import logger

    try:
        return funzione()
    except Exception as errore:
        logger(__name__).error("Controllo diagnostico fallito: %s", nome, exc_info=True)
        return _voce(nome, NON_VERIFICATO, "non disponibile", type(errore).__name__)


def stato_rapido() -> dict:
    """Documentazione della versione portfolio."""
    sezioni = [
        _sezione_identita(),
        _sezione_database(),
        _sezione_backup(),
        _sezione_registro(),
        _sezione_filesystem(),
    ]
    return {
        "sezioni": sezioni,
        "esito": peggiore(s["stato"] for s in sezioni),
        "quando": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }


def _sezione(titolo: str, voci: list[dict]) -> dict:
    return {"titolo": titolo, "voci": voci, "stato": peggiore(v["stato"] for v in voci)}


def _sezione_identita() -> dict:
    return _sezione("Identità software", [
        _voce("Control Room Manager Demo", OK, ETICHETTA_VERSIONE),
        _protetto("Schema database", _voce_schema),
    ])


def _voce_schema() -> dict:
    from data.schema import stato_compatibilita

    percorso = _percorso_database()
    if not percorso.is_file():
        return _voce("Schema database", NON_VERIFICATO, "nessun database",
                     "il file non esiste ancora")

    trovata = _leggi_user_version(percorso)
    stato_testuale = stato_compatibilita(trovata)
    if stato_testuale == "non supportato":
        return _voce(
            "Schema database", CRITICO, f"{trovata} (atteso {SCHEMA_DATABASE})",
            "il database viene da una versione più recente del programma: "
            "nessuna scrittura è consentita",
        )
    if stato_testuale == "allineato":
        return _voce("Schema database", OK, str(trovata), "compatibile")
    return _voce("Schema database", ATTENZIONE, str(trovata),
                 f"{stato_testuale}: sarà allineato al prossimo avvio")


def _percorso_database() -> Path:
    from data.database import NOME_FILE_DATABASE

    return cartella_dati_applicazione() / NOME_FILE_DATABASE


def _leggi_user_version(percorso: Path) -> int:
    conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
    try:
        (valore,) = conn.execute("PRAGMA user_version").fetchone()
    finally:
        conn.close()
    return int(valore)


def _sezione_database() -> dict:
    return _sezione("Database", [
        _protetto("Stato", _voce_database_apribile),
        _protetto("Dimensione", _voce_dimensione_database),
        _voce("Percorso", OK, _percorso_database().parent),
        _voce_ultimo_controllo(),
    ])


def _voce_database_apribile() -> dict:
    """Documentazione della versione portfolio."""
    percorso = _percorso_database()
    if not percorso.is_file():
        return _voce("Stato", ERRORE, "assente", f"nessun file in {percorso}")

    conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
    try:
        (quante,) = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchone()
    finally:
        conn.close()
    if quante == 0:
        return _voce("Stato", ERRORE, "vuoto", "nessuna tabella nel database")
    return _voce("Stato", OK, "apribile", f"{quante} tabelle")


def _voce_dimensione_database() -> dict:
    percorso = _percorso_database()
    if not percorso.is_file():
        return _voce("Dimensione", NON_VERIFICATO, "-")
    return _voce("Dimensione", OK, _leggibile(percorso.stat().st_size))


def _voce_ultimo_controllo() -> dict:
    """Documentazione della versione portfolio."""
    ultimo = ultimo_controllo_approfondito()
    if ultimo is None:
        return _voce("Ultimo controllo approfondito", OK, "mai in questa sessione",
                     "si esegue su richiesta")
    return _voce("Ultimo controllo approfondito", OK,
                 f"{ultimo['quando']} — {ultimo['esito']}")


def _sezione_backup() -> dict:
    return _sezione("Backup", _protetto_lista("Backup", _voci_backup))


def _protetto_lista(nome: str, funzione) -> list[dict]:
    from config.registro import logger

    try:
        return funzione()
    except Exception as errore:
        logger(__name__).error("Controllo diagnostico fallito: %s", nome, exc_info=True)
        return [_voce(nome, NON_VERIFICATO, "non disponibile", type(errore).__name__)]


def _voci_backup() -> list[dict]:
    from data.backup import NOME_FILE_BACKUP, elenco_versioni

    percorso = carica_impostazioni().get("cartella_backup", "")
    if not percorso.strip():


        return [_voce("Configurato", NON_CONFIGURATO, "no",
                      "nessuna copia esterna dei dati viene conservata")]

    cartella = Path(percorso)
    if not cartella.is_dir():
        return [
            _voce("Configurato", OK, "sì", str(cartella)),
            _voce("Cartella", ERRORE, "non raggiungibile",
                  "la chiavetta è stata tolta o il disco di rete non risponde"),
        ]

    voci = [_voce("Configurato", OK, "sì", str(cartella))]

    corrente = cartella / NOME_FILE_BACKUP
    if not corrente.is_file():
        voci.append(_voce("Ultimo backup", ERRORE, "nessuno",
                          "la cartella è configurata ma non contiene una copia"))
    else:
        quando = datetime.fromtimestamp(corrente.stat().st_mtime)
        ore = (datetime.now() - quando).total_seconds() / 3600
        stato = ATTENZIONE if ore > ORE_BACKUP_ATTENZIONE else OK
        voci.append(_voce("Ultimo backup", stato, quando.strftime("%d/%m/%Y %H:%M")))
        voci.append(_voce(
            "Età del backup", stato, _eta_leggibile(ore),
            f"oltre {ORE_BACKUP_ATTENZIONE} ore" if stato == ATTENZIONE else "",
        ))


    versioni = elenco_versioni(cartella, verifica=False)
    if not versioni:
        voci.append(_voce("Versioni datate", ATTENZIONE, "nessuna",
                          "non è ancora stata creata alcuna copia datata"))
    else:
        giorni = _giorni_dal_nome(versioni[0]["nome"])
        stato = ATTENZIONE if giorni is not None and giorni > GIORNI_VERSIONE_ATTENZIONE else OK
        voci.append(_voce(
            "Ultima versione", stato, versioni[0]["nome"],
            f"{len(versioni)} copie conservate · integrità verificabile "
            "con il controllo approfondito",
        ))
    return voci


def _giorni_dal_nome(nome: str) -> float | None:
    try:
        return (datetime.now() - datetime.strptime(nome, "%Y-%m-%d_%H%M%S")).days
    except ValueError:
        return None


def _sezione_registro() -> dict:
    return _sezione("Registro tecnico", _protetto_lista("Registro", _voci_registro))


def _voci_registro() -> list[dict]:
    percorso = percorso_file_log()
    ripiego = motivo_fallback()

    if percorso is None:
        voci = [
            _voce("Stato", ERRORE, "solo stderr",
                  "nessun file di registro: i guasti non lasciano traccia su disco"),
            _voce("Modalità", ERRORE, "nessun file", ripiego or ""),
        ]
        return voci

    if ripiego:
        voci = [
            _voce("Stato", ATTENZIONE, "attivo"),
            _voce("Modalità", ATTENZIONE, "ripiego",
                  "la cartella prevista non è scrivibile: il registro scrive altrove"),
        ]
    else:
        voci = [
            _voce("Stato", OK, "attivo"),
            _voce("Modalità", OK, "normale"),
        ]
    voci.append(_voce("Percorso", OK, percorso.parent))

    conteggi = conteggi_registro()
    if not conteggi["disponibile"]:
        voci.append(_voce("Eventi registrati", NON_VERIFICATO, "nessun file leggibile"))
        return voci


    nota = "conteggio relativo ai soli file di registro conservati"
    voci.append(_voce("WARNING", OK if not conteggi["warning"] else ATTENZIONE,
                      conteggi["warning"], nota))
    voci.append(_voce("ERROR", OK if not conteggi["error"] else ATTENZIONE,
                      conteggi["error"], nota))
    voci.append(_voce("CRITICAL", OK if not conteggi["critical"] else CRITICO,
                      conteggi["critical"], nota))
    voci.append(_voce("Errori ultime 24 ore",
                      OK if not conteggi["recenti"] else ATTENZIONE,
                      conteggi["recenti"], "ERROR e CRITICAL delle ultime 24 ore"))
    voci.append(_voce("Ultimo ERROR", OK,
                      _quando_leggibile(conteggi["ultimo_error"]),
                      conteggi["origine_ultimo_error"] or ""))
    voci.append(_voce("Ultimo CRITICAL", OK,
                      _quando_leggibile(conteggi["ultimo_critical"]),
                      conteggi["origine_ultimo_critical"] or ""))
    if conteggi["file_illeggibili"]:
        voci.append(_voce("File illeggibili", ATTENZIONE, conteggi["file_illeggibili"]))
    return voci


def _quando_leggibile(quando: str | None) -> str:
    if not quando:
        return "nessuno"
    try:
        return datetime.strptime(quando, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return quando


def _sezione_filesystem() -> dict:
    return _sezione("Cartelle e spazio", _protetto_lista("Filesystem", _voci_filesystem))


def _voci_filesystem() -> list[dict]:
    impostazioni = carica_impostazioni()
    voci = []
    configurate = raggiungibili = 0

    for chiave in CHIAVI_CARTELLE:
        percorso = (impostazioni.get(chiave) or "").strip()
        etichetta = _etichetta_cartella(chiave)
        if not percorso:
            voci.append(_voce(etichetta, NON_CONFIGURATO, "non configurata"))
            continue
        configurate += 1
        stato, valore, dettaglio = _controlla_cartella(percorso)
        if stato == OK:
            raggiungibili += 1
        voci.append(_voce(etichetta, stato, valore, dettaglio))

    voci.insert(0, _voce(
        "Cartelle operative",
        OK if configurate and raggiungibili == configurate else
        (NON_CONFIGURATO if not configurate else ATTENZIONE),
        f"{raggiungibili}/{configurate} raggiungibili e scrivibili"
        if configurate else "nessuna configurata",
    ))
    voci.append(_voce_spazio("Spazio disco dati", cartella_dati_applicazione(),
                             GIGABYTE_LIBERI_MINIMI_DATI))

    percorso_backup = (impostazioni.get("cartella_backup") or "").strip()
    if percorso_backup and Path(percorso_backup).is_dir():
        if not _stesso_disco(Path(percorso_backup), cartella_dati_applicazione()):
            voci.append(_voce_spazio("Spazio disco backup", Path(percorso_backup),
                                     GIGABYTE_LIBERI_MINIMI_BACKUP))

    voci.append(stato_configurazione())
    return voci


def _etichetta_cartella(chiave: str) -> str:
    """Documentazione della versione portfolio."""
    try:
        from ui.impostazioni.schermata import ETICHETTE_CARTELLE

        return ETICHETTE_CARTELLE.get(chiave, chiave)
    except Exception:
        return chiave.replace("cartella_", "").replace("_", " ").capitalize()


def _controlla_cartella(percorso: str) -> tuple[str, str, str]:
    """Documentazione della versione portfolio."""
    cartella = Path(percorso)
    if not cartella.is_dir():
        return ERRORE, "non raggiungibile", percorso

    descrittore = nome = None
    try:
        descrittore, nome = tempfile.mkstemp(dir=cartella, prefix=".demo_prova_")
    except OSError as errore:
        return ERRORE, "non scrivibile", f"{type(errore).__name__}"
    finally:
        if descrittore is not None:
            os.close(descrittore)
        if nome is not None:
            try:
                os.unlink(nome)
            except OSError:
                pass
    return OK, "raggiungibile e scrivibile", percorso


def _voce_spazio(nome: str, dove: Path, minimo_gb: int) -> dict:
    try:
        libero = shutil.disk_usage(dove).free
    except OSError as errore:
        return _voce(nome, NON_VERIFICATO, "non determinabile", type(errore).__name__)
    gigabyte = libero / _BYTE_PER_GIGABYTE
    stato = ERRORE if gigabyte < minimo_gb / 2 else (ATTENZIONE if gigabyte < minimo_gb else OK)
    return _voce(nome, stato, f"{gigabyte:.1f} GB liberi",
                 f"soglia: {minimo_gb} GB" if stato != OK else "")


def _stesso_disco(uno: Path, altro: Path) -> bool:
    try:
        return os.path.splitdrive(uno.resolve())[0].lower() == \
            os.path.splitdrive(altro.resolve())[0].lower()
    except OSError:
        return False


def stato_configurazione() -> dict:
    """Documentazione della versione portfolio."""
    percorso = percorso_file_impostazioni()
    scartato = percorso.with_suffix(percorso.suffix + ".corrotto")
    if scartato.exists():
        return _voce("Configurazione", ATTENZIONE, "recuperata",
                     "un file di configurazione illeggibile è stato messo da parte")
    if not percorso.is_file():
        return _voce("Configurazione", NON_CONFIGURATO, "assente",
                     "nessuna cartella è ancora stata configurata")
    return _voce("Configurazione", OK, "leggibile")


def controllo_approfondito() -> dict:
    """Documentazione della versione portfolio."""
    global _ultimo_controllo
    from config.registro import logger

    registro = logger(__name__)
    registro.info("Controllo approfondito: avvio")

    voci = [
        _protetto("Integrità database", _voce_integrity_check),
        _protetto("Vincoli di integrità", _voce_foreign_key_check),
        _protetto("Schema", _voce_schema),
        _protetto("Backup più recente", _voce_backup_verificato),
        _protetto("Cartelle operative", _voce_cartelle_aggregate),
        _protetto("Spazio disco", lambda: _voce_spazio(
            "Spazio disco", cartella_dati_applicazione(), GIGABYTE_LIBERI_MINIMI_DATI)),
        _protetto("Registro tecnico", _voce_registro_aggregata),
        _protetto("Configurazione", stato_configurazione),
    ]
    esito = peggiore(v["stato"] for v in voci)
    quando = datetime.now().strftime("%d/%m/%Y %H:%M")
    _ultimo_controllo = {"quando": quando, "esito": esito}

    registro.info(
        "Controllo approfondito: %s — %s", esito,
        " · ".join(f"{v['nome']}={v['stato']}" for v in voci),
    )
    return {"voci": voci, "esito": esito, "quando": quando}


def _voce_integrity_check() -> dict:
    percorso = _percorso_database()
    if not percorso.is_file():
        return _voce("Integrità database", ERRORE, "database assente")
    conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
    try:
        (esito,) = conn.execute("PRAGMA integrity_check").fetchone()
    finally:
        conn.close()
    if esito == "ok":
        return _voce("Integrità database", OK, "ok")
    return _voce("Integrità database", CRITICO, "non superata", esito[:200])


def _voce_foreign_key_check() -> dict:
    percorso = _percorso_database()
    if not percorso.is_file():
        return _voce("Vincoli di integrità", ERRORE, "database assente")
    conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
    try:
        violazioni = conn.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        conn.close()
    if not violazioni:
        return _voce("Vincoli di integrità", OK, "nessuna violazione")
    return _voce("Vincoli di integrità", ERRORE, f"{len(violazioni)} violazioni",
                 "alcune righe puntano a record che non esistono più")


def _voce_backup_verificato() -> dict:
    """Documentazione della versione portfolio."""
    from data.backup import elenco_versioni

    percorso = (carica_impostazioni().get("cartella_backup") or "").strip()
    if not percorso:
        return _voce("Backup più recente", NON_CONFIGURATO, "nessuna cartella configurata")
    if not Path(percorso).is_dir():
        return _voce("Backup più recente", ERRORE, "cartella non raggiungibile")

    versioni = elenco_versioni(percorso)
    if not versioni:
        return _voce("Backup più recente", ATTENZIONE, "nessuna versione datata")

    piu_recente = versioni[0]
    if piu_recente["valida"]:
        return _voce("Backup più recente", OK, piu_recente["nome"],
                     "manifesto e impronte verificati")
    return _voce("Backup più recente", ERRORE, piu_recente["nome"],
                 "; ".join(piu_recente["problemi"])[:200])


def _voce_cartelle_aggregate() -> dict:
    impostazioni = carica_impostazioni()
    configurate = [c for c in CHIAVI_CARTELLE if (impostazioni.get(c) or "").strip()]
    if not configurate:
        return _voce("Cartelle operative", NON_CONFIGURATO, "nessuna configurata")

    problemi = []
    buone = 0
    for chiave in configurate:
        stato, valore, _ = _controlla_cartella(impostazioni[chiave])
        if stato == OK:
            buone += 1
        else:
            problemi.append(f"{_etichetta_cartella(chiave)}: {valore}")

    totale = len(configurate)
    if buone == totale:
        return _voce("Cartelle operative", OK, f"{buone}/{totale}")
    return _voce("Cartelle operative", ERRORE, f"{buone}/{totale}",
                 "; ".join(problemi)[:300])


def _voce_registro_aggregata() -> dict:
    percorso = percorso_file_log()
    if percorso is None:
        return _voce("Registro tecnico", ERRORE, "nessun file",
                     "i guasti non lasciano traccia su disco")
    if motivo_fallback():
        return _voce("Registro tecnico", ATTENZIONE, "ripiego", str(percorso.parent))

    conteggi = conteggi_registro()
    if conteggi["critical"]:
        return _voce("Registro tecnico", CRITICO,
                     f"{conteggi['critical']} CRITICAL nei file conservati")
    if conteggi["recenti"]:
        return _voce("Registro tecnico", ATTENZIONE,
                     f"{conteggi['recenti']} errori nelle ultime 24 ore")
    return _voce("Registro tecnico", OK, "attivo, nessun errore recente")


def _leggibile(byte: int) -> str:
    if byte < 1024:
        return f"{byte} B"
    if byte < 1024 ** 2:
        return f"{byte / 1024:.0f} KB"
    if byte < 1024 ** 3:
        return f"{byte / 1024 ** 2:.1f} MB"
    return f"{byte / 1024 ** 3:.2f} GB"


def _eta_leggibile(ore: float) -> str:
    if ore < 1:
        return f"{int(ore * 60)} minuti"
    if ore < 48:
        return f"{int(ore)} ore"
    return f"{int(ore / 24)} giorni"


VERSIONE = VERSIONE_APP
SCHEMA_ATTESO = SCHEMA_DATABASE
SCHEMA_MASSIMO = SCHEMA_MASSIMO_SUPPORTATO
