"""Documentazione della versione portfolio."""
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.impostazioni import (
    CHIAVE_CASSAFORTE,
    CHIAVE_PASSAGGIO_CONSEGNE,
    CHIAVE_OGGETTI_SMARRITI,
    CHIAVE_PROSPETTI_CONSEGNA_RADIO,
    CHIAVE_PROSPETTI_GESTIONE_RADIO,
    cartella_esiste,
    carica_impostazioni,
    salva_impostazioni,
)
from config.registro import percorso_file_log, raccogli_diagnostica
from ui.impostazioni.stile import FOGLIO_DI_STILE_IMPOSTAZIONI
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO


PERCORSO_FOTO_SFONDO = Path(__file__).parent.parent / "assets" / "images" / "demo_impostazioni.jpg"


ETICHETTE_CARTELLE = {
    "cartella_rapporti": "Cartella Rapporti Giornalieri",
    CHIAVE_PROSPETTI_GESTIONE_RADIO: "Prospetto Radio",
    CHIAVE_PROSPETTI_CONSEGNA_RADIO: "Consegna Radio",
    "cartella_prospetti_chiavi": "Cartella Prospetti Chiavi",
    CHIAVE_OGGETTI_SMARRITI: "Oggetti Smarriti",
    CHIAVE_CASSAFORTE: "Cassaforte",
    CHIAVE_PASSAGGIO_CONSEGNE: "Passaggio di Consegne",
    "cartella_backup": "Cartella di Backup",
}


class SchermataImpostazioni(PaginaConSfondo):
    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, HOME_OPACITA_VELO)
        self.setObjectName("impostazioni_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_IMPOSTAZIONI)
        self._campi_percorso = {}
        self._avvisi = {}
        self._costruisci_interfaccia()
        self._carica_valori_correnti()

    def _costruisci_interfaccia(self):
        layout_principale = QVBoxLayout(self)
        layout_principale.setContentsMargins(40, 16, 40, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_impostazioni")
        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(32, 28, 32, 28)
        layout_pannello.setSpacing(14)

        titolo = QLabel("Impostazioni")
        titolo.setObjectName("titolo_impostazioni")
        layout_pannello.addWidget(titolo)

        sottotitolo = QLabel(
            "Configura le destinazioni dei prospetti, dei rapporti e dei backup. "
            "I percorsi non disponibili vengono segnalati senza modificare i dati salvati."
        )
        sottotitolo.setObjectName("sottotitolo_impostazioni")
        sottotitolo.setWordWrap(True)
        layout_pannello.addWidget(sottotitolo)

        sezione_percorsi = QLabel("PERCORSI E ARCHIVI")
        sezione_percorsi.setObjectName("sezione_impostazioni")
        layout_pannello.addWidget(sezione_percorsi)

        contenitore_percorsi = QFrame()
        contenitore_percorsi.setObjectName("contenitore_percorsi_impostazioni")
        griglia = QGridLayout(contenitore_percorsi)
        griglia.setContentsMargins(18, 16, 18, 16)
        griglia.setHorizontalSpacing(12)
        griglia.setVerticalSpacing(10)
        griglia.setColumnStretch(1, 1)

        for riga, (chiave, etichetta) in enumerate(ETICHETTE_CARTELLE.items()):
            etichetta_percorso = QLabel(etichetta)
            etichetta_percorso.setObjectName("etichetta_percorso_impostazioni")
            griglia.addWidget(etichetta_percorso, riga, 0)

            campo = QLineEdit()
            campo.setObjectName("percorso_impostazioni")
            campo.setProperty("chiave", chiave)
            campo.setReadOnly(True)
            self._campi_percorso[chiave] = campo
            griglia.addWidget(campo, riga, 1)

            pulsante_sfoglia = QPushButton("Sfoglia...")
            pulsante_sfoglia.setObjectName("sfoglia_impostazioni")
            pulsante_sfoglia.setProperty("chiave", chiave)
            pulsante_sfoglia.clicked.connect(lambda _, c=chiave: self._scegli_cartella(c))
            griglia.addWidget(pulsante_sfoglia, riga, 2)

            avviso = QLabel("")
            avviso.setObjectName("avviso_percorso_impostazioni")
            self._avvisi[chiave] = avviso
            griglia.addWidget(avviso, riga, 3)

        layout_pannello.addWidget(contenitore_percorsi)

        pulsante_salva = QPushButton("Salva")
        pulsante_salva.setObjectName("salva_impostazioni")
        pulsante_salva.clicked.connect(self._salva)
        riga_salva = QHBoxLayout()
        riga_salva.addStretch()
        riga_salva.addWidget(pulsante_salva)
        layout_pannello.addLayout(riga_salva)


        titolo_diagnostica = QLabel("Diagnostica")
        titolo_diagnostica.setObjectName("sezione_impostazioni")
        layout_pannello.addWidget(titolo_diagnostica)


        scheda_stato = QFrame()
        scheda_stato.setObjectName("scheda_operatori_impostazioni")
        riga_stato = QHBoxLayout(scheda_stato)
        riga_stato.setContentsMargins(18, 14, 18, 14)
        descrizione_stato = QLabel(
            "Versione, schema del database, backup, registro tecnico, cartelle e "
            "spazio disco in una sola schermata. Comprende un controllo "
            "approfondito su richiesta, in sola lettura: non modifica nulla."
        )
        descrizione_stato.setObjectName("descrizione_operatori_impostazioni")
        descrizione_stato.setWordWrap(True)
        riga_stato.addWidget(descrizione_stato, stretch=1)

        pulsante_stato = QPushButton("Stato sistema...")
        pulsante_stato.setObjectName("apri_stato_sistema_impostazioni")
        pulsante_stato.clicked.connect(self._apri_stato_sistema)
        riga_stato.addWidget(pulsante_stato)
        layout_pannello.addWidget(scheda_stato)

        scheda_diagnostica = QFrame()
        scheda_diagnostica.setObjectName("scheda_operatori_impostazioni")
        riga_diagnostica = QHBoxLayout(scheda_diagnostica)
        riga_diagnostica.setContentsMargins(18, 14, 18, 14)
        descrizione_diagnostica = QLabel(
            "Raccoglie in un unico file i registri tecnici, le informazioni "
            "sull\u2019ambiente e un controllo del database, da allegare a una "
            "segnalazione. Non include il database n\u00e9 i documenti operativi."
        )
        descrizione_diagnostica.setObjectName("descrizione_operatori_impostazioni")
        descrizione_diagnostica.setWordWrap(True)
        riga_diagnostica.addWidget(descrizione_diagnostica, stretch=1)

        pulsante_diagnostica = QPushButton("Esporta diagnostica...")
        pulsante_diagnostica.setObjectName("esporta_diagnostica_impostazioni")
        pulsante_diagnostica.clicked.connect(self._esporta_diagnostica)
        riga_diagnostica.addWidget(pulsante_diagnostica)
        layout_pannello.addWidget(scheda_diagnostica)

        layout_pannello.addStretch()

        area = QScrollArea()
        area.setObjectName("area_impostazioni")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setWidget(pannello)
        layout_principale.addWidget(area, stretch=1)

    def _apri_stato_sistema(self):
        """Documentazione della versione portfolio."""
        from ui.impostazioni.stato_sistema import DialogoStatoSistema

        DialogoStatoSistema(self).exec()

    def _esporta_diagnostica(self):
        """Documentazione della versione portfolio."""
        cartella = QFileDialog.getExistingDirectory(
            self, "Dove salvare il pacchetto diagnostico"
        )
        if not cartella:
            return

        try:
            percorso = raccogli_diagnostica(cartella)
        except OSError as errore:
            QMessageBox.warning(
                self, "Diagnostica non esportata",
                f"Non \u00e8 stato possibile creare il pacchetto: {errore}",
            )
            return

        dove_log = percorso_file_log()
        nota = "" if dove_log else (
            "\n\nAttenzione: il registro tecnico non sta scrivendo su file, "
            "quindi il pacchetto contiene solo le informazioni di ambiente."
        )
        QMessageBox.information(
            self, "Diagnostica esportata",
            f"Pacchetto creato in:\n{percorso}\n\n"
            f"Non contiene il database n\u00e9 i documenti operativi.{nota}",
        )

    def _carica_valori_correnti(self):
        impostazioni = carica_impostazioni()
        for chiave, campo in self._campi_percorso.items():
            percorso = impostazioni.get(chiave, "")
            campo.setText(percorso)
            self._aggiorna_avviso(chiave, percorso)

    def _scegli_cartella(self, chiave):
        cartella_scelta = QFileDialog.getExistingDirectory(self, "Scegli cartella")
        if cartella_scelta:
            self._campi_percorso[chiave].setText(cartella_scelta)
            self._aggiorna_avviso(chiave, cartella_scelta)

    def _aggiorna_avviso(self, chiave, percorso):
        if percorso and not cartella_esiste(percorso):
            self._avvisi[chiave].setText("Cartella non trovata")
        else:
            self._avvisi[chiave].setText("")

    def _salva(self):
        impostazioni = {chiave: campo.text() for chiave, campo in self._campi_percorso.items()}
        salva_impostazioni(impostazioni)
        for chiave, percorso in impostazioni.items():
            self._aggiorna_avviso(chiave, percorso)
        QMessageBox.information(self, "Impostazioni", "Impostazioni salvate.")
