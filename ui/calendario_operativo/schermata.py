"""Documentazione della versione portfolio."""
from pathlib import Path

from PySide6.QtCore import QDate, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPalette, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from data.calendario_operativo import (
    MODULO_PASSAGGIO_CONSEGNE,
    MODULO_RAPPORTO_GIORNALIERO,
    eventi_del_giorno,
    eventi_per_modulo,
    giorni_con_eventi,
    moduli_disponibili,
)
from ui.comune.archivio_anno_mese import DialogoDettaglioEvento
from ui.comune.icone import SIMBOLI_MODULI, pixmap_simbolo
from ui.comune.riga_scorrevole import riga_scorrevole
from ui.passaggio_consegne.panel import NAVY_SU_ORO, ORO_IMPORTANTE, icona_priorita
from ui.sfondo import PaginaConSfondo
from ui.tema import (
    ACCENTO_CALENDARIO,
    FOGLIO_DI_STILE_CALENDARIO,
    HOME_OPACITA_VELO,
    INTESTAZIONE_CALENDARIO,
    SFONDO_CALENDARIO,
    SFONDO_GIORNO_CON_EVENTI,
    TESTO_ATTENUATO,
    TESTO_CALENDARIO,
    TESTO_CALENDARIO_SPENTO,
)

TUTTI_I_MODULI = "Tutti i moduli"
PERCORSO_FOTO_SFONDO = (
    Path(__file__).parent.parent / "assets" / "images" / "demo_calendario_operativo.jpg"
)

MESI_ITALIANI = [
    "GENNAIO", "FEBBRAIO", "MARZO", "APRILE", "MAGGIO", "GIUGNO",
    "LUGLIO", "AGOSTO", "SETTEMBRE", "OTTOBRE", "NOVEMBRE", "DICEMBRE",
]

ORA_NON_REGISTRATA = "Ora non registrata"

PAGINA_CALENDARIO = 0
PAGINA_GIORNATA = 1


LARGHEZZA_MASSIMA_ANTEPRIMA = 300


ALTEZZA_RIGA_NOMI_GIORNI = 34


def data_da_qdate(qdate: QDate) -> str:
    """Documentazione della versione portfolio."""
    return qdate.toString("dd-MM-yyyy")


def qdate_da_data(data: str) -> QDate:
    return QDate.fromString(data, "dd-MM-yyyy")


def _titolo_giornata(data: str) -> str:
    qdate = qdate_da_data(data)
    if not qdate.isValid():
        return data
    return f"{qdate.day():02d} {MESI_ITALIANI[qdate.month() - 1]} {qdate.year()}"


def _pixmap_modulo(nome: str, lato: int = 18):
    """Documentazione della versione portfolio."""
    if nome == MODULO_PASSAGGIO_CONSEGNE:
        return icona_priorita(lato, ORO_IMPORTANTE, NAVY_SU_ORO)
    simbolo = SIMBOLI_MODULI.get(nome, SIMBOLI_MODULI["Calendario Operativo"])
    return pixmap_simbolo(simbolo, lato, "#9FC8F2")


def _icona_modulo(nome: str, lato: int = 18) -> QIcon:
    return QIcon(_pixmap_modulo(nome, lato))


def _mese_anno(qdate: QDate) -> str:
    return f"{MESI_ITALIANI[qdate.month() - 1]} {qdate.year()}"


class _CalendarioSoloMeseCorrente(QCalendarWidget):
    """Documentazione della versione portfolio."""

    def paintCell(self, painter, rettangolo, data: QDate):
        if data.month() != self.monthShown() or data.year() != self.yearShown():
            painter.fillRect(rettangolo, QColor(SFONDO_CALENDARIO))
            return
        super().paintCell(painter, rettangolo, data)


class _RigaEvento(QFrame):
    """Documentazione della versione portfolio."""

    cliccata = Signal()

    def __init__(self, evento: dict):
        super().__init__()
        self.setObjectName("riga_risultato_chiave")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        ora = QLabel(evento["ora"] or "—")
        ora.setFixedWidth(52)
        ora.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        ora.setStyleSheet("font-weight: 600;" if evento["ora"] else f"color: {TESTO_ATTENUATO};")
        layout.addWidget(ora)

        testi = QVBoxLayout()
        testi.setSpacing(2)

        prima_riga = QLabel(f"{evento['tipo_evento']}   {evento['titolo']}")
        prima_riga.setWordWrap(True)
        testi.addWidget(prima_riga)

        sotto = evento["descrizione"] or ""
        if not evento["ora"]:

            sotto = f"{sotto} · {ORA_NON_REGISTRATA}" if sotto else ORA_NON_REGISTRATA
        if sotto:
            seconda_riga = QLabel(sotto)
            seconda_riga.setWordWrap(True)
            seconda_riga.setStyleSheet(f"color: {TESTO_ATTENUATO}; font-size: 12px;")
            testi.addWidget(seconda_riga)

        layout.addLayout(testi, stretch=1)

        if evento["riferimento"]:
            azione = QLabel("Apri ›")
            azione.setStyleSheet(f"color: {TESTO_ATTENUATO}; font-size: 12px;")
            layout.addWidget(azione, alignment=Qt.AlignTop)

    def mousePressEvent(self, event):
        self.cliccata.emit()
        super().mousePressEvent(event)


class SchermataCalendarioOperativo(PaginaConSfondo):
    """Documentazione della versione portfolio."""

    def __init__(self, finestra_principale=None):
        super().__init__(PERCORSO_FOTO_SFONDO, opacita_velo=HOME_OPACITA_VELO)


        self._finestra_principale = finestra_principale
        self._eventi_del_giorno: list[dict] = []
        self.setObjectName("calendario_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_CALENDARIO)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        riga_titolo = QWidget()
        disposizione_titolo = QHBoxLayout(riga_titolo)
        disposizione_titolo.setContentsMargins(0, 0, 0, 0)
        disposizione_titolo.setSpacing(9)
        icona_titolo = QLabel()
        icona_titolo.setObjectName("icona_titolo_calendario")
        icona_titolo.setFixedSize(22, 22)
        icona_titolo.setPixmap(pixmap_simbolo(
            SIMBOLI_MODULI["Calendario Operativo"], 22, "#C0E3FF"
        ))
        disposizione_titolo.addWidget(icona_titolo, 0, Qt.AlignVCenter)
        self._titolo = QLabel("Calendario Operativo")
        self._titolo.setStyleSheet("font-size: 20px; font-weight: 600;")
        disposizione_titolo.addWidget(self._titolo, 0, Qt.AlignVCenter)
        disposizione_titolo.addStretch()
        layout.addWidget(riga_titolo)

        self._sottotitolo = QLabel()


        self._sottotitolo.setWordWrap(True)
        self._sottotitolo.setStyleSheet(f"color: {TESTO_ATTENUATO};")
        layout.addWidget(self._sottotitolo)

        self._pagine = QStackedWidget()
        self._pagine.setObjectName("pagine_calendario")
        self._pagine.addWidget(self._costruisci_pagina_calendario())
        self._pagine.addWidget(self._costruisci_pagina_giornata())
        layout.addWidget(self._pagine, stretch=1)

        self._mostra_pagina(PAGINA_CALENDARIO)
        self._aggiorna_tutto()


    def _costruisci_pagina_calendario(self) -> QWidget:
        pagina = QWidget()
        pagina.setObjectName("pagina_calendario")
        corpo = QHBoxLayout(pagina)
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(20)

        corpo.addWidget(self._crea_riquadro_calendario(), stretch=1)
        corpo.addWidget(self._crea_anteprima())
        return pagina

    def _crea_riquadro_calendario(self) -> QWidget:
        riquadro = QFrame()
        riquadro.setObjectName("pannello_home")

        layout = QVBoxLayout(riquadro)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(self._crea_barra_navigazione())

        self._calendario = _CalendarioSoloMeseCorrente()
        self._calendario.setObjectName("calendario_operativo")


        self._calendario.setNavigationBarVisible(False)
        self._calendario.setGridVisible(True)
        self._calendario.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self._calendario.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self._calendario.setSelectionMode(QCalendarWidget.SingleSelection)
        self._calendario.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._applica_tavolozza()
        self._uniforma_dimensioni_celle()
        self._calendario.selectionChanged.connect(self._al_cambio_giorno)
        self._calendario.currentPageChanged.connect(self._al_cambio_mese)


        self._calendario.activated.connect(lambda _: self.apri_giornata())
        layout.addWidget(self._calendario, stretch=1)

        return riquadro

    def _applica_tavolozza(self):
        """Documentazione della versione portfolio."""
        tavolozza = self._calendario.palette()
        tavolozza.setColor(QPalette.Base, QColor(SFONDO_CALENDARIO))
        tavolozza.setColor(QPalette.Window, QColor(SFONDO_CALENDARIO))
        tavolozza.setColor(QPalette.Text, QColor(TESTO_CALENDARIO))
        tavolozza.setColor(QPalette.WindowText, QColor(TESTO_CALENDARIO))
        tavolozza.setColor(QPalette.Highlight, QColor("#1F70CE"))
        tavolozza.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

        tavolozza.setColor(QPalette.Disabled, QPalette.Text,
                           QColor(TESTO_CALENDARIO_SPENTO))
        self._calendario.setPalette(tavolozza)

        intestazione = QTextCharFormat()
        intestazione.setForeground(QColor(INTESTAZIONE_CALENDARIO))
        intestazione.setBackground(QColor(SFONDO_CALENDARIO))
        for giorno in (Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday,
                       Qt.Friday, Qt.Saturday, Qt.Sunday):
            self._calendario.setWeekdayTextFormat(giorno, intestazione)

    def _uniforma_dimensioni_celle(self):
        """Documentazione della versione portfolio."""
        vista = self._calendario.findChild(QTableView)
        if vista is None:
            return

        vista.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        intestazione_verticale = vista.verticalHeader()
        intestazione_verticale.setSectionResizeMode(QHeaderView.Stretch)
        modello = vista.model()
        if modello is not None and modello.rowCount() > 0:
            intestazione_verticale.setSectionResizeMode(0, QHeaderView.Fixed)
            intestazione_verticale.resizeSection(0, ALTEZZA_RIGA_NOMI_GIORNI)

    def _crea_barra_navigazione(self) -> QWidget:
        barra = QWidget()
        barra.setObjectName("barra_calendario")
        riga = QHBoxLayout(barra)
        riga.setContentsMargins(0, 0, 0, 0)
        riga.setSpacing(10)

        self._etichetta_mese = QLabel()
        self._etichetta_mese.setObjectName("mese_calendario")


        self._etichetta_mese.setWordWrap(True)
        riga.addWidget(self._etichetta_mese)
        riga.addStretch()


        self._pulsante_oggi = QPushButton("Oggi")
        self._pulsante_oggi.setObjectName("oggi_calendario")
        self._pulsante_oggi.setCursor(Qt.PointingHandCursor)
        self._pulsante_oggi.clicked.connect(self.vai_a_oggi)
        riga.addWidget(self._pulsante_oggi)

        self._mese_precedente = QPushButton("‹")
        self._mese_precedente.setObjectName("freccia_calendario")
        self._mese_precedente.setCursor(Qt.PointingHandCursor)
        self._mese_precedente.setToolTip("Mese precedente")
        self._mese_precedente.clicked.connect(self.mese_precedente)
        riga.addWidget(self._mese_precedente)

        self._mese_successivo = QPushButton("›")
        self._mese_successivo.setObjectName("freccia_calendario")
        self._mese_successivo.setCursor(Qt.PointingHandCursor)
        self._mese_successivo.setToolTip("Mese successivo")
        self._mese_successivo.clicked.connect(self.mese_successivo)
        riga.addWidget(self._mese_successivo)

        return barra

    def _crea_anteprima(self) -> QWidget:
        riquadro = QFrame()
        riquadro.setObjectName("pannello_home")


        riquadro.setMaximumWidth(LARGHEZZA_MASSIMA_ANTEPRIMA)
        riquadro.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        layout = QVBoxLayout(riquadro)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        riga_data = QWidget()
        riga_data.setObjectName("riga_data_anteprima")
        disposizione_data = QHBoxLayout(riga_data)
        disposizione_data.setContentsMargins(0, 0, 0, 0)
        disposizione_data.setSpacing(8)
        icona_data = QLabel()
        icona_data.setObjectName("icona_data_anteprima")
        icona_data.setFixedSize(20, 20)
        icona_data.setPixmap(pixmap_simbolo(
            SIMBOLI_MODULI["Calendario Operativo"], 20, "#C0E3FF"
        ))
        disposizione_data.addWidget(icona_data, 0, Qt.AlignTop)
        self._anteprima_data = QLabel()
        self._anteprima_data.setObjectName("anteprima_data")
        self._anteprima_data.setWordWrap(True)
        disposizione_data.addWidget(self._anteprima_data, stretch=1)
        layout.addWidget(riga_data)

        self._anteprima_conteggio = QLabel()
        self._anteprima_conteggio.setObjectName("anteprima_conteggio")
        self._anteprima_conteggio.setWordWrap(True)
        layout.addWidget(self._anteprima_conteggio)

        contenitore_righe = QWidget()
        contenitore_righe.setObjectName("contenitore_anteprima_calendario")
        self._layout_anteprima = QVBoxLayout(contenitore_righe)
        self._layout_anteprima.setContentsMargins(0, 4, 0, 0)
        self._layout_anteprima.setSpacing(6)
        layout.addWidget(contenitore_righe)

        layout.addStretch()

        self._pulsante_apri = QPushButton("Apri giornata →")
        self._pulsante_apri.setObjectName("apri_giornata")
        self._pulsante_apri.setCursor(Qt.PointingHandCursor)
        self._pulsante_apri.clicked.connect(self.apri_giornata)
        layout.addWidget(self._pulsante_apri)

        scorciatoia = QLabel("oppure doppio clic sulla data")
        scorciatoia.setObjectName("nota_anteprima")
        scorciatoia.setAlignment(Qt.AlignCenter)
        scorciatoia.setWordWrap(True)
        layout.addWidget(scorciatoia)

        return riquadro


    def _costruisci_pagina_giornata(self) -> QWidget:
        pagina = QWidget()
        pagina.setObjectName("pagina_giornata")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)


        self._pulsante_torna = QPushButton("← Calendario")
        self._pulsante_torna.setObjectName("torna_al_calendario")
        self._pulsante_torna.setCursor(Qt.PointingHandCursor)
        self._pulsante_torna.clicked.connect(self.torna_al_calendario)
        layout.addWidget(self._pulsante_torna, alignment=Qt.AlignLeft)

        riquadro = QFrame()
        riquadro.setObjectName("pannello_home")
        interno = QVBoxLayout(riquadro)
        interno.setContentsMargins(18, 16, 18, 18)
        interno.setSpacing(12)

        riga_intestazione = QWidget()
        riga_intestazione.setObjectName("intestazione_giornata_calendario")
        intestazione = QHBoxLayout(riga_intestazione)
        intestazione.setContentsMargins(0, 0, 0, 0)

        self._etichetta_giorno = QLabel()
        self._etichetta_giorno.setObjectName("titolo_giornata")
        intestazione.addWidget(self._etichetta_giorno)

        self._etichetta_conteggio = QLabel()
        self._etichetta_conteggio.setStyleSheet(f"color: {TESTO_ATTENUATO};")
        intestazione.addWidget(self._etichetta_conteggio)
        intestazione.addStretch()

        intestazione.addWidget(QLabel("Modulo:"))
        self._filtro = QComboBox()


        self._filtro.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self._filtro.setMinimumContentsLength(14)
        self._filtro.addItem(TUTTI_I_MODULI)
        for nome in moduli_disponibili():
            self._filtro.addItem(_icona_modulo(nome, 17), nome, userData=nome)
        self._filtro.setIconSize(QSize(17, 17))
        self._filtro.currentIndexChanged.connect(self._ridisegna_eventi)
        intestazione.addWidget(self._filtro)

        interno.addWidget(riga_scorrevole(riga_intestazione))

        area = QScrollArea()
        area.setObjectName("elenco_eventi_calendario")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        self._contenuto = QWidget()
        self._contenuto.setObjectName("contenuto_eventi_calendario")
        self._layout_eventi = QVBoxLayout(self._contenuto)
        self._layout_eventi.setContentsMargins(0, 0, 0, 0)
        self._layout_eventi.setSpacing(8)
        area.setWidget(self._contenuto)
        interno.addWidget(area, stretch=1)

        layout.addWidget(riquadro, stretch=1)
        return pagina


    def _mostra_pagina(self, indice: int):
        self._pagine.setCurrentIndex(indice)
        self._sottotitolo.setText(
            "Scegli un giorno per vedere cosa e' stato registrato in quella giornata."
            if indice == PAGINA_CALENDARIO
            else "Tutto cio' che e' stato registrato nella giornata selezionata."
        )

    def apri_giornata(self):
        """Documentazione della versione portfolio."""
        self._ridisegna_eventi()
        self._mostra_pagina(PAGINA_GIORNATA)

    def torna_al_calendario(self):
        """Documentazione della versione portfolio."""
        self._mostra_pagina(PAGINA_CALENDARIO)

    def torna_dalla_consultazione(self):
        """Documentazione della versione portfolio."""
        if self._finestra_principale is not None:
            self._finestra_principale.mostra_calendario_operativo()

    def mese_precedente(self):
        self._calendario.showPreviousMonth()

    def mese_successivo(self):
        self._calendario.showNextMonth()

    def vai_a_oggi(self):
        """Documentazione della versione portfolio."""
        self._calendario.setSelectedDate(QDate.currentDate())
        self._calendario.showToday()


    def showEvent(self, event):
        """Documentazione della versione portfolio."""
        super().showEvent(event)
        self._aggiorna_tutto()

    def _aggiorna_tutto(self):
        self._evidenzia_giorni_con_eventi()
        self._al_cambio_giorno()

    def _al_cambio_mese(self, anno: int, mese: int):
        self._evidenzia_giorni_con_eventi(anno, mese)
        self._etichetta_mese.setText(_mese_anno(QDate(anno, mese, 1)))

    def _evidenzia_giorni_con_eventi(self, anno: int | None = None, mese: int | None = None):
        anno = anno if anno is not None else self._calendario.yearShown()
        mese = mese if mese is not None else self._calendario.monthShown()
        self._etichetta_mese.setText(_mese_anno(QDate(anno, mese, 1)))


        self._calendario.setDateTextFormat(QDate(), QTextCharFormat())

        formato = QTextCharFormat()
        formato.setFontWeight(75)
        formato.setBackground(QColor(SFONDO_GIORNO_CON_EVENTI))
        formato.setForeground(QColor(ACCENTO_CALENDARIO))
        for data in giorni_con_eventi(anno, mese):
            qdate = qdate_da_data(data)
            if qdate.isValid():
                self._calendario.setDateTextFormat(qdate, formato)

    def _al_cambio_giorno(self):
        data = data_da_qdate(self._calendario.selectedDate())
        self._etichetta_giorno.setText(_titolo_giornata(data))
        self._eventi_del_giorno = eventi_del_giorno(data)
        self._aggiorna_anteprima(data)
        self._ridisegna_eventi()


    def _aggiorna_anteprima(self, data: str):
        """Documentazione della versione portfolio."""
        while self._layout_anteprima.count():
            elemento = self._layout_anteprima.takeAt(0)
            widget = elemento.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self._anteprima_data.setText(_titolo_giornata(data))

        gruppi = eventi_per_modulo(self._eventi_del_giorno)
        totale = len(self._eventi_del_giorno)
        if totale == 0:
            self._anteprima_conteggio.setText("Nessuna attivita' registrata")
            return

        attivita = "1 attivita'" if totale == 1 else f"{totale} attivita'"
        moduli = "1 modulo" if len(gruppi) == 1 else f"{len(gruppi)} moduli"
        self._anteprima_conteggio.setText(f"{attivita} · {moduli}")

        for nome, del_modulo in gruppi:
            self._layout_anteprima.addWidget(self._crea_riga_anteprima(nome, len(del_modulo)))

    def _crea_riga_anteprima(self, nome: str, quanti: int) -> QWidget:
        riga = QWidget()
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        icona = QLabel()
        icona.setObjectName("icona_modulo_anteprima")
        icona.setFixedSize(18, 18)
        icona.setPixmap(_pixmap_modulo(nome, 18))
        layout.addWidget(icona, 0, Qt.AlignTop)

        etichetta = QLabel(nome)
        etichetta.setObjectName("riga_anteprima")
        etichetta.setWordWrap(True)
        layout.addWidget(etichetta, stretch=1)

        numero = QLabel(str(quanti))
        numero.setObjectName("numero_anteprima")
        numero.setAlignment(Qt.AlignCenter)


        larghezza_testo = numero.fontMetrics().horizontalAdvance(numero.text())
        numero.setMinimumSize(max(36, larghezza_testo + 20), 26)
        numero.setMaximumHeight(26)
        layout.addWidget(numero)
        return riga


    def _modulo_selezionato(self) -> str | None:
        return self._filtro.currentData()

    def _ridisegna_eventi(self):
        while self._layout_eventi.count():
            elemento = self._layout_eventi.takeAt(0)
            widget = elemento.widget()
            if widget is not None:


                widget.setParent(None)
                widget.deleteLater()

        modulo = self._modulo_selezionato()


        eventi = [e for e in self._eventi_del_giorno if not modulo or e["modulo"] == modulo]

        totale = len(self._eventi_del_giorno)
        self._etichetta_conteggio.setText(
            "" if totale == 0 else (f"{totale} eventi" if totale > 1 else "1 evento")
        )

        if not eventi:
            self._layout_eventi.addWidget(self._crea_stato_vuoto(modulo, totale))
            self._layout_eventi.addStretch()
            return

        for nome_modulo, del_modulo in eventi_per_modulo(eventi):
            self._layout_eventi.addWidget(self._crea_titolo_modulo(nome_modulo))
            for evento in del_modulo:
                riga = _RigaEvento(evento)
                riga.cliccata.connect(lambda e=evento: self._al_click_evento(e))
                self._layout_eventi.addWidget(riga)

        self._layout_eventi.addStretch()

    def _crea_titolo_modulo(self, nome: str) -> QWidget:
        riga = QWidget()
        riga.setObjectName("intestazione_modulo_giornata")
        disposizione = QHBoxLayout(riga)
        disposizione.setContentsMargins(0, 0, 0, 0)
        disposizione.setSpacing(7)
        icona = QLabel()
        icona.setObjectName("icona_modulo_giornata")
        icona.setFixedSize(17, 17)
        icona.setPixmap(_pixmap_modulo(nome, 17))
        disposizione.addWidget(icona, 0, Qt.AlignVCenter)
        etichetta = QLabel(nome.upper())
        etichetta.setObjectName("titolo_modulo_giornata")
        disposizione.addWidget(etichetta, 0, Qt.AlignVCenter)
        disposizione.addStretch()
        return riga

    def _crea_stato_vuoto(self, modulo: str | None, totale_giornata: int) -> QLabel:
        if modulo and totale_giornata:
            testo = f"Nessun evento di «{modulo}» in questa giornata."
        else:
            testo = "Nessun evento registrato in questa giornata."
        etichetta = QLabel(testo)
        etichetta.setAlignment(Qt.AlignCenter)
        etichetta.setStyleSheet(f"color: {TESTO_ATTENUATO}; padding: 24px;")
        return etichetta


    def _al_click_evento(self, evento: dict):
        """Documentazione della versione portfolio."""
        riferimento = evento.get("riferimento") or {}

        if riferimento.get("tipo") == "rapporto" and self._finestra_principale is not None:
            self._finestra_principale.consulta_rapporto_giornaliero(
                riferimento["rapporto"], al_ritorno=self.torna_dalla_consultazione
            )
            return

        voci = [("Data", evento["data"]), ("Ora", evento["ora"] or ORA_NON_REGISTRATA)]
        voci += [(etichetta, valore) for etichetta, valore in evento["dettaglio"]]
        DialogoDettaglioEvento(
            self, f"{evento['tipo_evento']} — {evento['titolo']}", voci
        ).exec()
