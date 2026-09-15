"""Documentazione della versione portfolio."""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.registro import logger, motivo_fallback, percorso_file_log
from data.stato_sistema import (
    ATTENZIONE,
    CRITICO,
    ERRORE,
    NON_CONFIGURATO,
    NON_VERIFICATO,
    OK,
    controllo_approfondito,
    stato_rapido,
)

_registro = logger(__name__)


_COLORI = {
    OK:              ("#6FCF97", "rgba(111, 207, 151, 38)", "rgba(111, 207, 151, 120)"),
    ATTENZIONE:      ("#E7BB67", "rgba(231, 187, 103, 42)", "rgba(231, 187, 103, 130)"),
    ERRORE:          ("#FF8A73", "rgba(255, 138, 115, 40)", "rgba(255, 138, 115, 140)"),
    CRITICO:         ("#FFFFFF", "rgba(201, 90, 90, 170)", "#C95A5A"),
    NON_CONFIGURATO: ("#9FB3CE", "rgba(159, 179, 206, 26)", "rgba(159, 179, 206, 90)"),
    NON_VERIFICATO:  ("#9FB3CE", "rgba(159, 179, 206, 26)", "rgba(159, 179, 206, 90)"),
}

FOGLIO_DI_STILE_STATO = """
QDialog#stato_sistema_modern_control_room {
    background-color: #0B1E35;
    color: #F2F2F2;
}
QScrollArea#area_stato_sistema,
QScrollArea#area_stato_sistema > QWidget > QWidget,
QWidget#contenuto_stato_sistema,
QWidget#riga_stato_sistema,
QWidget#comandi_stato_sistema {
    background: transparent;
    border: none;
}
QLabel#titolo_stato_sistema {
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #F2F2F2;
}
QLabel#sottotitolo_stato_sistema { font-size: 12px; color: #9FB3CE; }
QFrame#sezione_stato_sistema {
    background-color: rgba(11, 30, 53, 176);
    border: 1px solid rgba(87, 134, 182, 120);
    border-radius: 14px;
}
QLabel#titolo_sezione_stato {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: #C0E3FF;
}
QLabel#nome_voce_stato { font-size: 13px; color: #C6D3E6; }
QLabel#valore_voce_stato { font-size: 13px; font-weight: 600; color: #F2F2F2; }
QLabel#dettaglio_voce_stato { font-size: 11px; color: #7E90AB; }
QFrame#separatore_stato { background-color: rgba(87, 134, 182, 46); border: none; }
QPushButton#azione_stato_sistema {
    min-height: 32px;
    padding: 6px 14px;
    color: #C6D3E6;
    background: transparent;
    border: 1px solid #32577E;
    border-radius: 9px;
    font-size: 13px;
}
QPushButton#azione_stato_sistema:hover {
    background-color: rgba(31, 112, 206, 40);
    color: #F2F2F2;
    border-color: #4A83BC;
}
QPushButton#azione_primaria_stato {
    min-height: 32px;
    padding: 6px 16px;
    color: #FFFFFF;
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#azione_primaria_stato:hover { background-color: #2C80DF; }
QPushButton#azione_primaria_stato:disabled {
    background-color: rgba(31, 112, 206, 60);
    color: #9FB3CE;
    border-color: #32577E;
}
QScrollBar:vertical {
    background: rgba(5, 16, 30, 122);
    width: 10px; margin: 2px; border-radius: 5px;
}
QScrollBar::handle:vertical { background: #365F89; min-height: 26px; border-radius: 4px; }
QScrollBar::handle:vertical:hover { background: #4D7EAE; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0px; background: transparent;
}
"""


def _pillola(stato: str) -> QLabel:
    """Documentazione della versione portfolio."""
    testo, fondo, bordo = _COLORI.get(stato, _COLORI[NON_VERIFICATO])
    etichetta = QLabel(stato)
    etichetta.setObjectName("pillola_stato")
    etichetta.setAlignment(Qt.AlignCenter)
    etichetta.setStyleSheet(
        f"color: {testo}; background-color: {fondo}; border: 1px solid {bordo};"
        "border-radius: 10px; padding: 2px 10px; font-size: 11px; font-weight: 700;"
        "letter-spacing: 0.4px;"
    )
    return etichetta


class DialogoStatoSistema(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("stato_sistema_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_STATO)
        self.setWindowTitle("Stato sistema")
        self.setMinimumSize(620, 560)
        self.resize(720, 680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        layout.addLayout(self._crea_intestazione())

        self._area = QScrollArea()
        self._area.setObjectName("area_stato_sistema")
        self._area.setWidgetResizable(True)
        self._area.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self._area, stretch=1)

        layout.addLayout(self._crea_comandi())

        self.aggiorna()


    def _crea_intestazione(self) -> QHBoxLayout:
        riga = QHBoxLayout()
        colonna = QVBoxLayout()
        colonna.setSpacing(2)

        titolo = QLabel("Stato sistema")
        titolo.setObjectName("titolo_stato_sistema")
        colonna.addWidget(titolo)

        self._sottotitolo = QLabel("")
        self._sottotitolo.setObjectName("sottotitolo_stato_sistema")
        colonna.addWidget(self._sottotitolo)

        riga.addLayout(colonna)
        riga.addStretch()

        self._pillola_generale = _pillola(OK)
        riga.addWidget(self._pillola_generale, alignment=Qt.AlignTop)
        return riga

    def _crea_comandi(self) -> QHBoxLayout:
        riga = QHBoxLayout()
        riga.setSpacing(8)

        self._pulsante_aggiorna = QPushButton("Aggiorna stato")
        self._pulsante_aggiorna.setObjectName("azione_stato_sistema")
        self._pulsante_aggiorna.clicked.connect(self.aggiorna)
        riga.addWidget(self._pulsante_aggiorna)

        self._pulsante_log = QPushButton("Apri cartella log")
        self._pulsante_log.setObjectName("azione_stato_sistema")
        self._pulsante_log.clicked.connect(self._apri_cartella_log)
        riga.addWidget(self._pulsante_log)

        riga.addStretch()

        self._pulsante_approfondito = QPushButton("Esegui controllo approfondito")
        self._pulsante_approfondito.setObjectName("azione_primaria_stato")
        self._pulsante_approfondito.setToolTip(
            "Verifica integrità del database, vincoli, backup e cartelle. "
            "Richiede qualche secondo e non modifica nulla."
        )
        self._pulsante_approfondito.clicked.connect(self._esegui_approfondito)
        riga.addWidget(self._pulsante_approfondito)

        chiudi = QPushButton("Chiudi")
        chiudi.setObjectName("azione_stato_sistema")
        chiudi.clicked.connect(self.accept)
        riga.addWidget(chiudi)
        return riga


    def aggiorna(self):
        """Documentazione della versione portfolio."""
        self._stato = stato_rapido()
        self._sottotitolo.setText(
            f"Rilevato il {self._stato['quando']} · i controlli pesanti si eseguono su richiesta"
        )
        self._mostra_pillola(self._stato["esito"])
        self._area.setWidget(self._costruisci_contenuto(self._stato["sezioni"]))

    def _mostra_pillola(self, stato: str):
        nuova = _pillola(stato)
        vecchia = self._pillola_generale
        vecchia.parentWidget().layout().replaceWidget(vecchia, nuova)
        vecchia.deleteLater()
        self._pillola_generale = nuova

    def _costruisci_contenuto(self, sezioni: list[dict]) -> QWidget:
        contenuto = QWidget()
        contenuto.setObjectName("contenuto_stato_sistema")
        layout = QVBoxLayout(contenuto)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(10)
        for sezione in sezioni:
            layout.addWidget(self._crea_sezione(sezione))
        layout.addStretch()
        return contenuto

    def _crea_sezione(self, sezione: dict) -> QFrame:
        riquadro = QFrame()
        riquadro.setObjectName("sezione_stato_sistema")
        layout = QVBoxLayout(riquadro)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        intestazione = QHBoxLayout()
        titolo = QLabel(sezione["titolo"].upper())
        titolo.setObjectName("titolo_sezione_stato")
        intestazione.addWidget(titolo)
        intestazione.addStretch()
        intestazione.addWidget(_pillola(sezione["stato"]))
        layout.addLayout(intestazione)

        separatore = QFrame()
        separatore.setObjectName("separatore_stato")
        separatore.setFixedHeight(1)
        layout.addWidget(separatore)

        for voce in sezione["voci"]:
            layout.addWidget(self._crea_voce(voce))
        return riquadro

    def _crea_voce(self, voce: dict) -> QWidget:
        riga = QWidget()
        riga.setObjectName("riga_stato_sistema")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(10)

        nome = QLabel(voce["nome"])
        nome.setObjectName("nome_voce_stato")
        nome.setMinimumWidth(190)
        nome.setWordWrap(True)
        layout.addWidget(nome)

        colonna = QVBoxLayout()
        colonna.setSpacing(0)
        valore = QLabel(voce["valore"])
        valore.setObjectName("valore_voce_stato")
        valore.setWordWrap(True)
        colonna.addWidget(valore)
        if voce["dettaglio"]:
            dettaglio = QLabel(voce["dettaglio"])
            dettaglio.setObjectName("dettaglio_voce_stato")
            dettaglio.setWordWrap(True)
            colonna.addWidget(dettaglio)
        layout.addLayout(colonna, stretch=1)

        if voce["stato"] != OK:
            layout.addWidget(_pillola(voce["stato"]), alignment=Qt.AlignTop)

        if voce["dettaglio"]:
            riga.setToolTip(voce["dettaglio"])
        return riga


    def _apri_cartella_log(self):
        """Documentazione della versione portfolio."""
        from PySide6.QtWidgets import QMessageBox

        percorso = percorso_file_log()
        if percorso is None:
            QMessageBox.information(
                self, "Nessun registro su file",
                "Il registro tecnico non sta scrivendo su file: non c'è una "
                "cartella da aprire.\n\nControlla i permessi della cartella dati.",
            )
            return

        cartella = Path(percorso).parent
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(cartella))):
            _registro.error("Impossibile aprire la cartella dei registri: %s", cartella)
            QMessageBox.warning(
                self, "Cartella non aperta",
                "Non è stato possibile aprire la cartella dei registri tecnici.\n\n"
                f"Si trova in:\n{cartella}",
            )

    def _esegui_approfondito(self):
        """Documentazione della versione portfolio."""
        from PySide6.QtWidgets import QMessageBox

        self._pulsante_approfondito.setEnabled(False)
        self._pulsante_approfondito.setText("Controllo in corso...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        try:
            esito = controllo_approfondito()
        except Exception:


            _registro.error("Controllo approfondito non riuscito", exc_info=True)
            QMessageBox.warning(
                self, "Controllo non riuscito",
                "Non è stato possibile completare il controllo approfondito. "
                "Il dettaglio è nel registro tecnico.",
            )
            return
        finally:
            QApplication.restoreOverrideCursor()
            self._pulsante_approfondito.setEnabled(True)
            self._pulsante_approfondito.setText("Esegui controllo approfondito")

        self.aggiorna()
        DialogoEsitoControllo(self, esito).exec()


class DialogoEsitoControllo(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, esito: dict):
        super().__init__(parent)
        self.setObjectName("stato_sistema_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_STATO)
        self.setWindowTitle("Esito del controllo approfondito")
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        intestazione = QHBoxLayout()
        colonna = QVBoxLayout()
        colonna.setSpacing(2)
        titolo = QLabel("Esito del controllo")
        titolo.setObjectName("titolo_stato_sistema")
        colonna.addWidget(titolo)
        quando = QLabel(f"Eseguito il {esito['quando']}")
        quando.setObjectName("sottotitolo_stato_sistema")
        colonna.addWidget(quando)
        intestazione.addLayout(colonna)
        intestazione.addStretch()
        intestazione.addWidget(_pillola(esito["esito"]), alignment=Qt.AlignTop)
        layout.addLayout(intestazione)

        riquadro = QFrame()
        riquadro.setObjectName("sezione_stato_sistema")
        righe = QVBoxLayout(riquadro)
        righe.setContentsMargins(16, 12, 16, 12)
        righe.setSpacing(6)
        for voce in esito["voci"]:
            righe.addWidget(self._riga(voce))
        layout.addWidget(riquadro)

        problemi = [v for v in esito["voci"] if v["stato"] not in (OK, NON_CONFIGURATO)]
        if problemi:
            nota = QLabel(
                "Il dettaglio tecnico completo è nel registro. Per inviarlo "
                "all'assistenza usa “Esporta diagnostica”."
            )
            nota.setObjectName("dettaglio_voce_stato")
            nota.setWordWrap(True)
            layout.addWidget(nota)

        comandi = QHBoxLayout()
        comandi.addStretch()
        chiudi = QPushButton("Chiudi")
        chiudi.setObjectName("azione_primaria_stato")
        chiudi.clicked.connect(self.accept)
        comandi.addWidget(chiudi)
        layout.addLayout(comandi)

    def _riga(self, voce: dict) -> QWidget:
        riga = QWidget()
        riga.setObjectName("riga_stato_sistema")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(10)

        nome = QLabel(voce["nome"])
        nome.setObjectName("nome_voce_stato")
        nome.setMinimumWidth(190)
        layout.addWidget(nome)

        colonna = QVBoxLayout()
        colonna.setSpacing(0)
        valore = QLabel(voce["valore"])
        valore.setObjectName("valore_voce_stato")
        valore.setWordWrap(True)
        colonna.addWidget(valore)
        if voce["dettaglio"]:
            dettaglio = QLabel(voce["dettaglio"])
            dettaglio.setObjectName("dettaglio_voce_stato")
            dettaglio.setWordWrap(True)
            colonna.addWidget(dettaglio)
        layout.addLayout(colonna, stretch=1)
        layout.addWidget(_pillola(voce["stato"]), alignment=Qt.AlignTop)
        return riga
