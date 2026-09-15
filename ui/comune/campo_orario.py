"""Documentazione della versione portfolio."""
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QAbstractSpinBox, QTimeEdit

from ui.tema import BLU_NAVY_SCURO, BORDO_BOTTONE, TESTO_CHIARO

_FOGLIO_DI_STILE_CAMPO_ORARIO = f"""
QTimeEdit {{
    background-color: {BLU_NAVY_SCURO};
    color: {TESTO_CHIARO};
    border: 1px solid {BORDO_BOTTONE};
    border-radius: 4px;
    padding: 5px;
}}
"""


def crea_campo_orario(valore_iniziale: str | None = None) -> QTimeEdit:
    """Documentazione della versione portfolio."""
    campo = QTimeEdit()
    campo.setDisplayFormat("HH:mm")
    campo.setButtonSymbols(QAbstractSpinBox.NoButtons)
    campo.setWrapping(True)
    campo.setStyleSheet(_FOGLIO_DI_STILE_CAMPO_ORARIO)

    ora = QTime.fromString((valore_iniziale or "").strip(), "HH:mm")
    campo.setTime(ora if ora.isValid() else QTime(0, 0))
    return campo


def testo_orario(campo: QTimeEdit) -> str:
    """Documentazione della versione portfolio."""
    return campo.time().toString("HH:mm")
