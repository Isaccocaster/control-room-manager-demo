"""Documentazione della versione portfolio."""

from pathlib import Path

from PySide6.QtWidgets import QFrame, QVBoxLayout

from ui.anagrafica_operatori.stile import FOGLIO_DI_STILE_ANAGRAFICA_OPERATORI
from ui.impostazioni.gestione_operatori import PannelloGestioneOperatori
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO


PERCORSO_FOTO_SFONDO = (
    Path(__file__).parent.parent / "assets" / "images" / "demo_anagrafica_operatori.jpg"
)


class SchermataAnagraficaOperatori(PaginaConSfondo):
    """Documentazione della versione portfolio."""

    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, HOME_OPACITA_VELO)
        self.setObjectName("anagrafica_operatori_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_ANAGRAFICA_OPERATORI)


        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(24, 16, 24, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_anagrafica_operatori")
        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(24, 24, 24, 24)

        self.contenuto = PannelloGestioneOperatori(pannello)
        layout_pannello.addWidget(self.contenuto, stretch=1)
        layout_esterno.addWidget(pannello, stretch=1)
