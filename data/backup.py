"""Documentazione della versione portfolio."""
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import date, datetime
from pathlib import Path

from config.impostazioni import (
    cartella_esiste,
    carica_impostazioni,
    percorso_file_impostazioni,
)
from config.registro import logger

_registro = logger(__name__)

NOME_FILE_BACKUP = "control_room_demo_backup.db"
NOME_FILE_BACKUP_IMPOSTAZIONI = "config_backup.json"

NOME_CARTELLA_VERSIONI = "versioni"
NOME_CARTELLA_RAPPORTI = "rapporti"
NOME_MANIFESTO = "manifesto.json"
NOME_MARCATORE_RAPPORTI = ".ultima_copia_rapporti"


INTERVALLO_VERSIONE_MINUTI = 60
VERSIONI_DA_CONSERVARE = 30

_FORMATO_NOME_VERSIONE = "%Y-%m-%d_%H%M%S"


_stato_ultimo_backup: dict | None = None


def stato_ultimo_backup() -> dict | None:
    """Documentazione della versione portfolio."""
    return _stato_ultimo_backup


def _registra_esito(riuscito: bool, motivo: str | None = None,
                    configurato: bool = True) -> bool:
    global _stato_ultimo_backup
    _stato_ultimo_backup = {
        "riuscito": riuscito,
        "configurato": configurato,
        "motivo": motivo,
        "quando": datetime.now().strftime("%d-%m-%Y %H:%M"),
    }
    return riuscito


def esegui_backup() -> bool:
    """Documentazione della versione portfolio."""
    percorso_backup = carica_impostazioni().get("cartella_backup", "")
    configurato = bool(percorso_backup.strip())
    if not cartella_esiste(percorso_backup):
        _registro.warning(
            "Backup non eseguito: cartella %s (%r)",
            "non raggiungibile" if configurato else "non configurata", percorso_backup,
        )
        return _registra_esito(
            False,
            (
                "La cartella di backup configurata non è raggiungibile. "
                "I dati sono salvati regolarmente nel programma, ma non ne viene "
                "più conservata una copia esterna."
            ) if configurato else (
                "Nessuna cartella di backup configurata: non viene conservata "
                "alcuna copia esterna dei dati."
            ),
            configurato=configurato,
        )

    cartella_backup = Path(percorso_backup)
    temporaneo = None
    try:
        temporaneo = Path(tempfile.mkdtemp(dir=cartella_backup, prefix="."))
        copia_database = temporaneo / "control_room_demo.db"
        _copia_database(_percorso_database(), copia_database)

        if not _database_integro(copia_database):
            raise ErroreBackup("la copia del database non ha superato il controllo di integrità")

        copia_impostazioni = temporaneo / "config.json"
        _copia_impostazioni(copia_impostazioni)

        if _serve_una_nuova_versione(cartella_backup):
            _crea_versione(cartella_backup, temporaneo)

        _aggiorna_copia_corrente(cartella_backup, copia_database, copia_impostazioni)
    except Exception as errore:
        _registro.error("Backup fallito verso %s", percorso_backup, exc_info=True)
        return _registra_esito(False, _motivo_per_operatore(errore))
    finally:
        if temporaneo is not None:
            _rimuovi_cartella(temporaneo)


    try:
        _copia_rapporti_incrementale(cartella_backup)
    except Exception:
        _registro.error("Copia dei rapporti non riuscita (il backup del database e' comunque valido)", exc_info=True)

    _registro.info("Backup aggiornato in %s", percorso_backup)
    return _registra_esito(True)


class ErroreBackup(Exception):
    """Documentazione della versione portfolio."""


def _motivo_per_operatore(errore: Exception) -> str:
    """Documentazione della versione portfolio."""
    if isinstance(errore, ErroreBackup):
        return f"Copia di sicurezza non completata: {errore}."
    if isinstance(errore, PermissionError):
        return (
            "Copia di sicurezza non riuscita: permesso negato sulla cartella di backup."
        )
    if isinstance(errore, OSError) and errore.errno == 28:
        return "Copia di sicurezza non riuscita: spazio insufficiente sul disco di backup."
    if isinstance(errore, OSError):
        return (
            "Copia di sicurezza non riuscita: la cartella di backup non ha risposto. "
            "Controlla che il disco o la cartella di rete siano disponibili."
        )
    return "Copia di sicurezza non riuscita per un problema imprevisto."


def _rimuovi_cartella(percorso: Path) -> None:
    """Documentazione della versione portfolio."""
    try:
        shutil.rmtree(percorso, ignore_errors=True)
    except Exception:
        _registro.warning("Cartella di lavoro non rimossa: %s", percorso, exc_info=True)


def _percorso_database() -> Path:

    from data.database import percorso_database

    return percorso_database()


def _copia_database(origine: Path, destinazione: Path) -> None:
    """Documentazione della versione portfolio."""
    sorgente = sqlite3.connect(f"file:{origine.as_posix()}?mode=ro", uri=True)
    try:
        copia = sqlite3.connect(destinazione)
        try:
            sorgente.backup(copia)
        finally:
            copia.close()
    finally:
        sorgente.close()


def _database_integro(percorso: Path) -> bool:
    """Documentazione della versione portfolio."""
    try:
        conn = sqlite3.connect(f"file:{percorso.as_posix()}?mode=ro", uri=True)
        try:
            (esito,) = conn.execute("PRAGMA integrity_check").fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        _registro.error("Controllo di integrita' non riuscito su %s", percorso, exc_info=True)
        return False
    if esito != "ok":
        _registro.error("Copia del database non integra (%s): %s", percorso, esito)
        return False
    return True


def _copia_impostazioni(destinazione: Path) -> None:
    origine = percorso_file_impostazioni()
    if origine.is_file():
        shutil.copy2(origine, destinazione)
    else:
        destinazione.write_text("{}", encoding="utf-8")


def _aggiorna_copia_corrente(
    cartella_backup: Path, copia_database: Path, copia_impostazioni: Path
) -> None:
    """Documentazione della versione portfolio."""
    os.replace(copia_database, cartella_backup / NOME_FILE_BACKUP)
    os.replace(copia_impostazioni, cartella_backup / NOME_FILE_BACKUP_IMPOSTAZIONI)


def _ora_per_nome() -> str:
    return datetime.now().strftime(_FORMATO_NOME_VERSIONE)


def _cartella_versioni(cartella_backup: Path) -> Path:
    return cartella_backup / NOME_CARTELLA_VERSIONI


def _versioni_presenti(cartella_backup: Path) -> list[Path]:
    """Documentazione della versione portfolio."""
    radice = _cartella_versioni(cartella_backup)
    if not radice.is_dir():
        return []
    return sorted(
        percorso for percorso in radice.iterdir()
        if percorso.is_dir() and not percorso.name.startswith(".")
    )


def _serve_una_nuova_versione(cartella_backup: Path) -> bool:
    """Documentazione della versione portfolio."""
    if INTERVALLO_VERSIONE_MINUTI <= 0:
        return True
    presenti = _versioni_presenti(cartella_backup)
    if not presenti:
        return True
    try:
        ultima = datetime.strptime(presenti[-1].name, _FORMATO_NOME_VERSIONE)
    except ValueError:
        return True
    trascorsi = (datetime.now() - ultima).total_seconds() / 60
    return trascorsi >= INTERVALLO_VERSIONE_MINUTI


def _crea_versione(cartella_backup: Path, temporaneo: Path) -> Path:
    """Documentazione della versione portfolio."""
    radice = _cartella_versioni(cartella_backup)
    radice.mkdir(parents=True, exist_ok=True)

    nome = _ora_per_nome()
    definitiva = radice / nome
    in_lavorazione = radice / f".{nome}"
    if definitiva.exists():
        return definitiva
    _rimuovi_cartella(in_lavorazione)
    in_lavorazione.mkdir()

    shutil.copy2(temporaneo / "control_room_demo.db", in_lavorazione / "control_room_demo.db")
    shutil.copy2(temporaneo / "config.json", in_lavorazione / "config.json")
    try:
        _scrivi_manifesto(in_lavorazione)
        os.replace(in_lavorazione, definitiva)
    except Exception:
        _rimuovi_cartella(in_lavorazione)
        raise

    _applica_retention(cartella_backup)
    return definitiva


def _applica_retention(cartella_backup: Path) -> None:
    """Documentazione della versione portfolio."""
    presenti = _versioni_presenti(cartella_backup)
    if len(presenti) <= VERSIONI_DA_CONSERVARE:
        return
    for da_togliere in presenti[: len(presenti) - VERSIONI_DA_CONSERVARE]:
        try:
            shutil.rmtree(da_togliere)
            _registro.info("Versione di backup rimossa per retention: %s", da_togliere.name)
        except OSError:
            _registro.warning("Versione non rimossa: %s", da_togliere, exc_info=True)


def _sha256(percorso: Path) -> str:
    digest = hashlib.sha256()
    with open(percorso, "rb") as file:
        for blocco in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(blocco)
    return digest.hexdigest()


def _versione_schema(percorso_database: Path) -> int | None:
    """Documentazione della versione portfolio."""
    try:
        conn = sqlite3.connect(f"file:{percorso_database.as_posix()}?mode=ro", uri=True)
        try:
            (valore,) = conn.execute("PRAGMA user_version").fetchone()
        finally:
            conn.close()
        return valore
    except sqlite3.Error:
        return None


def _scrivi_manifesto(cartella_versione: Path) -> None:
    """Documentazione della versione portfolio."""
    file_descritti = [
        {
            "nome": percorso.name,
            "dimensione": percorso.stat().st_size,
            "sha256": _sha256(percorso),
        }
        for percorso in sorted(cartella_versione.iterdir())
        if percorso.is_file()
    ]
    manifesto = {
        "creato_il": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "versione_schema": _versione_schema(cartella_versione / "control_room_demo.db"),
        "file": file_descritti,
        "nota": (
            "Copia di sicurezza di Control Room Manager Demo. Per ripristinare: chiudere il "
            "programma e ricopiare control_room_demo.db e config.json nella cartella "
            "dati_applicazione. Verificare prima le impronte sha256."
        ),
    }
    (cartella_versione / NOME_MANIFESTO).write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def verifica_versione(cartella_versione: Path | str) -> tuple[bool, list[str]]:
    """Documentazione della versione portfolio."""
    cartella_versione = Path(cartella_versione)
    problemi: list[str] = []
    percorso_manifesto = cartella_versione / NOME_MANIFESTO
    if not percorso_manifesto.is_file():
        return False, [f"manifesto assente in {cartella_versione.name}"]

    try:
        manifesto = json.loads(percorso_manifesto.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as errore:
        return False, [f"manifesto illeggibile: {errore}"]

    for descrizione in manifesto.get("file", []):
        percorso = cartella_versione / descrizione["nome"]
        if not percorso.is_file():
            problemi.append(f"{descrizione['nome']}: file mancante")
            continue
        if percorso.stat().st_size != descrizione["dimensione"]:
            problemi.append(f"{descrizione['nome']}: dimensione diversa da quella dichiarata")
            continue
        if _sha256(percorso) != descrizione["sha256"]:
            problemi.append(f"{descrizione['nome']}: contenuto diverso da quello dichiarato")
    return not problemi, problemi


def elenco_versioni(cartella_backup: Path | str, verifica: bool = True) -> list[dict]:
    """Documentazione della versione portfolio."""
    cartella_backup = Path(cartella_backup)
    elenco = []
    for percorso in reversed(_versioni_presenti(cartella_backup)):
        if verifica:
            valida, problemi = verifica_versione(percorso)
        else:
            valida, problemi = None, []
        elenco.append({
            "nome": percorso.name,
            "percorso": percorso,
            "valida": valida,
            "problemi": problemi,
        })
    return elenco


def _oggi_per_marcatore() -> str:
    return date.today().isoformat()


def _copia_rapporti_incrementale(cartella_backup: Path) -> None:
    """Documentazione della versione portfolio."""
    percorso_rapporti = carica_impostazioni().get("cartella_rapporti", "")
    if not cartella_esiste(percorso_rapporti):
        return

    destinazione = cartella_backup / NOME_CARTELLA_RAPPORTI
    marcatore = destinazione / NOME_MARCATORE_RAPPORTI
    oggi = _oggi_per_marcatore()
    if marcatore.is_file() and marcatore.read_text(encoding="utf-8").strip() == oggi:
        return

    origine = Path(percorso_rapporti)
    destinazione.mkdir(parents=True, exist_ok=True)
    copiati = 0
    for documento in origine.rglob("*.docx"):
        if not documento.is_file():
            continue
        relativo = documento.relative_to(origine)
        copia = destinazione / relativo
        if _gia_copiato(documento, copia):
            continue
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(documento, copia)
        copiati += 1

    marcatore.write_text(oggi, encoding="utf-8")
    if copiati:
        _registro.info("Copia dei rapporti: %d documenti aggiornati", copiati)


def _gia_copiato(origine: Path, copia: Path) -> bool:
    """Documentazione della versione portfolio."""
    if not copia.is_file():
        return False
    dati_origine, dati_copia = origine.stat(), copia.stat()
    return (
        dati_origine.st_size == dati_copia.st_size
        and int(dati_origine.st_mtime) == int(dati_copia.st_mtime)
    )
