"""Documentazione della versione portfolio."""
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.registro import logger
from data.backup import stato_ultimo_backup
from data.chiavi import conta_chiavi_fuori
from data.consegne_radio import conta_radio_fuori
from data.rapporti_giornalieri import conta_rapporti_aperti
from documents.word.rapporto_giornaliero import ErroreSalvataggioRapporto
from ui.anagrafica_operatori.schermata import SchermataAnagraficaOperatori
from ui.bacheca_chiavi.schermata import SchermataBachecaChiavi
from ui.calendario_operativo.schermata import SchermataCalendarioOperativo
from ui.cassaforte.schermata import SchermataCassaforte
from ui.comune.icone import SIMBOLI_MODULI, pixmap_simbolo
from ui.comune.sidebar_moduli import MOTIVO_EDITOR, SidebarModuli
from ui.consegna_radio.schermata import SchermataConsegnaRadio
from ui.gestione_radio.schermata import SchermataGestioneRadio
from ui.impostazioni.schermata import SchermataImpostazioni
from ui.logo import crea_etichetta_logo
from ui.oggetti_smarriti.schermata import SchermataOggettiSmarriti
from ui.passaggio_consegne.panel import PannelloPassaggioConsegne
from ui.rapporto_giornaliero.editor_rapporto import EditorRapporto
from ui.rapporto_giornaliero.schermata import SchermataRapportoGiornaliero
from ui.sfondo import PaginaConSfondo
from ui.tema import FOGLIO_DI_STILE_HOME, HOME_OPACITA_VELO, TESTO_ATTENUATO, TESTO_CHIARO

_registro = logger(__name__)

NOME_CONSEGNA_RADIO = "Consegna Radio"
NOME_RAPPORTO_GIORNALIERO = "Rapporto Giornaliero"


NOME_DOCUMENTO_WORD = "Documento Rapporto Giornaliero"


NOME_CONSULTAZIONE_RAPPORTO = "Consultazione Rapporto Giornaliero"
SEZIONI_IN_COSTRUZIONE = []
NOME_GESTIONE_RADIO = "Gestione Radio"
NOME_ANAGRAFICA_OPERATORI = "Anagrafica Operatori"
NOME_BACHECA_CHIAVI = "Bacheca Chiavi"
NOME_OGGETTI_SMARRITI = "Oggetti Smarriti"
NOME_CASSAFORTE = "Cassaforte"
NOME_CALENDARIO_OPERATIVO = "Calendario Operativo"
TUTTE_LE_SEZIONI = [
    NOME_RAPPORTO_GIORNALIERO, NOME_BACHECA_CHIAVI, NOME_CONSEGNA_RADIO, NOME_GESTIONE_RADIO,
    NOME_ANAGRAFICA_OPERATORI, NOME_OGGETTI_SMARRITI, NOME_CASSAFORTE,
    NOME_CALENDARIO_OPERATIVO, "Impostazioni",
]

NOME_HOME = "Home"


_BADGE_OPERATIVI = (
    (NOME_BACHECA_CHIAVI, conta_chiavi_fuori, "fuori", "fuori"),
    (NOME_CONSEGNA_RADIO, conta_radio_fuori, "fuori", "fuori"),
    (NOME_RAPPORTO_GIORNALIERO, conta_rapporti_aperti, "aperto", "aperti"),
)


def stati_operativi() -> dict[str, tuple[int, str]]:
    """Documentazione della versione portfolio."""
    stati = {}
    for nome, conta, singolare, plurale in _BADGE_OPERATIVI:
        numero = conta()
        stati[nome] = (numero, singolare if numero == 1 else plurale)
    return stati


VOCI_TRASVERSALI = (NOME_CALENDARIO_OPERATIVO,)
VOCI_IN_FONDO = ("Impostazioni",)

PERCORSO_FOTO_SFONDO_HOME = Path(__file__).parent / "assets" / "images" / "demo_sala_fucine.jpg"


def _crea_intestazione(barra_rapporti_aperti: QWidget) -> QWidget:
    intestazione = QFrame()
    intestazione.setObjectName("intestazione")
    intestazione.setFixedHeight(72)

    layout = QHBoxLayout(intestazione)
    layout.setContentsMargins(24, 0, 24, 0)
    layout.setSpacing(10)

    layout.addWidget(crea_etichetta_logo(44, TESTO_CHIARO))

    testo_security = QLabel("Manager Demo")
    testo_security.setStyleSheet(f"font-size:20px; font-weight:400; color:{TESTO_ATTENUATO};")
    layout.addWidget(testo_security)

    layout.addStretch()


    layout.addWidget(barra_rapporti_aperti)
    return intestazione


def _crea_pagina_modulo(contenuto: QWidget) -> QWidget:
    """Documentazione della versione portfolio."""
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    layout.addWidget(contenuto, stretch=1)
    return pagina


def _crea_sezione_in_costruzione(nome: str) -> QWidget:
    pagina = QWidget()
    layout = QVBoxLayout(pagina)
    etichetta = QLabel(f"{nome}\n\n(sezione non ancora implementata)")
    etichetta.setAlignment(Qt.AlignCenter)
    etichetta.setStyleSheet(f"font-size: 16px; color: {TESTO_ATTENUATO};")
    layout.addWidget(etichetta)
    return pagina


class _FasciaInferiore(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, pannello_consegne: QWidget):
        super().__init__()
        self.setObjectName("fascia_inferiore")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 14, 0)
        layout.setSpacing(12)

        self._alloggio = QWidget()
        self._alloggio.setObjectName("alloggio_passaggio_inferiore")
        self._layout_alloggio = QHBoxLayout(self._alloggio)
        self._layout_alloggio.setContentsMargins(0, 0, 0, 0)
        self._layout_alloggio.setSpacing(0)
        layout.addWidget(self._alloggio, stretch=1)

        self._credito = QLabel("Desktop demo")
        self._credito.setObjectName("credito_powered_by_tony")
        self._credito.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self._credito)

        self.aggancia_passaggio(pannello_consegne)

    def aggancia_passaggio(self, pannello: QWidget):
        if not self._alloggio.isAncestorOf(pannello):
            self._layout_alloggio.addWidget(pannello)

    def sgancia_passaggio(self, pannello: QWidget):
        self._layout_alloggio.removeWidget(pannello)


class _BarraDocumentoWord(QWidget):
    """Documentazione della versione portfolio."""

    def __init__(self, al_click_chip):
        super().__init__()
        self.setFixedHeight(44)
        self.setMaximumWidth(520)
        self.hide()
        self._al_click_chip = al_click_chip
        self._chip_per_id: dict[int, QPushButton] = {}

        layout_esterno = QHBoxLayout(self)
        layout_esterno.setContentsMargins(0, 0, 0, 0)

        area_scorrimento = QScrollArea()
        area_scorrimento.setWidgetResizable(True)
        area_scorrimento.setFrameShape(QFrame.NoFrame)
        area_scorrimento.setStyleSheet("background: transparent;")
        area_scorrimento.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        area_scorrimento.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._contenitore_chip = QWidget()
        self._contenitore_chip.setStyleSheet("background: transparent;")
        self._layout_chip = QHBoxLayout(self._contenitore_chip)
        self._layout_chip.setContentsMargins(0, 0, 0, 0)
        self._layout_chip.setSpacing(8)
        self._layout_chip.addStretch()
        area_scorrimento.setWidget(self._contenitore_chip)

        layout_esterno.addWidget(area_scorrimento)

    def aggiungi_o_aggiorna_chip(self, id_rapporto: int, etichetta: str):
        chip = self._chip_per_id.get(id_rapporto)
        if chip is None:
            chip = QPushButton(etichetta)
            chip.setCheckable(True)
            chip.clicked.connect(lambda: self._al_click_chip(id_rapporto))
            self._layout_chip.insertWidget(self._layout_chip.count() - 1, chip)
            self._chip_per_id[id_rapporto] = chip
        else:
            chip.setText(etichetta)
        self._mostra_se_necessario()

    def imposta_attivo(self, id_rapporto: int | None):
        for id_, chip in self._chip_per_id.items():
            chip.setChecked(id_ == id_rapporto)

    def ha_chip(self, id_rapporto: int) -> bool:
        return id_rapporto in self._chip_per_id

    def rimuovi_chip(self, id_rapporto: int):
        chip = self._chip_per_id.pop(id_rapporto, None)
        if chip is not None:
            chip.hide()
            chip.deleteLater()
        self._mostra_se_necessario()

    def _mostra_se_necessario(self):
        if not self._chip_per_id:
            self.hide()
            return


        self.setVisible(True)
        self._forza_relayout()
        QTimer.singleShot(0, self._forza_relayout)

    def _forza_relayout(self):
        self.updateGeometry()
        genitore = self.parentWidget()
        if genitore is not None and genitore.layout() is not None:
            genitore.layout().invalidate()
            genitore.layout().activate()
        self.update()


_DESCRIZIONI_HOME = {
    NOME_RAPPORTO_GIORNALIERO: "Compila e consulta il rapporto\ndi servizio giornaliero.",
    NOME_BACHECA_CHIAVI: "Gestisci la bacheca delle chiavi\ne le movimentazioni.",
    NOME_CONSEGNA_RADIO: "Registra la consegna\ne la riconsegna delle radio.",
    NOME_GESTIONE_RADIO: "Amministra il parco radio\ne le relative assegnazioni.",
    NOME_ANAGRAFICA_OPERATORI: "Gestione e consultazione\ndegli operatori.",
    NOME_OGGETTI_SMARRITI: "Registra e gestisci gli oggetti\nsmarriti e ritrovati.",
    NOME_CASSAFORTE: "Gestisci gli elementi in cassaforte\ne le relative movimentazioni.",
    NOME_CALENDARIO_OPERATIVO: "Consulta gli eventi operativi registrati, giorno per giorno.",
    "Impostazioni": "Configura le cartelle dei documenti e del backup.",
}


_SIMBOLI_HOME = SIMBOLI_MODULI


def _crea_icona_home(nome: str) -> QLabel:
    simbolo = _SIMBOLI_HOME.get(nome, _SIMBOLI_HOME[NOME_RAPPORTO_GIORNALIERO])
    pixmap = pixmap_simbolo(simbolo, 40, "#C9DFFF")

    icona = QLabel()
    icona.setObjectName("icona_modulo_home")
    icona.setPixmap(pixmap)
    icona.setAlignment(Qt.AlignCenter)
    icona.setFixedSize(56, 56)
    return icona


class _CardModuloHome(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, nome: str, al_click_sezione):
        super().__init__()
        self.setObjectName("card_modulo_home")
        self.setMinimumHeight(112)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(16)
        layout.addWidget(_crea_icona_home(nome))

        testo = QWidget()
        testo.setObjectName("testo_card_home")
        righe = QVBoxLayout(testo)
        righe.setContentsMargins(0, 0, 0, 0)
        righe.setSpacing(6)
        titolo = QLabel(nome)
        titolo.setObjectName("nome_modulo_home")
        titolo.setWordWrap(True)
        titolo.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        righe.addWidget(titolo)
        descrizione = QLabel(_DESCRIZIONI_HOME.get(nome, "Apri la sezione."))
        descrizione.setObjectName("descrizione_modulo_home")
        descrizione.setWordWrap(True)
        descrizione.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        righe.addWidget(descrizione)
        layout.addWidget(testo, stretch=1)

        azioni = QWidget()
        azioni.setObjectName("azioni_card_home")
        colonna = QVBoxLayout(azioni)
        colonna.setContentsMargins(0, 0, 0, 0)
        colonna.setSpacing(10)
        colonna.addStretch()
        self.badge = QLabel()
        self.badge.setObjectName("badge_modulo_home")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setMinimumHeight(28)
        self.badge.setMaximumHeight(28)
        self.badge.hide()
        colonna.addWidget(self.badge, alignment=Qt.AlignRight)

        self.pulsante = QPushButton("Apri")
        self.pulsante.setObjectName("apri_modulo_home")
        self.pulsante.setMinimumWidth(78)
        self.pulsante.setAccessibleName(f"Apri {nome}")
        self.pulsante.setToolTip(f"Apri {nome}")
        self.pulsante.setCursor(Qt.PointingHandCursor)
        self.pulsante.clicked.connect(lambda _=False: al_click_sezione(nome))
        colonna.addWidget(self.pulsante, alignment=Qt.AlignRight)
        colonna.addStretch()
        layout.addWidget(azioni)

    def aggiorna_badge(self, numero: int, termine: str):
        """Documentazione della versione portfolio."""
        self.badge.setText(f"{numero} {termine}" if numero else "")
        self.badge.setVisible(numero > 0)


class _PaginaHome(PaginaConSfondo):
    """Documentazione della versione portfolio."""

    def __init__(self, sezioni: list, al_click_sezione):
        super().__init__(PERCORSO_FOTO_SFONDO_HOME, opacita_velo=HOME_OPACITA_VELO)
        self.setObjectName("home_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_HOME)
        self._colonne = 0
        self._sezioni = list(sezioni)

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(0, 0, 0, 0)

        self._area = QScrollArea()
        self._area.setObjectName("area_home")
        self._area.setWidgetResizable(True)
        self._area.setFrameShape(QFrame.NoFrame)
        self._area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._area.viewport().setObjectName("viewport_home")
        self._area.viewport().setAutoFillBackground(False)

        contenuto = QWidget()
        contenuto.setObjectName("contenuto_home")
        contenuto.setAutoFillBackground(False)
        layout_contenuto = QVBoxLayout(contenuto)
        layout_contenuto.setContentsMargins(24, 16, 24, 16)
        layout_contenuto.setSpacing(0)

        pannello = QFrame()
        pannello.setObjectName("pannello_home")
        pannello.setMaximumWidth(1360)
        pannello.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(0, 0, 0, 0)
        layout_pannello.setSpacing(8)

        titolo = QLabel("CONTROL ROOM")
        titolo.setObjectName("titolo_control_room")
        layout_pannello.addWidget(titolo)
        sottotitolo = QLabel("Accesso rapido ai moduli operativi")
        sottotitolo.setObjectName("sottotitolo_control_room")
        sottotitolo.setWordWrap(True)
        layout_pannello.addWidget(sottotitolo)
        layout_pannello.addSpacing(10)

        self._griglia = QGridLayout()
        self._griglia.setContentsMargins(0, 0, 0, 0)
        self._griglia.setSpacing(12)
        layout_pannello.addLayout(self._griglia)
        self._card_sezione = {}
        self._pulsanti_sezione = {}
        for nome in sezioni:
            card = _CardModuloHome(nome, al_click_sezione)
            self._card_sezione[nome] = card
            self._pulsanti_sezione[nome] = card.pulsante


        centro = QHBoxLayout()
        centro.setContentsMargins(0, 0, 0, 0)
        centro.addStretch()
        centro.addWidget(pannello, stretch=1)
        centro.addStretch()
        layout_contenuto.addLayout(centro)
        layout_contenuto.addStretch()

        self._area.setWidget(contenuto)
        layout_esterno.addWidget(self._area)
        self._area.viewport().installEventFilter(self)
        self._disponi_card()
        self.aggiorna_badge_operativi(stati_operativi())

    def eventFilter(self, oggetto, evento):
        if oggetto is self._area.viewport() and evento.type() == QEvent.Resize:
            self._disponi_card()
        return super().eventFilter(oggetto, evento)

    def _disponi_card(self):

        larghezza = self._area.viewport().width()
        colonne = 3 if larghezza >= 1180 else (2 if larghezza >= 1100 else 1)
        if colonne == self._colonne:
            return
        self._colonne = colonne
        while self._griglia.count():
            self._griglia.takeAt(0)
        self._griglia.setColumnStretch(0, 1)
        self._griglia.setColumnStretch(1, 1 if colonne == 2 else 0)
        self._griglia.setColumnStretch(2, 1 if colonne == 3 else 0)
        if colonne == 3:
            self._griglia.setColumnStretch(1, 1)
        riga = colonna = 0
        for nome in self._sezioni:
            self._griglia.addWidget(self._card_sezione[nome], riga, colonna)
            colonna += 1
            if colonna == colonne:
                riga += 1
                colonna = 0

    def aggiorna_badge_operativi(self, stati: dict[str, tuple[int, str]]):
        """Documentazione della versione portfolio."""
        for nome, card in self._card_sezione.items():
            numero, termine = stati.get(nome, (0, ""))
            card.aggiorna_badge(numero, termine)

class FinestraPrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Room Manager Demo")
        self.resize(1300, 900)


        self._editor_per_rapporto: dict[int, EditorRapporto] = {}
        self._id_rapporto_espanso: int | None = None

        contenitore = QWidget()
        self.setCentralWidget(contenitore)
        layout_principale = QVBoxLayout(contenitore)
        layout_principale.setContentsMargins(0, 0, 0, 0)
        layout_principale.setSpacing(0)

        self._barra_documento_word = _BarraDocumentoWord(self._al_click_chip)
        layout_principale.addWidget(_crea_intestazione(self._barra_documento_word))


        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)

        self._sidebar = SidebarModuli(
            voci=[n for n in TUTTE_LE_SEZIONI if n not in VOCI_TRASVERSALI + VOCI_IN_FONDO],
            simboli=_SIMBOLI_HOME,
            al_click_voce=self._mostra_pagina,
            nome_home=NOME_HOME,
            voci_trasversali=VOCI_TRASVERSALI,
            voci_in_fondo=VOCI_IN_FONDO,
        )
        corpo.addWidget(self._sidebar)

        self._pagine = QStackedWidget()
        corpo.addWidget(self._pagine, stretch=1)
        layout_principale.addLayout(corpo, stretch=1)


        self._pannello_consegne = PannelloPassaggioConsegne(contenitore)
        self._pannello_consegne_in_sidebar = False
        self._sidebar_attiva = False


        self._avviso_backup_mostrato = False
        self._fascia_inferiore = _FasciaInferiore(self._pannello_consegne)
        layout_principale.addWidget(self._fascia_inferiore)

        self._sidebar.imposta_osservatore_stato(self._aggiorna_aggancio_passaggio_consegne)

        self._indici_pagine = {}
        self._pagina_home = _PaginaHome(TUTTE_LE_SEZIONI, self._mostra_pagina)
        self._aggiungi_pagina(NOME_HOME, self._pagina_home)

        for nome in SEZIONI_IN_COSTRUZIONE:
            contenuto = _crea_sezione_in_costruzione(nome)
            self._aggiungi_pagina(nome, _crea_pagina_modulo(contenuto))

        self._schermata_rapporto_giornaliero = SchermataRapportoGiornaliero(self)
        self._aggiungi_pagina(
            NOME_RAPPORTO_GIORNALIERO,
            _crea_pagina_modulo(self._schermata_rapporto_giornaliero),
        )


        self._pagine_editor = QStackedWidget()
        self._aggiungi_pagina(NOME_DOCUMENTO_WORD, self._pagine_editor)


        self._editor_consultazione = EditorRapporto()
        self._editor_consultazione.imposta_sola_lettura(True)
        self._aggiungi_pagina(NOME_CONSULTAZIONE_RAPPORTO, self._editor_consultazione)

        self._aggiungi_pagina(
            NOME_BACHECA_CHIAVI,
            _crea_pagina_modulo(SchermataBachecaChiavi()),
        )
        self._aggiungi_pagina(
            NOME_CONSEGNA_RADIO,
            _crea_pagina_modulo(SchermataConsegnaRadio()),
        )
        self._aggiungi_pagina(
            NOME_GESTIONE_RADIO,
            _crea_pagina_modulo(SchermataGestioneRadio()),
        )

        self._schermata_anagrafica_operatori = SchermataAnagraficaOperatori()
        self._aggiungi_pagina(
            NOME_ANAGRAFICA_OPERATORI,
            _crea_pagina_modulo(self._schermata_anagrafica_operatori),
        )

        self._aggiungi_pagina(
            NOME_OGGETTI_SMARRITI,
            _crea_pagina_modulo(SchermataOggettiSmarriti()),
        )

        self._aggiungi_pagina(
            NOME_CASSAFORTE,
            _crea_pagina_modulo(SchermataCassaforte()),
        )

        self._aggiungi_pagina(
            NOME_CALENDARIO_OPERATIVO,
            _crea_pagina_modulo(SchermataCalendarioOperativo(self)),
        )

        contenuto_impostazioni = SchermataImpostazioni()
        self._aggiungi_pagina(
            "Impostazioni", _crea_pagina_modulo(contenuto_impostazioni)
        )

        self._torna_alla_home()

    def _aggiungi_pagina(self, nome: str, pagina: QWidget):
        indice = self._pagine.addWidget(pagina)
        self._indici_pagine[nome] = indice

    def _mostra_pagina(self, nome: str):
        self._pagine.setCurrentIndex(self._indici_pagine[nome])
        self._aggiorna_sidebar(nome)


        self.aggiorna_badge_operativi()

    def _aggiorna_sidebar(self, nome_pagina: str):
        """Documentazione della versione portfolio."""
        e_home = nome_pagina == NOME_HOME


        self._sidebar_attiva = not e_home
        self._sidebar.setVisible(self._sidebar_attiva)
        a_tutto_schermo = nome_pagina in (NOME_DOCUMENTO_WORD, NOME_CONSULTAZIONE_RAPPORTO)
        self._sidebar.forza_compatta(MOTIVO_EDITOR, a_tutto_schermo)


        if nome_pagina == NOME_DOCUMENTO_WORD:
            self._sidebar.imposta_attivo(NOME_RAPPORTO_GIORNALIERO)
        elif nome_pagina == NOME_CONSULTAZIONE_RAPPORTO:
            self._sidebar.imposta_attivo(NOME_CALENDARIO_OPERATIVO)
        else:
            self._sidebar.imposta_attivo(nome_pagina)
        self._aggiorna_aggancio_passaggio_consegne()

    def _aggiorna_aggancio_passaggio_consegne(self):
        """Documentazione della versione portfolio."""
        in_sidebar = self._sidebar_attiva and not self._sidebar.e_compatta()
        if in_sidebar == self._pannello_consegne_in_sidebar:
            return


        self._pannello_consegne.chiudi_blocco_note()

        if in_sidebar:
            self._fascia_inferiore.sgancia_passaggio(self._pannello_consegne)
            self._sidebar.aggancia_in_fondo(self._pannello_consegne)
        else:
            self._sidebar.sgancia(self._pannello_consegne)
            self._fascia_inferiore.aggancia_passaggio(self._pannello_consegne)

        self._pannello_consegne.imposta_variante_sidebar(in_sidebar)
        self._pannello_consegne_in_sidebar = in_sidebar

    def aggiorna_badge_operativi(self):
        """Documentazione della versione portfolio."""
        stati = stati_operativi()
        self._pagina_home.aggiorna_badge_operativi(stati)
        for nome, (numero, termine) in stati.items():
            self._sidebar.aggiorna_badge(nome, numero, termine)
        self._avvisa_se_il_backup_non_funziona()

    def _avvisa_se_il_backup_non_funziona(self):
        """Documentazione della versione portfolio."""
        if self._avviso_backup_mostrato:
            return
        stato = stato_ultimo_backup()
        if stato is None or stato["riuscito"]:
            return
        if not stato["configurato"]:


            return

        self._avviso_backup_mostrato = True
        QMessageBox.warning(
            self, "Copia di sicurezza non riuscita",
            f"{stato['motivo']}\n\n"
            "I dati che stai inserendo vengono salvati normalmente: è la copia "
            "esterna a non essere aggiornata. Controlla la cartella di backup "
            "nelle Impostazioni.",
        )


    def aggiorna_badge_chiavi(self):
        self.aggiorna_badge_operativi()

    def resizeEvent(self, evento):
        super().resizeEvent(evento)


        self._sidebar.adatta_alla_larghezza(self.width())

    def mostra_calendario_operativo(self):
        """Documentazione della versione portfolio."""
        self._mostra_pagina(NOME_CALENDARIO_OPERATIVO)

    def _torna_alla_home(self):
        self._mostra_pagina(NOME_HOME)

    def apri_rapporto_giornaliero(self, rapporto: dict):
        """Documentazione della versione portfolio."""
        self._schermata_rapporto_giornaliero.apri_rapporto(rapporto)

    def consulta_rapporto_giornaliero(self, rapporto: dict, al_ritorno):
        """Documentazione della versione portfolio."""
        self._schermata_rapporto_giornaliero.consulta_rapporto(rapporto, al_ritorno)

    def mostra_consultazione_rapporto(
        self, percorso_file, operatore: str, data_turno: str, orario: str, al_ritorno,
    ):
        """Documentazione della versione portfolio."""
        try:
            self._editor_consultazione.carica(percorso_file, operatore, data_turno, orario)
        except Exception as errore:
            QMessageBox.warning(
                self, "Rapporto non leggibile",
                "Non è stato possibile leggere il documento del rapporto:\n"
                f"{percorso_file}\n\n{errore}",
            )
            return
        self._editor_consultazione.imposta_sola_lettura(True, al_ritorno=al_ritorno)
        self._mostra_pagina(NOME_CONSULTAZIONE_RAPPORTO)


    def mostra_documento_word(
        self, id_rapporto: int, percorso_file, operatore: str, data_turno: str, orario: str, etichetta_bar: str,
    ):
        """Documentazione della versione portfolio."""
        editor = self._editor_per_rapporto.get(id_rapporto)
        if editor is None:
            nuovo_editor = EditorRapporto(al_salva_e_chiudi=lambda: self._salva_e_chiudi_da_editor(id_rapporto))
            try:
                nuovo_editor.carica(percorso_file, operatore, data_turno, orario)
            except Exception as errore:
                QMessageBox.warning(
                    self, "Rapporto non leggibile",
                    f"Non è stato possibile aprire questo rapporto:\n{percorso_file}\n\n"
                    "Il file potrebbe essere stato spostato, rinominato o danneggiato "
                    "da fuori il programma.\n\n"
                    f"Dettaglio: {errore}",
                )
                return
            editor = nuovo_editor
            self._editor_per_rapporto[id_rapporto] = editor
            self._pagine_editor.addWidget(editor)

        self._pagine_editor.setCurrentWidget(editor)
        self._id_rapporto_espanso = id_rapporto
        self._barra_documento_word.aggiungi_o_aggiorna_chip(id_rapporto, etichetta_bar)
        self._barra_documento_word.imposta_attivo(id_rapporto)
        self._mostra_pagina(NOME_DOCUMENTO_WORD)

    def riduci_documento_word(self):
        """Documentazione della versione portfolio."""
        if self._id_rapporto_espanso is None:
            return
        id_rapporto = self._id_rapporto_espanso
        editor = self._editor_per_rapporto.get(id_rapporto)
        if editor is not None:
            errore = self._salva_editor(id_rapporto, editor, "riduzione")
            if errore is not None:


                QMessageBox.warning(
                    self, "Rapporto non salvato",
                    f"{errore.messaggio_operatore}\n\n"
                    "Il rapporto resta aperto: quello che hai scritto non è perduto.",
                )
        self._id_rapporto_espanso = None
        self._barra_documento_word.imposta_attivo(None)
        self._mostra_pagina(NOME_RAPPORTO_GIORNALIERO)

    def espandi_documento_word(self, id_rapporto: int):
        """Documentazione della versione portfolio."""
        editor = self._editor_per_rapporto.get(id_rapporto)
        if editor is None:
            return
        self._pagine_editor.setCurrentWidget(editor)
        self._id_rapporto_espanso = id_rapporto
        self._barra_documento_word.imposta_attivo(id_rapporto)
        self._mostra_pagina(NOME_DOCUMENTO_WORD)

    def _al_click_chip(self, id_rapporto: int):
        """Documentazione della versione portfolio."""
        if self._id_rapporto_espanso == id_rapporto:
            self.riduci_documento_word()
        else:
            self.espandi_documento_word(id_rapporto)

    def _salva_e_chiudi_da_editor(self, id_rapporto: int):
        """Documentazione della versione portfolio."""
        self._schermata_rapporto_giornaliero.salva_e_chiudi_rapporto(id_rapporto)

    def chiudi_documento_word(self, id_rapporto: int) -> bool:
        """Documentazione della versione portfolio."""
        editor = self._editor_per_rapporto.get(id_rapporto)
        if editor is None:
            return True

        errore = self._salva_editor(id_rapporto, editor, "chiusura del rapporto")
        if errore is not None:
            QMessageBox.warning(
                self, "Rapporto non chiuso",
                f"{errore.messaggio_operatore}\n\n"
                "Il rapporto resta aperto e quello che hai scritto è ancora qui: "
                "risolvi il problema e riprova con \"Salva e chiudi\".",
            )
            return False

        del self._editor_per_rapporto[id_rapporto]
        self._pagine_editor.removeWidget(editor)
        editor.deleteLater()
        self._barra_documento_word.rimuovi_chip(id_rapporto)

        if self._id_rapporto_espanso == id_rapporto:
            self._id_rapporto_espanso = None
            self._mostra_pagina(NOME_RAPPORTO_GIORNALIERO)
        return True

    def aggiorna_metadati_documento_word(
        self, id_rapporto: int, percorso_file, operatore: str, orario: str, etichetta_bar: str,
    ):
        """Documentazione della versione portfolio."""
        editor = self._editor_per_rapporto.get(id_rapporto)
        if editor is not None:
            editor.aggiorna_intestazione(percorso_file, operatore, orario)
        if self._barra_documento_word.ha_chip(id_rapporto):
            self._barra_documento_word.aggiungi_o_aggiorna_chip(id_rapporto, etichetta_bar)


    def _salva_editor(self, id_rapporto: int, editor, operazione: str):
        """Documentazione della versione portfolio."""
        try:
            editor.salva_su_file()
            return None
        except ErroreSalvataggioRapporto as errore:
            _registro.error(
                "Salvataggio non riuscito durante %s — rapporto id=%s",
                operazione, id_rapporto, exc_info=errore.causa,
            )
            return errore
        except Exception as causa:
            _registro.error(
                "Guasto imprevisto salvando il rapporto id=%s durante %s",
                id_rapporto, operazione, exc_info=True,
            )
            return ErroreSalvataggioRapporto(getattr(editor, "_percorso_file", "?"), causa)

    def _descrizione_rapporto(self, id_rapporto: int) -> str:
        """Documentazione della versione portfolio."""
        chip = self._barra_documento_word._chip_per_id.get(id_rapporto)
        return chip.text() if chip is not None else f"rapporto {id_rapporto}"

    def closeEvent(self, evento):
        """Documentazione della versione portfolio."""
        falliti = []
        for id_rapporto, editor in list(self._editor_per_rapporto.items()):
            errore = self._salva_editor(id_rapporto, editor, "chiusura del programma")
            if errore is not None:
                falliti.append((id_rapporto, errore))

        if falliti:
            _registro.warning(
                "Chiusura annullata: %d rapporti non salvati (id: %s)",
                len(falliti), ", ".join(str(i) for i, _ in falliti),
            )
            elenco = "\n".join(
                f"    • {self._descrizione_rapporto(id_rapporto)}\n"
                f"        {errore.messaggio_operatore}"
                for id_rapporto, errore in falliti
            )
            QMessageBox.warning(
                self, "Rapporti non salvati",
                "Il programma non è stato chiuso: questi rapporti non è stato "
                f"possibile salvarli.\n\n{elenco}\n\n"
                "Quello che hai scritto è ancora aperto nel programma. "
                "Risolvi il problema indicato e chiudi di nuovo.",
            )
            evento.ignore()
            return

        _registro.info("Chiusura: %d rapporti salvati", len(self._editor_per_rapporto))
        super().closeEvent(evento)
