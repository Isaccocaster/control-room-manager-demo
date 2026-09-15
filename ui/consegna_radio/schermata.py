"""Documentazione della versione portfolio."""
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
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
    CHIAVE_PROSPETTI_CONSEGNA_RADIO,
    cartella_esiste,
    carica_impostazioni,
)
from data.consegne_radio import (
    cicli_consegne,
    mese_di_riferimento,
    periodi_storico,
    radio_fuori,
    registra_consegna,
    registra_riconsegna,
    storico_movimentazioni,
)
from documents.excel.prospetto_consegna_radio import genera_prospetto_mese
from ui.comune.archivio_anno_mese import DialogoArchivioAnnoMese
from ui.comune.icone import SIMBOLO_STORICO, applica_icona_pulsante
from ui.comune.campo_operatore import applica_autocomplete_operatori, risolvi_operatore_confermato
from ui.consegna_radio.stile import FOGLIO_DI_STILE_CONSEGNA_RADIO
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO

PERCORSO_FOTO_SFONDO = Path(__file__).parent.parent / "assets" / "images" / "demo_consegna_radio.jpg"


class _DialogoNuovaConsegna(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("dialogo_nuova_consegna_radio")
        self.setWindowTitle("Nuova consegna radio")
        self.setMinimumWidth(520)

        layout = QFormLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(14)

        self.campo_radio = QLineEdit()
        self.campo_radio.setObjectName("campo_identificativo_radio")
        self.campo_radio.setPlaceholderText("Es. DEMO-RAD-001")
        layout.addRow("Numero/identificativo radio:", self.campo_radio)


        self.campo_cognome = QLineEdit()
        self.campo_cognome.setObjectName("campo_operatore_consegna_radio")
        self.campo_cognome.setPlaceholderText("Nome e cognome dell'operatore")
        applica_autocomplete_operatori(self.campo_cognome)
        layout.addRow("Operatore:", self.campo_cognome)

        self.campo_auricolare = QComboBox()
        self.campo_auricolare.setObjectName("campo_auricolare_consegna_radio")
        self.campo_auricolare.addItems(["No", "Sì"])
        layout.addRow("Auricolare:", self.campo_auricolare)

        self.campo_note = QLineEdit()
        self.campo_note.setObjectName("campo_note_consegna_radio")
        self.campo_note.setPlaceholderText("Informazioni aggiuntive")
        layout.addRow("Note (opzionale):", self.campo_note)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.setObjectName("azioni_nuova_consegna_radio")
        conferma = pulsanti.button(QDialogButtonBox.Ok)
        conferma.setText("Registra consegna")
        conferma.setObjectName("conferma_nuova_consegna_radio")
        annulla = pulsanti.button(QDialogButtonBox.Cancel)
        annulla.setText("Annulla")
        annulla.setObjectName("annulla_nuova_consegna_radio")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addRow(pulsanti)

    def valori(self):
        return (
            self.campo_radio.text().strip(),
            self.campo_cognome.text().strip(),
            self.campo_auricolare.currentText(),
            self.campo_note.text().strip(),
        )


class _DialogoRiconsegna(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, identificativo_radio: str):
        super().__init__(parent)
        self.setObjectName("dialogo_riconsegna_radio")
        self.setWindowTitle("Riconsegna radio")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Nome e cognome di chi riconsegna la radio {identificativo_radio}:"))

        self.campo = QLineEdit()
        applica_autocomplete_operatori(self.campo)
        layout.addWidget(self.campo)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        conferma = pulsanti.button(QDialogButtonBox.Ok)
        conferma.setText("Registra riconsegna")
        conferma.setObjectName("conferma_riconsegna_radio")
        annulla = pulsanti.button(QDialogButtonBox.Cancel)
        annulla.setText("Annulla")
        annulla.setObjectName("annulla_riconsegna_radio")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def valore(self) -> str | None:
        if self.exec() != QDialog.Accepted:
            return None
        valore = self.campo.text().strip()
        return valore or None


class SchermataConsegnaRadio(PaginaConSfondo):
    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, opacita_velo=HOME_OPACITA_VELO)
        self.setObjectName("consegna_radio_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_CONSEGNA_RADIO)

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(40, 16, 40, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_consegna_radio")

        layout_principale = QVBoxLayout(pannello)
        layout_principale.setContentsMargins(32, 28, 32, 28)
        layout_principale.setSpacing(14)

        titolo = QLabel("Consegna Radio")
        titolo.setObjectName("titolo_consegna_radio")
        layout_principale.addWidget(titolo)

        barra = QHBoxLayout()
        pulsante_nuova = QPushButton("+ Nuova consegna")
        pulsante_nuova.setObjectName("nuova_consegna_radio")
        pulsante_nuova.clicked.connect(self._nuova_consegna)
        barra.addWidget(pulsante_nuova)


        pulsante_storico = QPushButton("Storico")
        pulsante_storico.setObjectName("storico_consegna_radio")
        applica_icona_pulsante(pulsante_storico, SIMBOLO_STORICO)
        pulsante_storico.clicked.connect(self._apri_storico)
        barra.addWidget(pulsante_storico)
        barra.addStretch()
        layout_principale.addLayout(barra)

        self._sottotitolo = QLabel("Radio attualmente fuori")
        self._sottotitolo.setObjectName("stato_consegna_radio")
        layout_principale.addWidget(self._sottotitolo)

        self._area_risultati = QScrollArea()
        self._area_risultati.setObjectName("elenco_radio_fuori")
        self._area_risultati.setWidgetResizable(True)
        self._area_risultati.setFrameShape(QFrame.NoFrame)

        self._contenitore_righe = QWidget()
        self._contenitore_righe.setObjectName("contenitore_radio_fuori")
        self._layout_righe = QVBoxLayout(self._contenitore_righe)
        self._layout_righe.setContentsMargins(0, 0, 0, 0)
        self._layout_righe.setSpacing(8)
        self._area_risultati.setWidget(self._contenitore_righe)

        layout_principale.addWidget(self._area_risultati, stretch=1)

        layout_esterno.addWidget(pannello, stretch=1)

        self._aggiorna_elenco()

    def _apri_storico(self):
        self._crea_dialogo_storico().exec()

    def _crea_dialogo_storico(self) -> DialogoArchivioAnnoMese:
        """Documentazione della versione portfolio."""
        dialogo = DialogoArchivioAnnoMese(
            self, "Storico Consegna Radio",
            colonne=[
                ("DATA", "data"), ("ORA", "ora"), ("OPERAZIONE", "operazione"),
                ("RADIO", "elemento"), ("PERSONA", "persona"), ("DETTAGLI", "dettagli"),
            ],
            periodi=periodi_storico,
            carica_mese=lambda anno, mese, testo: storico_movimentazioni(
                testo_ricerca=testo, anno=anno, mese=mese,
            ),
            dettaglio=self._dettaglio_evento,


            colonne_cicli=[
                ("RADIO", "elemento"), ("USCITA", "uscita_testo"),
                ("RIENTRO", "rientro_testo"), ("STATO", "stato"),
            ],
            carica_cicli=lambda testo: [self._evento_da_ciclo(c) for c in cicli_consegne(testo)],
            dettaglio_cicli=self._dettaglio_ciclo,
        )
        dialogo.setObjectName("dialogo_storico_consegna_radio")
        dialogo.setMinimumSize(760, 560)
        dialogo.resize(920, 680)
        dialogo.setStyleSheet(FOGLIO_DI_STILE_CONSEGNA_RADIO)

        for pulsante in dialogo.findChildren(QPushButton):
            if "Cronologico" in pulsante.text():
                pulsante.setObjectName("modo_cronologico_consegna_radio")
            elif "Cicli uscita/rientro" in pulsante.text():
                pulsante.setObjectName("modo_cicli_consegna_radio")
            elif pulsante.text() == "Chiudi":
                pulsante.setObjectName("chiudi_storico_consegna_radio")
        return dialogo

    @staticmethod
    def _dettaglio_evento(evento: dict):
        voci = [
            ("Data", evento["data"]), ("Ora", evento["ora"]),
            ("Operazione", evento["operazione"]), ("Radio", evento["elemento"]),
            ("Persona", evento["persona"]), ("Note", evento.get("note")),
        ]
        if evento.get("data_incerta"):
            voci.append(("Attenzione", "la data del rientro non era registrata "
                                       "(consegne precedenti al 09-09-2026)"))
        return f"{evento['operazione']} — Radio {evento['elemento']}", voci

    @staticmethod
    def _evento_da_ciclo(ciclo: dict) -> dict:
        def testo(data, ora, persona):
            return f"{data} {ora or ''} — {persona or ''}".strip()

        return {
            **ciclo,
            "uscita_testo": testo(ciclo["uscita_data"], ciclo["uscita_ora"], ciclo["uscita_persona"]),
            "rientro_testo": (
                testo(ciclo["rientro_data"], ciclo["rientro_ora"], ciclo["rientro_persona"])
                if ciclo["rientro_data"] else "— ancora fuori —"
            ),
        }

    @staticmethod
    def _dettaglio_ciclo(ciclo: dict):
        return f"{ciclo['stato']} — Radio {ciclo['elemento']}", [
            ("Radio", ciclo["elemento"]), ("Uscita", ciclo["uscita_testo"]),
            ("Rientro", ciclo["rientro_testo"]), ("Stato", ciclo["stato"]),
            ("Note", ciclo.get("note")),
        ]

    def _svuota_elenco(self):
        while self._layout_righe.count():
            item = self._layout_righe.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def _aggiorna_elenco(self):
        self._svuota_elenco()

        righe = radio_fuori()
        if not righe:
            segnaposto = QLabel("Nessuna radio fuori al momento.")
            segnaposto.setObjectName("nessuna_radio_fuori")
            self._layout_righe.addWidget(segnaposto)
        else:
            for consegna in righe:
                self._layout_righe.addWidget(self._crea_riga(consegna))

        self._layout_righe.addStretch()

    def _crea_riga(self, consegna: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_radio_fuori")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()
        intestazione = QLabel(f"Radio {consegna['radio_identificativo']}   —   {consegna['cognome_consegna']}")
        intestazione.setObjectName("identita_radio_fuori")
        layout_testo.addWidget(intestazione)

        dettaglio = QLabel(
            f"Presa il {consegna['data']} alle {consegna['ora_consegna']}"
            f"   —   Auricolare: {consegna['auricolare'] or 'No'}"
        )
        dettaglio.setObjectName("dettaglio_radio_fuori")
        layout_testo.addWidget(dettaglio)

        if consegna.get("note"):
            note = QLabel(consegna["note"])
            note.setObjectName("note_radio_fuori")
            layout_testo.addWidget(note)

        layout.addLayout(layout_testo, stretch=1)

        pulsante_riconsegna = QPushButton("Riconsegna")
        pulsante_riconsegna.setObjectName("riconsegna_radio")
        pulsante_riconsegna.clicked.connect(lambda: self._riconsegna(consegna))
        layout.addWidget(pulsante_riconsegna)

        return riga

    def _nuova_consegna(self):
        finestra = _DialogoNuovaConsegna(self)
        if finestra.exec() != QDialog.Accepted:
            return

        radio_identificativo, cognome, auricolare, note = finestra.valori()
        if not radio_identificativo or not cognome:
            QMessageBox.warning(self, "Dati mancanti", "Numero radio e cognome sono obbligatori.")
            return

        cognome = risolvi_operatore_confermato(self, cognome)
        if cognome is None:
            return

        adesso = datetime.now()
        data_consegna = adesso.strftime("%d-%m-%Y")
        registra_consegna(
            data=data_consegna,
            radio_identificativo=radio_identificativo,
            ora_consegna=adesso.strftime("%H:%M"),
            cognome_consegna=cognome,
            auricolare=auricolare,
            note=note,
        )
        self._aggiorna_elenco()
        self._rigenera_prospetto(data_consegna)

    def _riconsegna(self, consegna: dict):
        cognome = _DialogoRiconsegna(self, consegna["radio_identificativo"]).valore()
        if cognome is None:
            return

        cognome = risolvi_operatore_confermato(self, cognome)
        if cognome is None:
            return

        adesso = datetime.now()
        registra_riconsegna(
            consegna["id"], adesso.strftime("%H:%M"), cognome,
            data_riconsegna=adesso.strftime("%d-%m-%Y"),
        )
        self._aggiorna_elenco()


        self._rigenera_prospetto(consegna["data"])

    def _rigenera_prospetto(self, data_consegna: str):
        cartella = carica_impostazioni().get(CHIAVE_PROSPETTI_CONSEGNA_RADIO, "")
        if not cartella_esiste(cartella):
            QMessageBox.warning(
                self,
                "Cartella non configurata",
                "La modifica è stata salvata, ma non è stato possibile generare il prospetto Excel "
                "perché la cartella \"Consegna Radio\" non è configurata o non è "
                "raggiungibile. Configurala nelle Impostazioni.",
            )
            return

        anno, mese = mese_di_riferimento(data_consegna)
        try:
            genera_prospetto_mese(anno, mese, cartella)
        except OSError as errore:
            QMessageBox.warning(self, "Errore", f"Impossibile generare il prospetto Excel: {errore}")
