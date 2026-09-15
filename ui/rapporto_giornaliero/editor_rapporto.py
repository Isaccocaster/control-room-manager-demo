"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from documents.word.rapporto_giornaliero import (
    COLONNE_ANTINTRUSIONE,
    RIGHE_DATI_ANTINTRUSIONE,
    leggi_dati_editabili,
    salva_dati_editabili,
)
from ui.comune.campo_orario import crea_campo_orario, testo_orario
from ui.rapporto_giornaliero.stile import FOGLIO_DI_STILE_RAPPORTO, PERCORSO_FOTO_RAPPORTO
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO, TESTO_ATTENUATO

_INTESTAZIONI_COLONNE = ["Locale", "Orario disinserimento", "Orario inserimento", "Note"]


_COLONNE_ORARIO = (1, 2)


class _DelegateOrario(QStyledItemDelegate):
    """Documentazione della versione portfolio."""

    def createEditor(self, parent, option, index):
        return crea_campo_orario(index.data(Qt.EditRole))

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        model.setData(index, testo_orario(editor), Qt.EditRole)


class EditorRapporto(PaginaConSfondo):
    """Documentazione della versione portfolio."""

    def __init__(self, al_salva_e_chiudi=None):
        super().__init__(PERCORSO_FOTO_RAPPORTO, opacita_velo=HOME_OPACITA_VELO)
        self.setObjectName("editor_rapporto_moderno")
        self.setStyleSheet(FOGLIO_DI_STILE_RAPPORTO)
        self._percorso_file = None
        self._data_turno = None
        self._al_salva_e_chiudi = al_salva_e_chiudi


        self._sola_lettura = False
        self._al_ritorno = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        layout.addWidget(self._crea_intestazione())

        titolo_antintrusione = QLabel("ANTI-INTRUSIONE")
        titolo_antintrusione.setObjectName("titolo_editor_rapporto")
        layout.addWidget(titolo_antintrusione)

        self._tabella = QTableWidget(RIGHE_DATI_ANTINTRUSIONE, len(_INTESTAZIONI_COLONNE))
        self._tabella.setObjectName("tabella_antintrusione")
        self._tabella.setHorizontalHeaderLabels(_INTESTAZIONI_COLONNE)
        self._tabella.verticalHeader().setVisible(False)
        self._tabella.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tabella.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabella.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabella.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._delegate_orario = _DelegateOrario(self._tabella)
        for indice_colonna in _COLONNE_ORARIO:
            self._tabella.setItemDelegateForColumn(indice_colonna, self._delegate_orario)
        for indice_riga in range(RIGHE_DATI_ANTINTRUSIONE):
            for indice_colonna in range(len(_INTESTAZIONI_COLONNE)):
                self._tabella.setItem(indice_riga, indice_colonna, QTableWidgetItem(""))
        layout.addWidget(self._tabella, stretch=2)

        titolo_note = QLabel("NOTE")
        titolo_note.setObjectName("titolo_editor_rapporto")
        layout.addWidget(titolo_note)

        self._campo_note = QTextEdit()
        self._campo_note.setObjectName("note_rapporto")
        layout.addWidget(self._campo_note, stretch=1)

    def _crea_intestazione(self) -> QWidget:
        pannello = QFrame()
        pannello.setObjectName("pannello_home")
        layout = QHBoxLayout(pannello)
        layout.setContentsMargins(16, 10, 16, 10)

        self._etichetta_operatore = QLabel("")
        self._etichetta_operatore.setStyleSheet("font-weight: 600;")
        self._etichetta_operatore.setWordWrap(True)
        layout.addWidget(self._etichetta_operatore)

        layout.addStretch()

        self._etichetta_sola_lettura = QLabel("Sola consultazione")
        self._etichetta_sola_lettura.setObjectName("etichetta_sola_lettura")
        self._etichetta_sola_lettura.hide()
        layout.addWidget(self._etichetta_sola_lettura)

        self._etichetta_data_orario = QLabel("")
        self._etichetta_data_orario.setStyleSheet(f"color: {TESTO_ATTENUATO};")
        self._etichetta_data_orario.setWordWrap(True)
        layout.addWidget(self._etichetta_data_orario)


        self._pulsante_ritorno = QPushButton("← Torna al Calendario")
        self._pulsante_ritorno.setObjectName("torna_al_calendario")
        self._pulsante_ritorno.setCursor(Qt.PointingHandCursor)
        self._pulsante_ritorno.clicked.connect(self._al_click_ritorno)
        self._pulsante_ritorno.hide()
        layout.addWidget(self._pulsante_ritorno)


        self._pulsante_salva_e_chiudi = QPushButton("Salva e chiudi")

        self._pulsante_salva_e_chiudi.setObjectName("apri_giornata")
        self._pulsante_salva_e_chiudi.setCursor(Qt.PointingHandCursor)
        self._pulsante_salva_e_chiudi.clicked.connect(self._al_click_salva_e_chiudi)
        layout.addWidget(self._pulsante_salva_e_chiudi)

        return pannello

    def _al_click_salva_e_chiudi(self):
        if self._al_salva_e_chiudi is not None:
            self._al_salva_e_chiudi()

    def _al_click_ritorno(self):
        if self._al_ritorno is not None:
            self._al_ritorno()


    def imposta_sola_lettura(self, attiva: bool, al_ritorno=None):
        """Documentazione della versione portfolio."""
        self._sola_lettura = attiva
        self._al_ritorno = al_ritorno

        self._tabella.setEditTriggers(
            QAbstractItemView.NoEditTriggers if attiva else QAbstractItemView.AllEditTriggers
        )
        self._campo_note.setReadOnly(attiva)
        self._etichetta_sola_lettura.setVisible(attiva)
        self._pulsante_ritorno.setVisible(attiva)
        self._pulsante_salva_e_chiudi.setVisible(not attiva)

    def e_in_sola_lettura(self) -> bool:
        return self._sola_lettura


    def carica(self, percorso_file, operatore: str, data_turno: str, orario: str):
        self._percorso_file = percorso_file
        self._data_turno = data_turno
        self._etichetta_operatore.setText(f"Addetto alla SOC: {operatore}")
        self._etichetta_data_orario.setText(f"{data_turno}   ·   {orario}")

        dati = leggi_dati_editabili(percorso_file)
        for indice_riga, riga_dati in enumerate(dati["antintrusione"]):
            for indice_colonna, nome_colonna in enumerate(COLONNE_ANTINTRUSIONE):
                self._tabella.item(indice_riga, indice_colonna).setText(riga_dati.get(nome_colonna, ""))
        self._campo_note.setPlainText(dati["note"])

    def aggiorna_intestazione(self, percorso_file, operatore: str, orario: str):
        """Documentazione della versione portfolio."""
        self._percorso_file = percorso_file
        self._etichetta_operatore.setText(f"Addetto alla SOC: {operatore}")
        self._etichetta_data_orario.setText(f"{self._data_turno}   ·   {orario}")

    def dati_correnti(self) -> dict:
        antintrusione = []
        for indice_riga in range(RIGHE_DATI_ANTINTRUSIONE):
            antintrusione.append({
                nome_colonna: self._tabella.item(indice_riga, indice_colonna).text()
                for indice_colonna, nome_colonna in enumerate(COLONNE_ANTINTRUSIONE)
            })
        return {"antintrusione": antintrusione, "note": self._campo_note.toPlainText()}

    def salva_su_file(self):
        """Documentazione della versione portfolio."""
        if self._percorso_file is None or self._sola_lettura:
            return
        salva_dati_editabili(self._percorso_file, self.dati_correnti())
