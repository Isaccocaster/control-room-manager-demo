"""Documentazione della versione portfolio."""
import logging
import logging.handlers
import os
import platform
import re
import sys
import zipfile
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

NOME_LOGGER_RADICE = "control_room_demo"
NOME_CARTELLA_LOG = "log"
NOME_FILE_LOG = "control_room_demo.log"


DIMENSIONE_MASSIMA_BYTE = 2 * 1024 * 1024
COPIE_STORICHE = 5

FORMATO = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
FORMATO_ORA = "%Y-%m-%d %H:%M:%S"


_ATTRIBUTO_HANDLER = "_control_room_demo_handler"

_percorso_file_log: Path | None = None
_motivo_fallback: str | None = None


_fornitore_versione_libreria_ui: Callable[[], str] | None = None


def cartella_log_predefinita() -> Path:
    """Documentazione della versione portfolio."""
    override = os.environ.get("CONTROL_ROOM_DEMO_DATA_DIR")
    if override:
        return Path(override) / NOME_CARTELLA_LOG

    if getattr(sys, "frozen", False):
        base = os.environ.get("PROGRAMDATA") or os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "Control Room Manager Demo" / NOME_CARTELLA_LOG
        return Path.home() / "Control Room Manager Demo" / NOME_CARTELLA_LOG

    from config.impostazioni import cartella_dati_applicazione

    return cartella_dati_applicazione() / NOME_CARTELLA_LOG


def percorso_file_log() -> Path | None:
    """Documentazione della versione portfolio."""
    return _percorso_file_log


def motivo_fallback() -> str | None:
    """Documentazione della versione portfolio."""
    return _motivo_fallback


def configura(cartella: Path | str | None = None, livello: int = logging.INFO) -> Path | None:
    """Documentazione della versione portfolio."""
    global _percorso_file_log, _motivo_fallback

    radice = logging.getLogger(NOME_LOGGER_RADICE)
    radice.setLevel(livello)


    radice.propagate = False

    _rimuovi_handler_precedenti(radice)
    _percorso_file_log = None
    _motivo_fallback = None

    richiesta = Path(cartella) if cartella is not None else cartella_log_predefinita()
    candidate = [(richiesta, None)]

    ripiego = Path(os.environ.get("TEMP") or os.environ.get("TMP") or Path.home()) / "Control Room Manager Demo" / NOME_CARTELLA_LOG
    if ripiego != richiesta:
        candidate.append((ripiego, f"cartella preferita non scrivibile: {richiesta}"))

    for destinazione, motivo in candidate:
        handler = _crea_handler_file(destinazione)
        if handler is not None:
            radice.addHandler(handler)
            _percorso_file_log = destinazione / NOME_FILE_LOG
            _motivo_fallback = motivo
            if motivo:
                radice.warning("Registro su cartella di ripiego — %s", motivo)
            return _percorso_file_log


    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(FORMATO, FORMATO_ORA))
    setattr(handler, _ATTRIBUTO_HANDLER, True)
    radice.addHandler(handler)
    _motivo_fallback = f"nessuna cartella di log scrivibile (provate: {richiesta}, {ripiego})"
    radice.warning("Registro solo su stderr — %s", _motivo_fallback)
    return None


def _rimuovi_handler_precedenti(radice: logging.Logger) -> None:
    """Documentazione della versione portfolio."""
    for handler in list(radice.handlers):
        if getattr(handler, _ATTRIBUTO_HANDLER, False):
            radice.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass


def _crea_handler_file(cartella: Path) -> logging.Handler | None:
    """Documentazione della versione portfolio."""
    try:
        cartella.mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            cartella / NOME_FILE_LOG,
            maxBytes=DIMENSIONE_MASSIMA_BYTE,
            backupCount=COPIE_STORICHE,
            encoding="utf-8",
        )
    except OSError:
        return None

    handler.setFormatter(logging.Formatter(FORMATO, FORMATO_ORA))
    setattr(handler, _ATTRIBUTO_HANDLER, True)
    return handler


def logger(nome: str) -> logging.Logger:
    """Documentazione della versione portfolio."""
    return logging.getLogger(f"{NOME_LOGGER_RADICE}.{nome}")


def registra_eccezione_non_gestita(tipo, valore, traccia) -> None:
    """Documentazione della versione portfolio."""
    logging.getLogger(f"{NOME_LOGGER_RADICE}.eccezione").critical(
        "Eccezione non gestita: %s: %s", tipo.__name__, valore,
        exc_info=(tipo, valore, traccia),
    )


def registra_avvio() -> None:
    """Documentazione della versione portfolio."""
    registro = logger("avvio")
    registro.info("=" * 70)
    registro.info("Control Room Manager Demo %s — avvio", versione_applicazione())
    registro.info(
        "Python %s · %s %s · %s",
        platform.python_version(), platform.system(), platform.release(),
        "eseguibile congelato" if getattr(sys, "frozen", False) else "avvio da sorgente",
    )
    registro.info("Qt/PySide6: %s", _versione_libreria_ui())
    registro.info("Cartella dati: %s", _cartella_dati_per_registro())
    registro.info(
        "File di registro: %s%s",
        _percorso_file_log or "nessuno (solo stderr)",
        f"  [RIPIEGO: {_motivo_fallback}]" if _motivo_fallback else "",
    )


def registra_schema(versione_trovata: int) -> None:
    """Documentazione della versione portfolio."""
    from config.versione import SCHEMA_DATABASE, SCHEMA_MASSIMO_SUPPORTATO
    from data.schema import stato_compatibilita

    logger("avvio").info(
        "Schema database: rilevato %s · atteso %d · massimo supportato %d · %s",
        versione_trovata, SCHEMA_DATABASE, SCHEMA_MASSIMO_SUPPORTATO,
        stato_compatibilita(versione_trovata),
    )


def _cartella_dati_per_registro() -> str:
    try:
        from config.impostazioni import cartella_dati_applicazione

        return str(cartella_dati_applicazione())
    except Exception:
        return "non determinabile"


def registra_avvio_completato() -> None:
    logger("avvio").info("Avvio completato: finestra principale pronta")


def registra_chiusura(motivo: str = "chiusura normale") -> None:
    logger("chiusura").info("Control Room Manager Demo — %s", motivo)


def versione_applicazione() -> str:
    """Documentazione della versione portfolio."""
    try:
        from config.versione import ETICHETTA_VERSIONE

        return ETICHETTA_VERSIONE
    except Exception:
        return "non disponibile"


def imposta_fornitore_versione_libreria_ui(fornitore: Callable[[], str] | None) -> None:
    """Documentazione della versione portfolio."""
    global _fornitore_versione_libreria_ui
    _fornitore_versione_libreria_ui = fornitore


def _versione_libreria_ui() -> str:
    if _fornitore_versione_libreria_ui is None:
        return "non disponibile"
    try:
        return _fornitore_versione_libreria_ui()
    except Exception:
        return "non disponibile"


_INIZIO_RIGA = re.compile(
    r"^(?P<quando>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<livello>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+"
    r"(?P<origine>\S+)"
)

ORE_RECENTI = 24


def conteggi_registro(ore_recenti: int = ORE_RECENTI) -> dict:
    """Documentazione della versione portfolio."""
    esito = {
        "warning": 0, "error": 0, "critical": 0, "recenti": 0,
        "ultimo_error": None, "ultimo_critical": None,
        "origine_ultimo_error": None, "origine_ultimo_critical": None,
        "file_letti": 0, "file_illeggibili": 0, "disponibile": False,
    }
    file_registro = _file_di_registro()
    if not file_registro:
        return esito

    esito["disponibile"] = True
    soglia = datetime.now() - timedelta(hours=ore_recenti)

    for percorso in file_registro:
        try:


            testo = percorso.read_text(encoding="utf-8", errors="replace")
        except OSError:
            esito["file_illeggibili"] += 1
            _registro_interno().warning("Registro illeggibile: %s", percorso, exc_info=True)
            continue

        esito["file_letti"] += 1
        for riga in testo.splitlines():
            trovato = _INIZIO_RIGA.match(riga)
            if trovato is None:
                continue

            livello = trovato.group("livello")
            if livello not in ("WARNING", "ERROR", "CRITICAL"):
                continue

            quando = trovato.group("quando")


            momento = _momento_di(quando)
            if momento is None:
                continue

            esito[livello.lower()] += 1
            origine = trovato.group("origine")

            if livello == "ERROR":
                if esito["ultimo_error"] is None or quando > esito["ultimo_error"]:
                    esito["ultimo_error"] = quando
                    esito["origine_ultimo_error"] = origine
            elif livello == "CRITICAL":
                if esito["ultimo_critical"] is None or quando > esito["ultimo_critical"]:
                    esito["ultimo_critical"] = quando
                    esito["origine_ultimo_critical"] = origine

            if livello in ("ERROR", "CRITICAL") and momento >= soglia:
                esito["recenti"] += 1

    return esito


def _momento_di(quando: str) -> datetime | None:
    """Documentazione della versione portfolio."""
    try:
        return datetime.strptime(quando, FORMATO_ORA)
    except ValueError:
        return None


def _registro_interno():
    return logging.getLogger(f"{NOME_LOGGER_RADICE}.registro")


ESTENSIONI_VIETATE = (".db", ".docx", ".dotx", ".xlsx", ".xlsm", ".pdf", ".doc", ".xls")


def raccogli_diagnostica(destinazione: Path | str) -> Path:
    """Documentazione della versione portfolio."""
    destinazione = Path(destinazione)
    if destinazione.is_dir():
        adesso = datetime.now().strftime("%Y%m%d_%H%M%S")
        destinazione = destinazione / f"diagnostica_control_room_demo_{adesso}.zip"
    destinazione.parent.mkdir(parents=True, exist_ok=True)

    registro = logger("diagnostica")
    with zipfile.ZipFile(destinazione, "w", zipfile.ZIP_DEFLATED) as pacchetto:
        pacchetto.writestr("contenuto.txt", _manifesto())
        pacchetto.writestr("informazioni.txt", _informazioni_ambiente())
        pacchetto.writestr("configurazione.txt", _stato_configurazione())
        pacchetto.writestr("database.txt", _diagnostica_database())
        for file_log in _file_di_registro():
            pacchetto.write(file_log, f"log/{file_log.name}")

    registro.info("Diagnostica esportata in %s", destinazione)
    return destinazione


def _file_di_registro() -> list[Path]:
    """Documentazione della versione portfolio."""
    if _percorso_file_log is None:
        return []
    cartella = _percorso_file_log.parent
    if not cartella.is_dir():
        return []
    return sorted(
        percorso for percorso in cartella.iterdir()
        if percorso.is_file()
        and percorso.name.startswith(NOME_FILE_LOG)
        and not percorso.name.lower().endswith(ESTENSIONI_VIETATE)
    )


def _manifesto() -> str:
    return (
        "PACCHETTO DIAGNOSTICO — Control Room Manager Demo\n"
        "====================================\n\n"
        "Generato il " + datetime.now().strftime("%d-%m-%Y %H:%M") + "\n\n"
        "CONTENUTO\n"
        "  informazioni.txt   ambiente di esecuzione (sistema, runtime, versione)\n"
        "  configurazione.txt stato delle cartelle configurate\n"
        "  database.txt       controllo di integrita' e conteggi per tabella\n"
        "  log/               registro tecnico e sue copie storiche\n\n"
        "NON INCLUSO, DELIBERATAMENTE\n"
        "  il database operativo (control_room_demo.db)\n"
        "  i rapporti giornalieri (.docx) e i prospetti (.xlsx)\n"
        "  qualunque contenuto scritto dagli operatori\n\n"
        "Il pacchetto serve a capire perche' il programma non ha funzionato,\n"
        "non a trasferire i dati dell'esercizio.\n\n"
        "NOTA: i percorsi delle cartelle sono inclusi perche' senza di essi\n"
        "un errore di percorso non e' diagnosticabile. Contengono il nome\n"
        "dell'utente Windows della postazione.\n"
    )


def _informazioni_ambiente() -> str:
    righe = [
        "AMBIENTE DI ESECUZIONE",
        "======================",
        f"Data                 : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        f"Versione Demo         : {versione_applicazione()}",
        f"Python               : {platform.python_version()}",
        f"PySide6              : {_versione_libreria_ui()}",
        f"Sistema              : {platform.system()} {platform.release()} ({platform.machine()})",
        f"Eseguibile congelato : {'si' if getattr(sys, 'frozen', False) else 'no'}",
        f"Cartella dati        : {_cartella_dati_per_registro()}",
        f"Cartella di log      : {_percorso_file_log.parent if _percorso_file_log else 'nessuna'}",
        f"Ripiego attivo       : {_motivo_fallback or 'no'}",
    ]
    righe += _righe_schema()
    righe += _righe_registro()
    righe += _righe_backup()
    righe += _righe_ultimo_controllo()
    return "\n".join(righe) + "\n"


def _righe_schema() -> list[str]:
    """Documentazione della versione portfolio."""
    try:
        import sqlite3

        from config.impostazioni import cartella_dati_applicazione
        from config.versione import SCHEMA_DATABASE, SCHEMA_MASSIMO_SUPPORTATO
        from data.database import NOME_FILE_DATABASE
        from data.schema import stato_compatibilita

        percorso = cartella_dati_applicazione() / NOME_FILE_DATABASE
        if not percorso.is_file():
            trovata, stato = "nessun database", "non applicabile"
        else:
            conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
            try:
                (valore,) = conn.execute("PRAGMA user_version").fetchone()
            finally:
                conn.close()
            trovata, stato = valore, stato_compatibilita(int(valore))
        return [
            "",
            f"Schema atteso        : {SCHEMA_DATABASE}",
            f"Schema max supportato: {SCHEMA_MASSIMO_SUPPORTATO}",
            f"Schema rilevato      : {trovata}",
            f"Compatibilita'       : {stato}",
        ]
    except Exception as errore:
        return ["", f"Schema               : non determinabile ({type(errore).__name__})"]


def _righe_registro() -> list[str]:
    """Documentazione della versione portfolio."""
    try:
        conteggi = conteggi_registro()
        return [
            "",
            "REGISTRO TECNICO (solo file conservati)",
            f"  File letti         : {conteggi['file_letti']}"
            + (f" (illeggibili: {conteggi['file_illeggibili']})"
               if conteggi["file_illeggibili"] else ""),
            f"  WARNING            : {conteggi['warning']}",
            f"  ERROR              : {conteggi['error']}",
            f"  CRITICAL           : {conteggi['critical']}",
            f"  ERROR+CRITICAL 24h : {conteggi['recenti']}",
            f"  Ultimo ERROR       : {conteggi['ultimo_error'] or 'nessuno'}"
            + (f"  [{conteggi['origine_ultimo_error']}]"
               if conteggi["origine_ultimo_error"] else ""),
            f"  Ultimo CRITICAL    : {conteggi['ultimo_critical'] or 'nessuno'}"
            + (f"  [{conteggi['origine_ultimo_critical']}]"
               if conteggi["origine_ultimo_critical"] else ""),
        ]
    except Exception as errore:
        return ["", f"Registro             : non leggibile ({type(errore).__name__})"]


def _righe_backup() -> list[str]:
    try:
        from data.backup import stato_ultimo_backup

        stato = stato_ultimo_backup()
        if stato is None:
            return ["", "Backup               : non ancora tentato in questa sessione"]
        return [
            "",
            "BACKUP (ultimo tentativo di questa sessione)",
            f"  Riuscito           : {'si' if stato['riuscito'] else 'no'}",
            f"  Configurato        : {'si' if stato['configurato'] else 'no'}",
            f"  Quando             : {stato['quando']}",
            f"  Motivo             : {stato['motivo'] or '-'}",
        ]
    except Exception as errore:
        return ["", f"Backup               : non determinabile ({type(errore).__name__})"]


def _righe_ultimo_controllo() -> list[str]:
    """Documentazione della versione portfolio."""
    try:
        from data.stato_sistema import ultimo_controllo_approfondito

        ultimo = ultimo_controllo_approfondito()
        if ultimo is None:
            return ["", "Ultimo controllo approfondito: nessuno in questa sessione"]
        return [
            "",
            f"Ultimo controllo approfondito: {ultimo['quando']} — {ultimo['esito']}",
        ]
    except Exception as errore:
        return ["", f"Ultimo controllo     : non determinabile ({type(errore).__name__})"]


def _stato_configurazione() -> str:
    """Documentazione della versione portfolio."""
    righe = ["STATO DELLE CARTELLE CONFIGURATE", "================================", ""]
    try:
        from config.impostazioni import CHIAVI_CARTELLE, carica_impostazioni

        impostazioni = carica_impostazioni()
    except Exception as errore:
        return "\n".join(righe) + f"Impossibile leggere la configurazione: {errore}\n"

    for chiave in CHIAVI_CARTELLE:
        percorso = impostazioni.get(chiave, "")
        if not percorso:
            stato = "NON CONFIGURATA"
        elif not Path(percorso).is_dir():
            stato = "NON RAGGIUNGIBILE"
        elif not os.access(percorso, os.W_OK):
            stato = "SOLA LETTURA"
        else:
            stato = "ok"
        righe.append(f"{chiave:38} {stato:18} {percorso}")
    return "\n".join(righe) + "\n"


def _diagnostica_database() -> str:
    """Documentazione della versione portfolio."""
    righe = ["CONTROLLO DEL DATABASE", "======================", ""]
    try:
        import sqlite3

        from config.impostazioni import cartella_dati_applicazione
        from data.database import NOME_FILE_DATABASE

        percorso = cartella_dati_applicazione() / NOME_FILE_DATABASE
        righe.append(f"File      : {percorso}")
        if not percorso.is_file():
            righe.append("Il file del database non esiste.")
            return "\n".join(righe) + "\n"
        righe.append(f"Dimensione: {percorso.stat().st_size / 1024:.1f} KB")

        conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
        try:
            (integrita,) = conn.execute("PRAGMA integrity_check").fetchone()
            righe.append(f"integrity_check  : {integrita}")
            righe.append(f"foreign_key_check: {len(conn.execute('PRAGMA foreign_key_check').fetchall())} violazioni")
            for pragma in ("user_version", "journal_mode", "page_size"):
                (valore,) = conn.execute(f"PRAGMA {pragma}").fetchone()
                righe.append(f"{pragma:17}: {valore}")
            righe.append("")
            righe.append("Righe per tabella (solo conteggi, nessun contenuto):")
            tabelle = [
                r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )
            ]
            for tabella in tabelle:
                (quante,) = conn.execute(f'SELECT COUNT(*) FROM "{tabella}"').fetchone()
                righe.append(f"  {tabella:30} {quante:8}")
        finally:
            conn.close()
    except Exception as errore:
        righe.append(f"Controllo non riuscito: {type(errore).__name__}: {errore}")
    return "\n".join(righe) + "\n"
