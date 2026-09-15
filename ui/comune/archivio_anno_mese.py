"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.comune.icone import SIMBOLI_MODULI, SIMBOLO_CICLI, applica_icona_pulsante

from ui.tema import TESTO_ATTENUATO

MESI_ITALIANI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

NOME_SENZA_DATA = "Senza data"


class _RigaEvento(QFrame):
    """Documentazione della versione portfolio."""

    cliccata = Signal()

    def mousePressEvent(self, event):
        self.cliccata.emit()
        super().mousePressEvent(event)


class DialogoDettaglioEvento(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, titolo: str, voci: list[tuple[str, str]]):
        super().__init__(parent)
        self.setWindowTitle("Dettaglio evento")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)

        intestazione = QLabel(titolo)
        intestazione.setWordWrap(True)
        intestazione.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(intestazione)

        for etichetta, valore in voci:
            if not valore:
                continue
            riga = QLabel(f"{etichetta}: {valore}")
            riga.setWordWrap(True)
            riga.setStyleSheet(f"color: {TESTO_ATTENUATO}; font-size: 12px;")
            layout.addWidget(riga)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Close)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)


def _peso_colonna(intestazione: str) -> int:
    """Documentazione della versione portfolio."""
    return 1 if intestazione in ("DATA", "ORA", "OPERAZIONE", "CAMPO") else 2


class DialogoArchivioAnnoMese(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, titolo: str, colonne: list[tuple[str, str]], periodi,
                 carica_mese, dettaglio=None, con_senza_data: bool = False,
                 carica_senza_data=None, colonne_cicli: list[tuple[str, str]] | None = None,
                 carica_cicli=None, dettaglio_cicli=None):
        """Documentazione della versione portfolio."""
        super().__init__(parent)
        self.setWindowTitle(titolo)
        self.resize(560, 640)
        self._colonne = colonne
        self._periodi = periodi
        self._carica_mese = carica_mese
        self._dettaglio = dettaglio
        self._con_senza_data = con_senza_data
        self._carica_senza_data = carica_senza_data
        self._colonne_cicli = colonne_cicli
        self._carica_cicli = carica_cicli
        self._dettaglio_cicli = dettaglio_cicli

        layout = QVBoxLayout(self)

        if self._carica_cicli is not None:
            layout.addWidget(self._crea_selettore_modo())

        self._pagine = QStackedWidget()
        layout.addWidget(self._pagine, stretch=1)

        pulsante_chiudi = QPushButton("Chiudi")
        pulsante_chiudi.clicked.connect(self.accept)
        layout.addWidget(pulsante_chiudi)

        self._mostra_anni()

    def _crea_selettore_modo(self) -> QWidget:
        contenitore = QWidget()
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        gruppo = QButtonGroup(self)
        gruppo.setExclusive(True)

        pulsante_cronologico = QPushButton("Cronologico")
        applica_icona_pulsante(
            pulsante_cronologico, SIMBOLI_MODULI["Calendario Operativo"]
        )
        pulsante_cronologico.setCheckable(True)
        pulsante_cronologico.setChecked(True)
        pulsante_cronologico.clicked.connect(self._mostra_anni)

        pulsante_cicli = QPushButton("Cicli uscita/rientro")
        applica_icona_pulsante(pulsante_cicli, SIMBOLO_CICLI)
        pulsante_cicli.setCheckable(True)
        pulsante_cicli.clicked.connect(self._mostra_cicli)

        for pulsante in (pulsante_cronologico, pulsante_cicli):
            gruppo.addButton(pulsante)
            layout.addWidget(pulsante)
        layout.addStretch()
        return contenitore


    def _vai_a(self, pagina: QWidget):
        self._pagine.addWidget(pagina)
        self._pagine.setCurrentWidget(pagina)

    def _crea_area_scorrevole(self) -> tuple[QScrollArea, QVBoxLayout]:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        contenitore = QWidget()
        layout = QVBoxLayout(contenitore)
        layout.setSpacing(8)
        area.setWidget(contenitore)
        return area, layout

    def _crea_intestazione_livello(self, titolo: str, al_indietro) -> QHBoxLayout:
        intestazione = QHBoxLayout()
        if al_indietro is not None:
            pulsante_indietro = QPushButton("←")
            pulsante_indietro.setFixedWidth(40)
            pulsante_indietro.clicked.connect(al_indietro)
            intestazione.addWidget(pulsante_indietro)
        etichetta = QLabel(titolo)
        etichetta.setStyleSheet("font-size: 16px; font-weight: 600;")
        intestazione.addWidget(etichetta)
        intestazione.addStretch()
        return intestazione

    def _mostra_anni(self):
        coppie = self._periodi()
        anni = sorted({anno for anno, _ in coppie}, reverse=True)

        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.addLayout(self._crea_intestazione_livello("Storico — Anni", None))

        area, layout_elenco = self._crea_area_scorrevole()
        if self._con_senza_data:
            pulsante = QPushButton(NOME_SENZA_DATA)
            pulsante.clicked.connect(self._mostra_senza_data)
            layout_elenco.addWidget(pulsante)
        if not anni and not self._con_senza_data:
            etichetta = QLabel("Nessun evento nello storico.")
            etichetta.setStyleSheet(f"color: {TESTO_ATTENUATO};")
            layout_elenco.addWidget(etichetta)
        for anno in anni:
            pulsante = QPushButton(str(anno))
            pulsante.clicked.connect(lambda _, a=anno: self._mostra_mesi(a, coppie))
            layout_elenco.addWidget(pulsante)
        layout_elenco.addStretch()
        layout.addWidget(area, stretch=1)

        self._vai_a(pagina)

    def _mostra_mesi(self, anno: int, coppie: list[tuple[int, int]]):
        mesi = sorted({mese for a, mese in coppie if a == anno})

        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.addLayout(self._crea_intestazione_livello(f"Storico — {anno}", self._mostra_anni))

        area, layout_elenco = self._crea_area_scorrevole()
        for mese in mesi:
            pulsante = QPushButton(MESI_ITALIANI[mese - 1].capitalize())
            pulsante.clicked.connect(lambda _, m=mese: self._mostra_elementi(anno, m))
            layout_elenco.addWidget(pulsante)
        layout_elenco.addStretch()
        layout.addWidget(area, stretch=1)

        self._vai_a(pagina)

    def _mostra_elementi(self, anno: int, mese: int):
        nome_mese = MESI_ITALIANI[mese - 1].capitalize()
        self._apri_pagina_elementi(
            titolo=f"Storico — {nome_mese} {anno}",
            al_indietro=lambda: self._mostra_mesi(anno, self._periodi()),
            carica=lambda testo: self._carica_mese(anno, mese, testo),
            colonne=self._colonne, dettaglio=self._dettaglio,
        )

    def _mostra_senza_data(self):
        self._apri_pagina_elementi(
            titolo=f"Storico — {NOME_SENZA_DATA}",
            al_indietro=self._mostra_anni,
            carica=self._carica_senza_data,
            colonne=self._colonne, dettaglio=self._dettaglio,
        )

    def _mostra_cicli(self):
        """Documentazione della versione portfolio."""
        self._apri_pagina_elementi(
            titolo="Cicli uscita/rientro",
            al_indietro=None,
            carica=self._carica_cicli,
            colonne=self._colonne_cicli, dettaglio=self._dettaglio_cicli,
            messaggio_vuoto="Nessun ciclo registrato.",
        )

    def _apri_pagina_elementi(self, titolo: str, al_indietro, carica, colonne, dettaglio,
                              messaggio_vuoto: str = "Nessun evento in questo periodo."):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.addLayout(self._crea_intestazione_livello(titolo, al_indietro))

        campo_ricerca = QLineEdit()
        campo_ricerca.setPlaceholderText("Cerca in questo periodo...")
        layout.addWidget(campo_ricerca)

        layout.addWidget(self._crea_intestazione_colonne(colonne))

        area, layout_elenco = self._crea_area_scorrevole()
        layout.addWidget(area, stretch=1)

        def aggiorna(testo: str = ""):
            while layout_elenco.count():
                item = layout_elenco.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.hide()
                    widget.setParent(None)
                    widget.deleteLater()

            eventi = carica(testo)
            if not eventi:
                etichetta = QLabel(messaggio_vuoto)
                etichetta.setStyleSheet(f"color: {TESTO_ATTENUATO};")
                layout_elenco.addWidget(etichetta)
            for evento in eventi:
                layout_elenco.addWidget(self._crea_riga(evento, colonne, dettaglio))
            layout_elenco.addStretch()

        campo_ricerca.textChanged.connect(aggiorna)
        aggiorna()

        self._vai_a(pagina)

    def _crea_intestazione_colonne(self, colonne: list[tuple[str, str]]) -> QWidget:
        contenitore = QWidget()
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(10, 0, 10, 0)
        for intestazione, _ in colonne:
            etichetta = QLabel(intestazione)
            etichetta.setStyleSheet(
                f"color: {TESTO_ATTENUATO}; font-weight: 700; font-size: 11px;"
            )
            layout.addWidget(etichetta, stretch=_peso_colonna(intestazione))
        return contenitore

    def _crea_riga(self, evento: dict, colonne: list[tuple[str, str]], dettaglio) -> QWidget:
        riga = _RigaEvento()
        riga.setObjectName("riga_risultato_chiave")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 6, 10, 6)

        for intestazione, chiave in colonne:
            etichetta = QLabel(str(evento.get(chiave) or ""))
            etichetta.setWordWrap(True)
            if intestazione in ("OPERAZIONE", "CAMPO", "STATO"):
                etichetta.setStyleSheet("font-weight: 600;")
            layout.addWidget(etichetta, stretch=_peso_colonna(intestazione))

        if dettaglio is not None:
            riga.setCursor(Qt.PointingHandCursor)
            riga.setToolTip("Apri il dettaglio")
            riga.cliccata.connect(lambda e=evento: self._apri_dettaglio(e, dettaglio))

        return riga

    def _apri_dettaglio(self, evento: dict, dettaglio):
        titolo, voci = dettaglio(evento)
        DialogoDettaglioEvento(self, titolo, voci).exec()
