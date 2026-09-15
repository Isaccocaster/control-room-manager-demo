"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.comune.icone import pixmap_simbolo
from ui.tema import (
    FOGLIO_DI_STILE_SIDEBAR,
    LARGHEZZA_SIDEBAR_COMPATTA,
    LARGHEZZA_SIDEBAR_ESTESA,
)


LARGHEZZA_FINESTRA_MINIMA_ESTESA = 1200

MOTIVO_EDITOR = "editor"
MOTIVO_FINESTRA_STRETTA = "finestra_stretta"

_COLORE_ICONA = "#B8C4D9"
_COLORE_ICONA_ATTIVA = "#C0E3FF"
_COLORE_PUNTO = "#FF8A73"


SIMBOLO_HOME = '<path d="M4 15L16 4l12 11 M8 13v14h16V13 M13 27v-8h6v8"/>'

_SIMBOLO_CHEVRON_SINISTRA = '<path d="M20 8l-8 8 8 8"/>'
_SIMBOLO_CHEVRON_DESTRA = '<path d="M12 8l8 8-8 8"/>'

_DIMENSIONE_ICONA = 22


def _icona(simbolo: str, colore: str, con_punto: bool) -> QPixmap:
    """Documentazione della versione portfolio."""
    return pixmap_simbolo(
        simbolo, _DIMENSIONE_ICONA, colore,
        _COLORE_PUNTO if con_punto else None,
    )


class _VoceSidebar(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, nome: str, simbolo: str, al_click):
        super().__init__()
        self.setObjectName("voce_sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("attiva", "false")
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)

        self._nome = nome
        self._simbolo = simbolo
        self._al_click = al_click
        self._attiva = False
        self._compatta = False
        self._numero = 0
        self._etichetta_badge = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 0, 12, 0)
        layout.setSpacing(12)

        self._icona = QLabel()
        self._icona.setFixedSize(_DIMENSIONE_ICONA, _DIMENSIONE_ICONA)
        self._icona.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._icona)

        self._testo = QLabel(nome)
        self._testo.setObjectName("etichetta_voce_sidebar")
        layout.addWidget(self._testo, stretch=1)

        self._badge = QLabel()
        self._badge.setObjectName("badge_voce_sidebar")
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setMinimumSize(26, 24)
        self._badge.setMaximumHeight(24)
        self._badge.hide()
        layout.addWidget(self._badge)

        self._ridisegna_icona()
        self._aggiorna_suggerimento()

    @property
    def nome(self) -> str:
        return self._nome

    def mousePressEvent(self, evento):
        self._al_click(self._nome)
        super().mousePressEvent(evento)

    def imposta_attiva(self, attiva: bool):
        if attiva == self._attiva:
            return
        self._attiva = attiva


        self.setProperty("attiva", "true" if attiva else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._ridisegna_icona()

    def imposta_badge(self, numero: int, etichetta: str):
        if numero == self._numero and etichetta == self._etichetta_badge:
            return
        self._numero = numero
        self._etichetta_badge = etichetta
        self._badge.setText(str(numero))
        self._aggiorna_visibilita_badge()
        self._ridisegna_icona()
        self._aggiorna_suggerimento()

    def imposta_compatta(self, compatta: bool):
        self._compatta = compatta
        self._testo.setVisible(not compatta)


        if compatta:
            self.layout().setContentsMargins(0, 0, 0, 0)
        else:
            self.layout().setContentsMargins(9, 0, 12, 0)
        self._aggiorna_visibilita_badge()
        self._ridisegna_icona()

    def _aggiorna_visibilita_badge(self):
        self._badge.setVisible(self._numero > 0 and not self._compatta)

    def _ridisegna_icona(self):


        con_punto = self._numero > 0 and self._compatta
        colore = _COLORE_ICONA_ATTIVA if self._attiva else _COLORE_ICONA
        self._icona.setPixmap(_icona(self._simbolo, colore, con_punto))

    def _aggiorna_suggerimento(self):
        if self._numero > 0 and self._etichetta_badge:
            self.setToolTip(f"{self._nome} — {self._numero} {self._etichetta_badge}")
        else:
            self.setToolTip(self._nome)


class SidebarModuli(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, voci: list[str], simboli: dict[str, str], al_click_voce,
                 nome_home: str, voci_trasversali: tuple = (), voci_in_fondo: tuple = ()):
        super().__init__()
        self.setObjectName("sidebar_moduli")
        self.setStyleSheet(FOGLIO_DI_STILE_SIDEBAR)
        self.setFixedWidth(LARGHEZZA_SIDEBAR_ESTESA)

        self._compatta_scelta = False
        self._motivi_compatta: set[str] = set()
        self._voci: dict[str, _VoceSidebar] = {}
        self._al_cambio_stato = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        area = QScrollArea()
        area.setObjectName("area_sidebar")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        area.viewport().setObjectName("viewport_sidebar")

        contenuto = QWidget()
        contenuto.setObjectName("contenuto_sidebar")
        self._layout_voci = QVBoxLayout(contenuto)
        self._layout_voci.setContentsMargins(8, 12, 8, 8)
        self._layout_voci.setSpacing(4)

        self._aggiungi_voce(nome_home, simboli, al_click_voce)
        for nome in voci:
            self._aggiungi_voce(nome, simboli, al_click_voce)

        if voci_trasversali:
            self._titolo_gruppo = self._aggiungi_separatore("TRASVERSALE")
            for nome in voci_trasversali:
                self._aggiungi_voce(nome, simboli, al_click_voce)

        self._layout_voci.addStretch()
        area.setWidget(contenuto)
        layout.addWidget(area, stretch=1)


        fondo = QWidget()
        fondo.setObjectName("fondo_sidebar")
        layout_fondo = QVBoxLayout(fondo)
        layout_fondo.setContentsMargins(8, 4, 8, 10)
        layout_fondo.setSpacing(4)


        self._layout_fondo = layout_fondo

        separatore = QFrame()
        separatore.setObjectName("separatore_sidebar")
        separatore.setFixedHeight(1)
        layout_fondo.addWidget(separatore)
        layout_fondo.addSpacing(4)

        for nome in voci_in_fondo:
            voce = _VoceSidebar(nome, simboli.get(nome, SIMBOLO_HOME), al_click_voce)
            self._voci[nome] = voce
            layout_fondo.addWidget(voce)

        self._voce_riduci = _VoceSidebar("Riduci menu", _SIMBOLO_CHEVRON_SINISTRA,
                                         lambda _: self.alterna_compatta())
        layout_fondo.addWidget(self._voce_riduci)

        layout.addWidget(fondo)
        self._applica_stato()


    def _aggiungi_voce(self, nome: str, simboli: dict, al_click):
        simbolo = SIMBOLO_HOME if nome not in simboli else simboli[nome]
        voce = _VoceSidebar(nome, simbolo, al_click)
        self._voci[nome] = voce
        self._layout_voci.addWidget(voce)

    def _aggiungi_separatore(self, testo: str) -> QWidget:
        contenitore = QWidget()
        contenitore.setObjectName("fondo_sidebar")
        riga = QHBoxLayout(contenitore)
        riga.setContentsMargins(12, 12, 8, 4)
        riga.setSpacing(8)

        titolo = QLabel(testo)
        titolo.setObjectName("titolo_gruppo_sidebar")
        riga.addWidget(titolo)

        linea = QFrame()
        linea.setObjectName("separatore_sidebar")
        linea.setFixedHeight(1)
        riga.addWidget(linea, stretch=1)

        self._layout_voci.addWidget(contenitore)
        return contenitore


    def e_compatta(self) -> bool:
        """Documentazione della versione portfolio."""
        return self._compatta_scelta or bool(self._motivi_compatta)

    def alterna_compatta(self):
        if self._motivi_compatta:
            return
        self._compatta_scelta = not self._compatta_scelta
        self._applica_stato()

    def imposta_compatta(self, compatta: bool):
        self._compatta_scelta = compatta
        self._applica_stato()

    def forza_compatta(self, motivo: str, attiva: bool):
        """Documentazione della versione portfolio."""
        prima = bool(self._motivi_compatta)
        if attiva:
            self._motivi_compatta.add(motivo)
        else:
            self._motivi_compatta.discard(motivo)
        if bool(self._motivi_compatta) != prima:
            self._applica_stato()

    def _applica_stato(self):
        compatta = self.e_compatta()
        self.setFixedWidth(LARGHEZZA_SIDEBAR_COMPATTA if compatta else LARGHEZZA_SIDEBAR_ESTESA)
        for voce in self._voci.values():
            voce.imposta_compatta(compatta)
        self._voce_riduci.imposta_compatta(compatta)
        self._voce_riduci._testo.setText("Espandi menu" if compatta else "Riduci menu")
        self._voce_riduci._simbolo = (
            _SIMBOLO_CHEVRON_DESTRA if compatta else _SIMBOLO_CHEVRON_SINISTRA
        )
        self._voce_riduci._ridisegna_icona()
        self._voce_riduci._aggiorna_suggerimento()


        self._voce_riduci.setVisible(not self._motivi_compatta)
        if hasattr(self, "_titolo_gruppo"):
            self._titolo_gruppo.setVisible(not compatta)
        if self._al_cambio_stato is not None:
            self._al_cambio_stato()


    def imposta_attivo(self, nome: str | None):
        for nome_voce, voce in self._voci.items():
            voce.imposta_attiva(nome_voce == nome)

    def aggiorna_badge(self, nome: str, numero: int, etichetta: str):
        voce = self._voci.get(nome)
        if voce is not None:
            voce.imposta_badge(numero, etichetta)

    def aggancia_in_fondo(self, widget: QWidget):
        """Documentazione della versione portfolio."""
        self._layout_fondo.insertWidget(0, widget)

    def sgancia(self, widget: QWidget):
        """Documentazione della versione portfolio."""
        self._layout_fondo.removeWidget(widget)

    def imposta_osservatore_stato(self, callback):
        """Documentazione della versione portfolio."""
        self._al_cambio_stato = callback

    def adatta_alla_larghezza(self, larghezza_finestra: int):
        """Documentazione della versione portfolio."""
        self.forza_compatta(
            MOTIVO_FINESTRA_STRETTA, larghezza_finestra < LARGHEZZA_FINESTRA_MINIMA_ESTESA
        )
