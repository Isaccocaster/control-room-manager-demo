"""Documentazione della versione portfolio."""
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
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

from config.impostazioni import CHIAVE_OGGETTI_SMARRITI, cartella_esiste, carica_impostazioni
from data.oggetti_smarriti import (
    periodi_storico,
    storico_eventi,
    STATO_IN_CUSTODIA,
    STATO_RICONSEGNATO,
    STATO_SMALTITO,
    elimina_oggetto,
    giorni_trascorsi,
    oggetti_per_stato,
    registra_oggetto,
    registra_riconsegna,
    registra_smaltimento,
)
from documents.excel.prospetto_oggetti_smarriti import NOMI_FILE, genera_prospetti
from ui.oggetti_smarriti.stile import FOGLIO_DI_STILE_OGGETTI
from ui.comune.archivio_anno_mese import DialogoArchivioAnnoMese
from ui.comune.campo_operatore import applica_autocomplete_operatori, risolvi_operatore_confermato
from ui.comune.icone import SIMBOLO_STORICO, applica_icona_pulsante
from ui.comune.riga_scorrevole import riga_scorrevole
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO

PERCORSO_FOTO_SFONDO = Path(__file__).parent.parent / "assets" / "images" / "demo_oggetti_smarriti.jpg"

ETICHETTE_VISTE = [
    (STATO_IN_CUSTODIA, "In custodia"),
    (STATO_RICONSEGNATO, "Oggetti Riconsegnati"),
    (STATO_SMALTITO, "Oggetti Smaltiti"),
]


def _cartella_configurata() -> str:
    percorso = carica_impostazioni().get(CHIAVE_OGGETTI_SMARRITI, "")
    return percorso if cartella_esiste(percorso) else ""


def _avviso_file_excel(stati) -> str:
    """Documentazione della versione portfolio."""
    if not _cartella_configurata():
        return (
            "⚠ La cartella \"Oggetti Smarriti\" non è configurata o non è raggiungibile.\n"
            "L'operazione verrà salvata nel database, ma nessun file Excel verrà aggiornato.\n"
            "Puoi configurare la cartella nelle Impostazioni."
        )
    elenco = "\n".join(f"    • {NOMI_FILE[stato]}" for stato in stati)
    return f"Verranno aggiornati e sovrascritti:\n{elenco}"


class _DialogoConAvvisoExcel(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, titolo: str, descrizione_operazione: str, stati_coinvolti):
        super().__init__(parent)
        self.setObjectName("dialogo_operazione_oggetti")
        self.setStyleSheet(FOGLIO_DI_STILE_OGGETTI)
        self.setWindowTitle(titolo)
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)

        intestazione = QLabel(descrizione_operazione)
        intestazione.setObjectName("intestazione_operazione_oggetti")
        intestazione.setWordWrap(True)
        layout.addWidget(intestazione)

        self._modulo = QFormLayout()
        layout.addLayout(self._modulo)

        avviso = QLabel(_avviso_file_excel(stati_coinvolti))
        avviso.setObjectName("avviso_excel_oggetti")
        avviso.setWordWrap(True)
        layout.addWidget(avviso)

        pulsanti = QDialogButtonBox()
        conferma = pulsanti.addButton("Conferma", QDialogButtonBox.AcceptRole)
        conferma.setObjectName("conferma_operazione_oggetti")
        annulla = pulsanti.addButton("Annulla", QDialogButtonBox.RejectRole)
        annulla.setObjectName("annulla_operazione_oggetti")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def aggiungi_campo(self, etichetta: str, segnaposto: str = "") -> QLineEdit:
        campo = QLineEdit()
        campo.setObjectName("campo_operazione_oggetti")
        if segnaposto:
            campo.setPlaceholderText(segnaposto)
        self._modulo.addRow(etichetta, campo)
        return campo


class SchermataOggettiSmarriti(PaginaConSfondo):
    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, HOME_OPACITA_VELO)
        self.setObjectName("oggetti_smarriti_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_OGGETTI)

        self._vista = STATO_IN_CUSTODIA

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(40, 16, 40, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_oggetti_smarriti")

        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(32, 28, 32, 28)
        layout_pannello.setSpacing(14)

        titolo = QLabel("Oggetti Smarriti")
        titolo.setObjectName("titolo_oggetti_smarriti")
        layout_pannello.addWidget(titolo)

        sottotitolo = QLabel("Presa in custodia, riconsegna e smaltimento con tracciabilità completa")
        sottotitolo.setObjectName("sottotitolo_oggetti_smarriti")
        sottotitolo.setWordWrap(True)
        layout_pannello.addWidget(sottotitolo)

        layout_pannello.addWidget(self._crea_selettore_vista())
        layout_pannello.addWidget(self._crea_barra_azioni())

        self._area_risultati = QScrollArea()
        self._area_risultati.setObjectName("elenco_oggetti_smarriti")
        self._area_risultati.setWidgetResizable(True)
        self._area_risultati.setFrameShape(QFrame.NoFrame)

        self._contenitore_righe = QWidget()
        self._contenitore_righe.setObjectName("contenitore_oggetti_smarriti")
        self._layout_righe = QVBoxLayout(self._contenitore_righe)
        self._layout_righe.setContentsMargins(0, 0, 0, 0)
        self._layout_righe.setSpacing(8)
        self._area_risultati.setWidget(self._contenitore_righe)

        layout_pannello.addWidget(self._area_risultati, stretch=1)

        layout_esterno.addWidget(pannello, stretch=1)

        self._aggiorna_elenco()

    def _apri_storico(self):
        self._crea_dialogo_storico().exec()

    def _crea_dialogo_storico(self) -> DialogoArchivioAnnoMese:
        dialogo = DialogoArchivioAnnoMese(
            self, "Storico Oggetti Smarriti",
            colonne=[
                ("DATA", "data"), ("ORA", "ora"), ("OPERAZIONE", "operazione"),
                ("OGGETTO", "elemento"), ("OPERATORE", "persona"), ("DETTAGLI", "dettagli"),
            ],
            periodi=periodi_storico,
            carica_mese=lambda anno, mese, testo: storico_eventi(
                testo_ricerca=testo, anno=anno, mese=mese,
            ),
            dettaglio=self._dettaglio_evento,
        )
        dialogo.setObjectName("storico_oggetti_modern_control_room")
        dialogo.setStyleSheet(FOGLIO_DI_STILE_OGGETTI)
        return dialogo


    def _crea_selettore_vista(self) -> QScrollArea:
        contenitore = QWidget()
        contenitore.setObjectName("contenitore_viste_oggetti")
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        gruppo = QButtonGroup(self)
        gruppo.setExclusive(True)
        self._gruppo_viste = gruppo

        for stato, etichetta in ETICHETTE_VISTE:
            pulsante = QPushButton(etichetta)
            pulsante.setObjectName("filtro_stato_oggetti")
            pulsante.setCheckable(True)
            pulsante.setChecked(stato == self._vista)
            pulsante.clicked.connect(lambda _, s=stato: self._cambia_vista(s))
            gruppo.addButton(pulsante)
            layout.addWidget(pulsante)

        layout.addStretch()

        area = riga_scorrevole(contenitore)
        area.setProperty("ruolo", "viste_oggetti")
        return area

    def _crea_barra_azioni(self) -> QScrollArea:
        contenitore = QWidget()
        contenitore.setObjectName("contenitore_azioni_oggetti")
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setObjectName("ricerca_oggetti_smarriti")
        self._campo_ricerca.setPlaceholderText("Cerca per oggetto, proprietario, sigillo...")
        self._campo_ricerca.textChanged.connect(lambda _: self._aggiorna_elenco())
        layout.addWidget(self._campo_ricerca, stretch=1)

        pulsante_nuovo = QPushButton("+ Nuovo oggetto")
        pulsante_nuovo.setObjectName("nuovo_oggetto_smarrito")
        pulsante_nuovo.clicked.connect(self._nuovo_oggetto)
        layout.addWidget(pulsante_nuovo)

        pulsante_excel = QPushButton("Aggiorna file Excel")
        pulsante_excel.setObjectName("aggiorna_excel_oggetti")
        pulsante_excel.clicked.connect(self._aggiorna_file_excel)
        layout.addWidget(pulsante_excel)


        pulsante_storico = QPushButton("Storico")
        pulsante_storico.setObjectName("storico_oggetti_smarriti")
        applica_icona_pulsante(pulsante_storico, SIMBOLO_STORICO)
        pulsante_storico.clicked.connect(self._apri_storico)
        layout.addWidget(pulsante_storico)


        area = riga_scorrevole(contenitore)
        area.setProperty("ruolo", "azioni_oggetti")
        return area


    def _cambia_vista(self, stato: str):
        self._vista = stato
        self._aggiorna_elenco()

    def _svuota_elenco(self):
        while self._layout_righe.count():
            item = self._layout_righe.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    @staticmethod
    def _dettaglio_evento(evento: dict):
        return f"{evento['operazione']} — {evento['elemento']}", [
            ("Data", evento["data"]), ("Ora", evento["ora"]),
            ("Operazione", evento["operazione"]), ("Oggetto", evento["elemento"]),
            ("Operatore", evento["persona"]), ("Dettagli", evento["dettagli"]),
            ("Note", evento.get("note")),
        ]

    def _aggiorna_elenco(self):
        self._svuota_elenco()

        oggetti = oggetti_per_stato(self._vista, self._campo_ricerca.text())
        if not oggetti:
            etichetta = QLabel("Nessun oggetto da mostrare.")
            etichetta.setObjectName("stato_vuoto_oggetti")
            self._layout_righe.addWidget(etichetta)
        else:
            for oggetto in oggetti:
                self._layout_righe.addWidget(self._crea_riga(oggetto))

        self._layout_righe.addStretch()

    def _crea_riga(self, oggetto: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_oggetto_smarrito")
        layout_esterno = QHBoxLayout(riga)
        layout_esterno.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()

        descrizione = QLabel(oggetto["descrizione"])
        descrizione.setObjectName("descrizione_oggetto_smarrito")
        descrizione.setWordWrap(True)
        layout_testo.addWidget(descrizione)

        dettaglio = QLabel(self._testo_dettaglio(oggetto))
        dettaglio.setObjectName("dettaglio_oggetto_smarrito")
        dettaglio.setWordWrap(True)
        layout_testo.addWidget(dettaglio)

        if oggetto.get("note_import"):
            anomalia = QLabel(f"⚠ {oggetto['note_import']}")
            anomalia.setObjectName("anomalia_oggetto_smarrito")
            anomalia.setWordWrap(True)
            layout_testo.addWidget(anomalia)

        layout_esterno.addLayout(layout_testo, stretch=1)

        for pulsante in self._crea_pulsanti_riga(oggetto):
            layout_esterno.addWidget(pulsante, alignment=Qt.AlignTop)

        return riga

    def _testo_dettaglio(self, oggetto: dict) -> str:
        sigillo = oggetto["numero_sigillo"] or "Senza sigillo"
        parti = [f"Ritirato il {oggetto['data_ritiro']}", f"Sigillo: {sigillo}"]

        if oggetto["proprietario"]:
            parti.append(f"Proprietario: {oggetto['proprietario']}")
        if oggetto["ubicazione"]:
            parti.append(f"Ubicazione: {oggetto['ubicazione']}")

        if self._vista == STATO_IN_CUSTODIA:
            giorni = giorni_trascorsi(oggetto["data_ritiro"])
            if giorni is not None:
                parti.append(f"In custodia da {giorni} giorni")
        elif self._vista == STATO_RICONSEGNATO:
            parti.append(f"Riconsegnato il {oggetto['data_riconsegna']} {oggetto['ora_riconsegna'] or ''}".strip())
            if oggetto["riconsegnato_a"]:
                parti.append(f"A: {oggetto['riconsegnato_a']}")
            if oggetto["operatore_riconsegna"]:
                parti.append(f"Operatore: {oggetto['operatore_riconsegna']}")
            giorni = giorni_trascorsi(oggetto["data_riconsegna"])
            if giorni is not None:
                parti.append(f"Riconsegnato da {giorni} giorni")
            if oggetto["note_riconsegna"]:
                parti.append(oggetto["note_riconsegna"])
        else:
            parti.append(f"Smaltito il {oggetto['data_smaltimento']} {oggetto['ora_smaltimento'] or ''}".strip())
            if oggetto["operatore_smaltimento"]:
                parti.append(f"Operatore: {oggetto['operatore_smaltimento']}")
            if oggetto["note_smaltimento"]:
                parti.append(oggetto["note_smaltimento"])

        return "   —   ".join(parti)

    def _crea_pulsanti_riga(self, oggetto: dict) -> list:
        if self._vista == STATO_IN_CUSTODIA:
            riconsegna = QPushButton("Riconsegna")
            riconsegna.setObjectName("riconsegna_oggetto")
            riconsegna.clicked.connect(lambda: self._riconsegna(oggetto))
            smaltisci = QPushButton("Smaltisci")
            smaltisci.setObjectName("smaltisci_oggetto")
            smaltisci.clicked.connect(lambda: self._smaltisci(oggetto))
            return [riconsegna, smaltisci]

        if self._vista == STATO_RICONSEGNATO:
            elimina = QPushButton("Elimina")
            elimina.setObjectName("elimina_oggetto")
            elimina.clicked.connect(lambda: self._elimina(oggetto))
            return [elimina]


        return []


    def _nuovo_oggetto(self):
        finestra = _DialogoConAvvisoExcel(
            self, "Nuovo oggetto smarrito",
            "Stai per prendere in consegna un nuovo oggetto.",
            [STATO_IN_CUSTODIA],
        )
        campo_descrizione = finestra.aggiungi_campo("Oggetto:", "Es. Portafoglio in pelle blu")
        campo_sigillo = finestra.aggiungi_campo("Nr. sigillo:", "Facoltativo")
        campo_proprietario = finestra.aggiungi_campo("Proprietario:", "Facoltativo")
        campo_ubicazione = finestra.aggiungi_campo("Ubicazione:", "Facoltativo")
        campo_operatore = finestra.aggiungi_campo("Operatore:", "Chi prende in consegna")
        applica_autocomplete_operatori(campo_operatore)

        if finestra.exec() != QDialog.Accepted:
            return

        descrizione = campo_descrizione.text().strip()
        if not descrizione:
            QMessageBox.warning(self, "Dati mancanti", "La descrizione dell'oggetto è obbligatoria.")
            return

        operatore_ritiro = risolvi_operatore_confermato(self, campo_operatore.text())
        if operatore_ritiro is None:
            return

        adesso = datetime.now()
        registra_oggetto(
            data_ritiro=adesso.strftime("%d-%m-%Y"),
            descrizione=descrizione,
            ora_ritiro=adesso.strftime("%H:%M"),
            operatore_ritiro=operatore_ritiro,
            numero_sigillo=campo_sigillo.text(),
            proprietario=campo_proprietario.text(),
            ubicazione=campo_ubicazione.text(),
        )
        self._cambia_vista(STATO_IN_CUSTODIA)
        self._rigenera_excel([STATO_IN_CUSTODIA])

    def _riconsegna(self, oggetto: dict):
        finestra = _DialogoConAvvisoExcel(
            self, "Riconsegna oggetto",
            f"Stai per registrare la riconsegna di:\n«{oggetto['descrizione']}»",
            [STATO_IN_CUSTODIA, STATO_RICONSEGNATO],
        )
        campo_a_chi = finestra.aggiungi_campo("Riconsegnato a:", "Nome di chi ritira")
        campo_operatore = finestra.aggiungi_campo("Operatore:", "Chi effettua la riconsegna")
        applica_autocomplete_operatori(campo_operatore)
        campo_note = finestra.aggiungi_campo("Note:", "Facoltative")

        if finestra.exec() != QDialog.Accepted:
            return

        operatore_riconsegna = risolvi_operatore_confermato(self, campo_operatore.text())
        if operatore_riconsegna is None:
            return

        adesso = datetime.now()
        registra_riconsegna(
            oggetto["id"],
            data_riconsegna=adesso.strftime("%d-%m-%Y"),
            ora_riconsegna=adesso.strftime("%H:%M"),
            riconsegnato_a=campo_a_chi.text(),
            operatore_riconsegna=operatore_riconsegna,
            note_riconsegna=campo_note.text(),
        )
        self._aggiorna_elenco()
        self._rigenera_excel([STATO_IN_CUSTODIA, STATO_RICONSEGNATO])

    def _smaltisci(self, oggetto: dict):
        finestra = _DialogoConAvvisoExcel(
            self, "Smaltimento oggetto",
            f"Stai per smaltire:\n«{oggetto['descrizione']}»\n"
            "L'oggetto non comparirà più tra quelli in custodia.",
            [STATO_IN_CUSTODIA, STATO_SMALTITO],
        )
        campo_operatore = finestra.aggiungi_campo("Operatore:", "Chi dispone lo smaltimento")
        applica_autocomplete_operatori(campo_operatore)
        campo_note = finestra.aggiungi_campo("Motivo/note:", "Es. in custodia da 8 mesi, mai reclamato")

        if finestra.exec() != QDialog.Accepted:
            return

        operatore_smaltimento = risolvi_operatore_confermato(self, campo_operatore.text())
        if operatore_smaltimento is None:
            return

        adesso = datetime.now()
        registra_smaltimento(
            oggetto["id"],
            data_smaltimento=adesso.strftime("%d-%m-%Y"),
            ora_smaltimento=adesso.strftime("%H:%M"),
            operatore_smaltimento=operatore_smaltimento,
            note_smaltimento=campo_note.text(),
        )
        self._aggiorna_elenco()
        self._rigenera_excel([STATO_IN_CUSTODIA, STATO_SMALTITO])

    def _elimina(self, oggetto: dict):
        risposta = QMessageBox.question(
            self, "Eliminare questo oggetto?",
            f"Stai per eliminare definitivamente dall'elenco dei riconsegnati:\n"
            f"«{oggetto['descrizione']}»\n\n"
            f"{_avviso_file_excel([STATO_RICONSEGNATO])}",
        )
        if risposta != QMessageBox.Yes:
            return

        elimina_oggetto(oggetto["id"])
        self._aggiorna_elenco()
        self._rigenera_excel([STATO_RICONSEGNATO])

    def _aggiorna_file_excel(self):
        risposta = QMessageBox.question(
            self, "Aggiornare i file Excel?",
            "Stai per rigenerare i file Excel degli Oggetti Smarriti.\n\n"
            f"{_avviso_file_excel([STATO_IN_CUSTODIA, STATO_RICONSEGNATO, STATO_SMALTITO])}",
        )
        if risposta != QMessageBox.Yes:
            return

        if not _cartella_configurata():
            QMessageBox.warning(
                self, "Cartella non configurata",
                "La cartella \"Oggetti Smarriti\" non è configurata o non è raggiungibile. "
                "Configurala nelle Impostazioni.",
            )
            return

        if self._rigenera_excel([STATO_IN_CUSTODIA, STATO_RICONSEGNATO, STATO_SMALTITO]):
            QMessageBox.information(self, "File aggiornati", "I tre file Excel sono stati aggiornati.")

    def _rigenera_excel(self, stati) -> bool:
        """Documentazione della versione portfolio."""
        cartella = _cartella_configurata()
        if not cartella:
            return False

        try:
            genera_prospetti(stati, cartella)
        except OSError as errore:
            QMessageBox.warning(
                self, "File Excel non aggiornati",
                "La modifica è stata salvata nel database, ma non è stato possibile "
                f"aggiornare i file Excel: {errore}\n\n"
                "Puoi riprovare con il pulsante \"Aggiorna file Excel\".",
            )
            return False
        return True
