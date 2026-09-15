"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.operatori import (
    CATEGORIE_OPERATORE,
    ETICHETTE_CATEGORIE_OPERATORE,
    cerca_operatori,
    disattiva_operatore,
    modifica_categoria,
    modifica_nome_canonico,
    nome_completo,
    registra_operatore,
    riattiva_operatore,
    trova_operatore,
)

_INTESTAZIONI = ["Nome", "Cognome", "Categoria", "Stato", "Azioni"]


_ARIA_CELLA = 28
_SPAZIO_FRA_PULSANTI = 8


_LARGHEZZA_MINIMA_COLONNA = 96


_ALTEZZA_MINIMA_RIGA = 40


_MARGINE_VERTICALE_AZIONI = 4
_RUOLO_ID_OPERATORE = Qt.UserRole + 1
_TUTTE_LE_CATEGORIE = None

_ETICHETTE_FILTRO_STATO = [
    ("attivi", "Attivi"),
    ("disattivati", "Disattivati"),
    ("tutti", "Tutti"),
]


class _DialogoNuovoOperatoreManuale(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Nuovo operatore")
        self.setObjectName("dialogo_nuovo_operatore")
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        modulo = QFormLayout()

        self.campo_nome = QLineEdit()
        self.campo_nome.setObjectName("nome_operatore_anagrafica")
        modulo.addRow("Nome:", self.campo_nome)
        self.campo_cognome = QLineEdit()
        self.campo_cognome.setObjectName("cognome_operatore_anagrafica")
        modulo.addRow("Cognome:", self.campo_cognome)

        self.campo_categoria = QComboBox()
        self.campo_categoria.setObjectName("categoria_operatore_anagrafica")
        self.campo_categoria.addItem("— Seleziona categoria —", None)
        for codice in CATEGORIE_OPERATORE:
            self.campo_categoria.addItem(ETICHETTE_CATEGORIE_OPERATORE[codice], codice)
        modulo.addRow("Categoria:", self.campo_categoria)

        layout.addLayout(modulo)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self._al_conferma)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def _al_conferma(self):
        if not self.campo_cognome.text().strip():
            QMessageBox.warning(self, "Dati mancanti", "Il cognome dell'operatore è obbligatorio.")
            return
        if self.campo_categoria.currentData() is None:
            QMessageBox.warning(self, "Categoria mancante", "Seleziona una categoria per il nuovo operatore.")
            return
        self.accept()


class _DialogoModificaOperatore(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, operatore: dict):
        super().__init__(parent)
        self._operatore = operatore
        self.setWindowTitle("Modifica operatore")
        self.setObjectName("dialogo_modifica_operatore")
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        modulo = QFormLayout()

        self.campo_nome = QLineEdit(operatore["nome_canonico"])
        self.campo_nome.setObjectName("nome_operatore_anagrafica")
        modulo.addRow("Nome:", self.campo_nome)

        self.campo_cognome = QLineEdit(operatore["cognome_canonico"])
        self.campo_cognome.setObjectName("cognome_operatore_anagrafica")
        modulo.addRow("Cognome:", self.campo_cognome)

        self.campo_categoria = QComboBox()
        self.campo_categoria.setObjectName("categoria_operatore_anagrafica")
        for codice in CATEGORIE_OPERATORE:
            self.campo_categoria.addItem(ETICHETTE_CATEGORIE_OPERATORE[codice], codice)
        indice = self.campo_categoria.findData(operatore["categoria_operatore"])
        self.campo_categoria.setCurrentIndex(max(indice, 0))
        modulo.addRow("Categoria:", self.campo_categoria)

        layout.addLayout(modulo)

        avviso = QLabel(
            "La correzione riguarda solo l'anagrafica corrente: gli eventi già "
            "registrati nei singoli moduli non vengono modificati."
        )
        avviso.setWordWrap(True)
        avviso.setObjectName("avviso_modifica_operatore")
        layout.addWidget(avviso)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self._al_conferma)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def _al_conferma(self):
        if not self.campo_cognome.text().strip():
            QMessageBox.warning(self, "Dati mancanti", "Il cognome dell'operatore è obbligatorio.")
            return
        self.accept()


_STATI_MOSTRATI = ("Attivo", "Disattivato")


_ETICHETTE_AZIONI = ("Modifica", "Disattiva", "Riattiva")


def _larghezza_per_voci(menu: QComboBox) -> int:
    """Documentazione della versione portfolio."""
    metriche = menu.fontMetrics()
    piu_lunga = max(
        (metriche.horizontalAdvance(menu.itemText(i)) for i in range(menu.count())),
        default=0,
    )

    return piu_lunga + 52


def _pulsante_azione(testo: str, nome_oggetto: str,
                     larghezza: int = 0, altezza: int = 0) -> QPushButton:
    """Documentazione della versione portfolio."""
    pulsante = QPushButton(testo)
    pulsante.setObjectName(nome_oggetto)
    pulsante.setCursor(Qt.PointingHandCursor)
    pulsante.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    if larghezza:
        pulsante.setFixedWidth(larghezza)
    if altezza:
        pulsante.setMinimumHeight(altezza)
    return pulsante


def _contenitore_azioni(genitore=None) -> QWidget:
    """Documentazione della versione portfolio."""
    contenitore = QWidget(genitore)
    contenitore.setObjectName("azioni_riga_anagrafica")
    layout = QHBoxLayout(contenitore)
    layout.setContentsMargins(8, _MARGINE_VERTICALE_AZIONI, 8, _MARGINE_VERTICALE_AZIONI)
    layout.setSpacing(_SPAZIO_FRA_PULSANTI)
    layout.setAlignment(Qt.AlignVCenter)
    return contenitore


def _azioni_di_prova(genitore, larghezza: int = 0, altezza: int = 0) -> QWidget:
    """Documentazione della versione portfolio."""
    contenitore = _contenitore_azioni(genitore)
    for testo, nome in (("Modifica", "modifica_operatore_anagrafica"),
                        ("Disattiva", "disattiva_operatore_anagrafica")):
        contenitore.layout().addWidget(
            _pulsante_azione(testo, nome, larghezza, altezza))
    return contenitore


class _ContenutoGestioneOperatori:
    """Documentazione della versione portfolio."""

    def _costruisci_contenuto(self, con_chiusura=False):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        intestazione = QHBoxLayout()
        titolo = QLabel("Anagrafica Operatori")
        titolo.setObjectName("titolo_anagrafica_operatori")
        intestazione.addWidget(titolo)
        intestazione.addStretch()
        pulsante_nuovo = QPushButton("+ Nuovo operatore")
        pulsante_nuovo.setObjectName("nuovo_operatore_anagrafica")
        pulsante_nuovo.clicked.connect(self._nuovo_operatore)
        intestazione.addWidget(pulsante_nuovo)
        layout.addLayout(intestazione)

        descrizione = QLabel("Gestione e consultazione degli operatori autorizzati nei moduli Control Room Manager Demo.")
        descrizione.setObjectName("sottotitolo_anagrafica_operatori")
        descrizione.setWordWrap(True)
        layout.addWidget(descrizione)


        barra_ricerca = QHBoxLayout()
        barra_ricerca.setSpacing(10)

        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setObjectName("ricerca_anagrafica_operatori")
        self._campo_ricerca.setPlaceholderText("Cerca nome o cognome...")
        self._campo_ricerca.setMinimumWidth(200)
        self._campo_ricerca.textChanged.connect(lambda _: self._aggiorna_elenco())
        barra_ricerca.addWidget(self._campo_ricerca, stretch=1)

        self._filtro_categoria = QComboBox()
        self._filtro_categoria.setObjectName("filtro_categoria_anagrafica")
        self._filtro_categoria.addItem("Tutte le categorie", _TUTTE_LE_CATEGORIE)
        for codice in CATEGORIE_OPERATORE:
            self._filtro_categoria.addItem(ETICHETTE_CATEGORIE_OPERATORE[codice], codice)
        self._filtro_categoria.currentIndexChanged.connect(lambda _: self._aggiorna_elenco())
        barra_ricerca.addWidget(self._filtro_categoria)

        self._filtro_stato = QComboBox()
        self._filtro_stato.setObjectName("filtro_stato_anagrafica")
        for valore, etichetta in _ETICHETTE_FILTRO_STATO:
            self._filtro_stato.addItem(etichetta, valore)
        self._filtro_stato.currentIndexChanged.connect(lambda _: self._aggiorna_elenco())
        barra_ricerca.addWidget(self._filtro_stato)

        for menu in (self._filtro_categoria, self._filtro_stato):
            menu.setMinimumWidth(_larghezza_per_voci(menu))
            menu.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        layout.addLayout(barra_ricerca)

        self._tabella = QTableWidget(0, len(_INTESTAZIONI))
        self._tabella.setObjectName("tabella_anagrafica_operatori")
        self._tabella.setHorizontalHeaderLabels(_INTESTAZIONI)
        self._tabella.verticalHeader().setVisible(False)
        self._tabella.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabella.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabella.setShowGrid(False)
        self._prepara_colonne()
        layout.addWidget(self._tabella, stretch=1)

        self._stato_vuoto = QLabel("")
        self._stato_vuoto.setObjectName("stato_vuoto_anagrafica_operatori")
        self._stato_vuoto.setAlignment(Qt.AlignCenter)
        self._stato_vuoto.hide()
        layout.addWidget(self._stato_vuoto)

        self._etichetta_conteggio = QLabel("")
        self._etichetta_conteggio.setObjectName("conteggio_anagrafica_operatori")
        layout.addWidget(self._etichetta_conteggio)

        if con_chiusura:
            chiudi = QDialogButtonBox(QDialogButtonBox.Close)
            chiudi.setObjectName("chiudi_anagrafica_operatori")
            chiudi.rejected.connect(self.reject)
            chiudi.accepted.connect(self.accept)
            layout.addWidget(chiudi)

        self._aggiorna_elenco()

    def _prepara_colonne(self):
        """Documentazione della versione portfolio."""
        self._larghezza_pulsante_azione, self._altezza_pulsante_azione = (
            self._misura_pulsante_azione()
        )

        intestazione = self._tabella.horizontalHeader()
        intestazione.setMinimumSectionSize(_LARGHEZZA_MINIMA_COLONNA)
        intestazione.setStretchLastSection(False)

        for colonna in (0, 1):
            intestazione.setSectionResizeMode(colonna, QHeaderView.Stretch)

        larghezze = self._larghezze_colonne()
        for colonna, larghezza in larghezze.items():
            intestazione.setSectionResizeMode(colonna, QHeaderView.Fixed)
            self._tabella.setColumnWidth(colonna, larghezza)


        verticale = self._tabella.verticalHeader()
        verticale.setSectionResizeMode(QHeaderView.Fixed)
        verticale.setDefaultSectionSize(self._altezza_riga())

        self._tabella.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def _larghezze_colonne(self) -> dict[int, int]:
        """Documentazione della versione portfolio."""
        metriche = self._tabella.fontMetrics()

        def per_testi(testi, intestazione):
            piu_lungo = max(
                [metriche.horizontalAdvance(t) for t in testi]
                + [metriche.horizontalAdvance(intestazione)]
            )
            return piu_lungo + _ARIA_CELLA

        return {
            2: per_testi(ETICHETTE_CATEGORIE_OPERATORE.values(), _INTESTAZIONI[2]),
            3: per_testi(_STATI_MOSTRATI, _INTESTAZIONI[3]),
            4: max(self._larghezza_azioni(), per_testi([], _INTESTAZIONI[4])),
        }

    def _misura_pulsante_azione(self) -> tuple[int, int]:
        """Documentazione della versione portfolio."""
        larghezza = altezza = 0
        for testo in _ETICHETTE_AZIONI:
            campione = _pulsante_azione(testo, "modifica_operatore_anagrafica")
            campione.setParent(self._tabella)
            campione.ensurePolished()
            larghezza = max(larghezza, campione.sizeHint().width())
            altezza = max(altezza, campione.sizeHint().height())
            campione.deleteLater()
        return larghezza, altezza

    def _larghezza_azioni(self) -> int:
        """Documentazione della versione portfolio."""
        campione = _azioni_di_prova(
            self._tabella, self._larghezza_pulsante_azione, self._altezza_pulsante_azione)
        campione.ensurePolished()
        larghezza = campione.sizeHint().width()
        campione.deleteLater()
        return larghezza

    def _altezza_riga(self) -> int:
        """Documentazione della versione portfolio."""
        return max(
            self._altezza_pulsante_azione + 2 * _MARGINE_VERTICALE_AZIONI,
            _ALTEZZA_MINIMA_RIGA,
        )

    def _aggiorna_elenco(self):
        stato = self._filtro_stato.currentData()
        risultati = cerca_operatori(
            self._campo_ricerca.text(), categoria=self._filtro_categoria.currentData(), stato=stato,
        )
        self._tabella.setRowCount(len(risultati))
        for riga, operatore in enumerate(risultati):
            self._tabella.setItem(riga, 0, QTableWidgetItem(operatore["nome_canonico"]))
            self._tabella.setItem(riga, 1, QTableWidgetItem(operatore["cognome_canonico"]))
            etichetta_categoria = ETICHETTE_CATEGORIE_OPERATORE.get(
                operatore["categoria_operatore"], operatore["categoria_operatore"]
            )
            self._tabella.setItem(riga, 2, QTableWidgetItem(etichetta_categoria))
            self._tabella.setItem(riga, 3, QTableWidgetItem("Attivo" if operatore["attivo"] else "Disattivato"))


            self._tabella.item(riga, 0).setData(_RUOLO_ID_OPERATORE, operatore["id"])

            self._tabella.setCellWidget(riga, 4, self._crea_azioni_riga(operatore))


        self._uniforma_altezza_righe()

        totale = len(cerca_operatori(stato="tutti"))
        self._stato_vuoto.setText(
            "Nessun operatore corrisponde alla ricerca o ai filtri selezionati."
            if totale else "Nessun operatore registrato."
        )
        self._stato_vuoto.setVisible(not risultati)
        if len(risultati) == totale:
            self._etichetta_conteggio.setText(f"{totale} operatori registrati")
        else:
            self._etichetta_conteggio.setText(f"{len(risultati)} di {totale} operatori")

    def _al_comparsa(self):
        """Documentazione della versione portfolio."""
        self._uniforma_altezza_righe()

    def _uniforma_altezza_righe(self):
        """Documentazione della versione portfolio."""


        necessaria = self._altezza_riga()
        for riga in range(self._tabella.rowCount()):
            cella = self._tabella.cellWidget(riga, 4)
            if cella is None:
                continue
            for pulsante in cella.findChildren(QPushButton):
                necessaria = max(
                    necessaria,
                    pulsante.sizeHint().height() + 2 * _MARGINE_VERTICALE_AZIONI,
                )
        self._tabella.verticalHeader().setDefaultSectionSize(necessaria)
        for riga in range(self._tabella.rowCount()):
            self._tabella.setRowHeight(riga, necessaria)

    def _crea_azioni_riga(self, operatore: dict) -> QWidget:
        """Documentazione della versione portfolio."""
        larghezza = getattr(self, "_larghezza_pulsante_azione", 0)
        altezza = getattr(self, "_altezza_pulsante_azione", 0)
        contenitore = _contenitore_azioni()
        layout = contenitore.layout()

        pulsante_modifica = _pulsante_azione(
            "Modifica", "modifica_operatore_anagrafica", larghezza, altezza)
        pulsante_modifica.clicked.connect(
            lambda _, id_operatore=operatore["id"]: self._modifica(id_operatore)
        )
        layout.addWidget(pulsante_modifica)

        if operatore["attivo"]:
            pulsante_stato = _pulsante_azione(
                "Disattiva", "disattiva_operatore_anagrafica", larghezza, altezza)
            pulsante_stato.clicked.connect(
                lambda _, id_operatore=operatore["id"]: self._disattiva(id_operatore)
            )
        else:
            pulsante_stato = _pulsante_azione(
                "Riattiva", "riattiva_operatore_anagrafica", larghezza, altezza)
            pulsante_stato.clicked.connect(
                lambda _, id_operatore=operatore["id"]: self._riattiva(id_operatore)
            )
        layout.addWidget(pulsante_stato)

        return contenitore

    def _trova(self, id_operatore: int) -> dict | None:
        return next((o for o in cerca_operatori(stato="tutti") if o["id"] == id_operatore), None)

    def _nuovo_operatore(self):
        finestra = _DialogoNuovoOperatoreManuale(self)
        if finestra.exec() != QDialog.Accepted:
            return

        nome = finestra.campo_nome.text()
        cognome = finestra.campo_cognome.text()
        categoria = finestra.campo_categoria.currentData()

        esistente = trova_operatore(nome, cognome)
        if esistente is not None and not esistente["attivo"]:
            risposta = QMessageBox.question(
                self, "Operatore disattivato",
                f"\"{nome_completo(esistente)}\" è presente in anagrafica ma risulta disattivato.\n"
                "Vuoi riattivarlo?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if risposta == QMessageBox.Yes:
                riattiva_operatore(esistente["id"])
            self._aggiorna_elenco()
            return

        operatore = registra_operatore(nome, cognome, categoria)
        if esistente is not None:
            QMessageBox.information(
                self, "Operatore già presente",
                f"\"{nome_completo(operatore)}\" era già nell'anagrafica: nessuna nuova voce creata.",
            )

        self._aggiorna_elenco()

    def _modifica(self, id_operatore: int):
        operatore = self._trova(id_operatore)
        if operatore is None:
            self._aggiorna_elenco()
            return

        finestra = _DialogoModificaOperatore(self, operatore)
        if finestra.exec() != QDialog.Accepted:
            return

        nuovo_nome = finestra.campo_nome.text()
        nuovo_cognome = finestra.campo_cognome.text()
        if (nuovo_nome.strip(), nuovo_cognome.strip()) != (operatore["nome_canonico"], operatore["cognome_canonico"]):
            modifica_nome_canonico(id_operatore, nuovo_nome, nuovo_cognome)
        modifica_categoria(id_operatore, finestra.campo_categoria.currentData())

        self._aggiorna_elenco()

    def _disattiva(self, id_operatore: int):
        operatore = self._trova(id_operatore)
        if operatore is None:
            self._aggiorna_elenco()
            return

        risposta = QMessageBox.question(
            self, "Disattivare operatore?",
            f"\"{nome_completo(operatore)}\" non comparirà più nei suggerimenti operativi.\n"
            "Resta consultabile qui e può essere riattivato in qualunque momento.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if risposta != QMessageBox.Yes:
            return

        disattiva_operatore(id_operatore)
        self._aggiorna_elenco()

    def _riattiva(self, id_operatore: int):
        riattiva_operatore(id_operatore)
        self._aggiorna_elenco()


class PannelloGestioneOperatori(QWidget, _ContenutoGestioneOperatori):
    """Documentazione della versione portfolio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("contenuto_anagrafica_operatori")
        self._costruisci_contenuto()

    def showEvent(self, evento):
        super().showEvent(evento)
        self._al_comparsa()


class DialogoGestioneOperatori(QDialog, _ContenutoGestioneOperatori):
    """Documentazione della versione portfolio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anagrafica Operatori")
        self.setObjectName("dialogo_anagrafica_operatori")
        self.setMinimumSize(680, 480)
        self._costruisci_contenuto(con_chiusura=True)

    def showEvent(self, evento):
        super().showEvent(evento)
        self._al_comparsa()
