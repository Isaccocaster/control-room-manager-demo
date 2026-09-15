"""Documentazione della versione portfolio."""
import re


VERSIONE_APP = "0.1.0"
ETICHETTA_VERSIONE = f"{VERSIONE_APP} (portfolio demo)"

SCHEMA_DATABASE = 1
SCHEMA_MASSIMO_SUPPORTATO = SCHEMA_DATABASE
SCHEMA_NON_NUMERATO = 0

_FORMA_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def versione_valida(versione: str) -> bool:
    """Documentazione della versione portfolio."""
    return bool(_FORMA_SEMVER.match(versione or ""))


def parti_versione(versione: str = VERSIONE_APP) -> tuple[int, int, int]:
    """Documentazione della versione portfolio."""
    if not versione_valida(versione):
        raise ValueError(f"Versione non valida: {versione!r} (attesa MAJOR.MINOR.PATCH)")
    maggiore, minore, correzione = versione.split(".")
    return int(maggiore), int(minore), int(correzione)


def e_pre_produzione(versione: str = VERSIONE_APP) -> bool:
    """Documentazione della versione portfolio."""
    return parti_versione(versione)[0] == 0
