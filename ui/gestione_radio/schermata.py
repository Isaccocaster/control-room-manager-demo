"""Documentazione della versione portfolio."""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config.impostazioni import CHIAVE_PROSPETTI_GESTIONE_RADIO, cartella_esiste, carica_impostazioni
from data.gestione_radio import (
    STATI_AURICOLARE,
    STATI_RADIO,
    TIPI_APPARATO_RADIO,
    aggiungi_radio,
    cerca_radio,
    conteggi_per_stato,
    e_af_impianti,
    elenco_auricolari,
    eventi_radio,
    imposta_conteggio_auricolare,
    modifica_radio,
    periodi_eventi_radio,
    raggruppa_per_tipo,
    rimuovi_radio,
    stato_effettivo,
)
from documents.excel.prospetto_gestione_radio import genera_prospetto
from ui.comune.archivio_anno_mese import DialogoArchivioAnnoMese
from ui.comune.icone import SIMBOLO_STORICO, applica_icona_pulsante
from ui.comune.campo_operatore import applica_autocomplete_operatori
from ui.comune.riga_scorrevole import riga_scorrevole
from ui.gestione_radio.stile import FOGLIO_DI_STILE_GESTIONE_RADIO
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO


PERCORSO_FOTO_SFONDO = Path(__file__).parent.parent / "assets" / "images" / "demo_gestione_radio.jpg"

NOME_TUTTE = "Tutte"
NOME_AURICOLARI = "🎧 Auricolari"
NOME_MANUTENTORI = "🔧 Manutentori"

ETICHETTE_STATO = {
    "disponibile": "Disponibile",
    "assegnata": "Assegnata",
    "guasta": "Guasta",
    "in_riparazione": "In riparazione",
    "persa": "Persa/Smarrita",
}


ETICHETTE_CAMPO_EVENTO = {
    "creazione": "Creazione",
    "tipo_apparato": "Tipo apparato",
    "selettiva": "Selettiva",
    "matricola": "Matricola",
    "custodito_da": "Custodito da",
    "assegnata_a": "Assegnata a",
    "stato": "Stato",
    "note": "Note",
    "rimozione": "Rimozione",
}


SCELTE_STATO_DIALOGO = [
    ("Nessuna condizione particolare", "disponibile"),
    ("Guasta", "guasta"),
    ("In riparazione", "in_riparazione"),
    ("Persa/Smarrita", "persa"),
]


class _DialogoRadio(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, tipo_apparato="", selettiva="", matricola="",
                 custodito_da="", assegnata_a="", stato="disponibile", note=""):
        super().__init__(parent)
        self.setWindowTitle("Radio")
        self.setObjectName("dialogo_radio_gestione")
        self.setStyleSheet(FOGLIO_DI_STILE_GESTIONE_RADIO)

        layout = QFormLayout(self)


        self.campo_tipo = QComboBox()
        self.campo_tipo.setObjectName("campo_tipo_radio")
        self.campo_tipo.addItems(TIPI_APPARATO_RADIO)
        if tipo_apparato in TIPI_APPARATO_RADIO:
            self.campo_tipo.setCurrentText(tipo_apparato)
        layout.addRow("Tipo apparato:", self.campo_tipo)

        self.campo_selettiva = QLineEdit(selettiva or "")
        self.campo_selettiva.setObjectName("campo_selettiva_radio")
        self.campo_selettiva.setPlaceholderText("Vuota per apparati fissi (base/ripetitore)")
        layout.addRow("Selettiva:", self.campo_selettiva)

        self.campo_matricola = QLineEdit(matricola or "")
        self.campo_matricola.setObjectName("campo_matricola_radio")
        layout.addRow("Matricola:", self.campo_matricola)


        self.campo_custodito_da = QLineEdit(custodito_da or "")
        self.campo_custodito_da.setObjectName("campo_custodito_radio")
        applica_autocomplete_operatori(self.campo_custodito_da)
        layout.addRow("Custodito da:", self.campo_custodito_da)

        self.campo_assegnata_a = QLineEdit(assegnata_a or "")
        self.campo_assegnata_a.setObjectName("campo_assegnata_radio")
        applica_autocomplete_operatori(self.campo_assegnata_a)
        layout.addRow("Assegnata a:", self.campo_assegnata_a)

        self.campo_stato = QComboBox()
        self.campo_stato.setObjectName("campo_stato_radio")
        for etichetta, valore in SCELTE_STATO_DIALOGO:
            self.campo_stato.addItem(etichetta, valore)
        indice = next(
            (i for i, (_, valore) in enumerate(SCELTE_STATO_DIALOGO) if valore == stato), 0
        )
        self.campo_stato.setCurrentIndex(indice)
        layout.addRow("Stato:", self.campo_stato)

        self.campo_note = QLineEdit(note or "")
        self.campo_note.setObjectName("campo_note_radio")
        layout.addRow("Note:", self.campo_note)

        avviso = QLabel(
            "\"Assegnata a\"/\"Custodito da\" sono un dato anagrafico stabile (dotazione "
            "fissa), diverso dalla presa in consegna di turno registrata in Consegna Radio: "
            "i due non si aggiornano a vicenda. \"Disponibile\"/\"Assegnata\" non si scelgono "
            "qui: si ricavano da sole da \"Assegnata a\" — questo menu serve solo per le "
            "condizioni speciali."
        )
        avviso.setWordWrap(True)
        avviso.setObjectName("avviso_dialogo_radio")
        layout.addRow(avviso)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.setObjectName("azioni_dialogo_radio")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addRow(pulsanti)

    def valori(self):
        return (
            self.campo_tipo.currentText(),
            self.campo_selettiva.text().strip(),
            self.campo_matricola.text().strip(),
            self.campo_custodito_da.text().strip(),
            self.campo_assegnata_a.text().strip(),
            self.campo_stato.currentData(),
            self.campo_note.text().strip(),
        )


class _DialogoAuricolare(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, modello="", stato="funzionante", quantita=0, modello_bloccato=False):
        super().__init__(parent)
        self.setWindowTitle("Conteggio auricolari")
        self.setObjectName("dialogo_auricolare_gestione")
        self.setStyleSheet(FOGLIO_DI_STILE_GESTIONE_RADIO)

        layout = QFormLayout(self)

        self.campo_modello = QLineEdit(modello)
        self.campo_modello.setObjectName("campo_modello_auricolare")
        self.campo_modello.setPlaceholderText("Es. RADIO DEMO B, RADIO DEMO A...")
        self.campo_modello.setEnabled(not modello_bloccato)
        layout.addRow("Modello:", self.campo_modello)

        self.campo_stato = QComboBox()
        self.campo_stato.setObjectName("campo_stato_auricolare")
        for valore in STATI_AURICOLARE:
            self.campo_stato.addItem(valore.capitalize(), valore)
        self.campo_stato.setCurrentIndex(STATI_AURICOLARE.index(stato))
        self.campo_stato.setEnabled(not modello_bloccato)
        layout.addRow("Stato:", self.campo_stato)

        self.campo_quantita = QSpinBox()
        self.campo_quantita.setObjectName("campo_quantita_auricolare")
        self.campo_quantita.setRange(0, 1000)
        self.campo_quantita.setValue(quantita)
        layout.addRow("Quantità:", self.campo_quantita)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.setObjectName("azioni_dialogo_auricolare")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addRow(pulsanti)

    def valori(self):
        return self.campo_modello.text().strip(), self.campo_stato.currentData(), self.campo_quantita.value()


class SchermataGestioneRadio(PaginaConSfondo):
    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, HOME_OPACITA_VELO)
        self.setObjectName("gestione_radio_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_GESTIONE_RADIO)

        self._filtro_stato = None
        self._modo = "radio"

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(40, 16, 40, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_gestione_radio")

        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(32, 28, 32, 28)
        layout_pannello.setSpacing(14)

        titolo = QLabel("Gestione Radio")
        titolo.setObjectName("titolo_gestione_radio")
        layout_pannello.addWidget(titolo)

        self._etichetta_conteggi = QLabel()
        self._etichetta_conteggi.setWordWrap(True)
        self._etichetta_conteggi.setObjectName("sottotitolo_gestione_radio")
        layout_pannello.addWidget(self._etichetta_conteggi)

        layout_pannello.addWidget(self._crea_selettore_stato())

        contenitore_ricerca = QWidget()
        contenitore_ricerca.setObjectName("contenitore_azioni_gestione_radio")
        riga_ricerca = QHBoxLayout(contenitore_ricerca)
        riga_ricerca.setContentsMargins(0, 0, 0, 0)
        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setObjectName("ricerca_gestione_radio")
        self._campo_ricerca.setPlaceholderText("Cerca per selettiva, matricola, custodito da, assegnata a, note...")
        self._campo_ricerca.textChanged.connect(lambda _: self._aggiorna())
        riga_ricerca.addWidget(self._campo_ricerca, stretch=1)

        self._pulsante_aggiungi = QPushButton("+ Aggiungi radio")
        self._pulsante_aggiungi.setObjectName("aggiungi_radio")
        self._pulsante_aggiungi.clicked.connect(self._aggiungi_radio)
        riga_ricerca.addWidget(self._pulsante_aggiungi)

        pulsante_excel = QPushButton("Aggiorna file Excel")
        pulsante_excel.setObjectName("aggiorna_excel_gestione_radio")
        pulsante_excel.clicked.connect(self._rigenera_prospetto)
        riga_ricerca.addWidget(pulsante_excel)


        pulsante_storico = QPushButton("Storico")
        pulsante_storico.setObjectName("storico_gestione_radio")
        applica_icona_pulsante(pulsante_storico, SIMBOLO_STORICO)
        pulsante_storico.clicked.connect(self._apri_storico)
        riga_ricerca.addWidget(pulsante_storico)


        barra_azioni = riga_scorrevole(contenitore_ricerca)
        barra_azioni.setProperty("ruolo", "azioni_gestione_radio")
        layout_pannello.addWidget(barra_azioni)

        self._area_risultati = QScrollArea()
        self._area_risultati.setObjectName("elenco_gestione_radio")
        self._area_risultati.setWidgetResizable(True)
        self._area_risultati.setFrameShape(QFrame.NoFrame)

        self._contenitore_risultati = QWidget()
        self._contenitore_risultati.setObjectName("contenitore_gestione_radio")
        self._layout_risultati = QVBoxLayout(self._contenitore_risultati)
        self._layout_risultati.setContentsMargins(0, 0, 0, 0)
        self._layout_risultati.setSpacing(8)
        self._area_risultati.setWidget(self._contenitore_risultati)

        layout_pannello.addWidget(self._area_risultati, stretch=1)

        layout_esterno.addWidget(pannello, stretch=1)

        self._aggiorna()


    def _crea_selettore_stato(self) -> QScrollArea:
        contenitore = QWidget()
        contenitore.setObjectName("contenitore_filtri_gestione_radio")
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        gruppo = QButtonGroup(self)
        gruppo.setExclusive(True)
        self._gruppo_stati = gruppo

        nomi_pulsanti = (
            [NOME_TUTTE] + [ETICHETTE_STATO[s] for s in STATI_RADIO]
            + [NOME_MANUTENTORI, NOME_AURICOLARI]
        )
        for nome in nomi_pulsanti:
            pulsante = QPushButton(nome)
            pulsante.setObjectName("filtro_gestione_radio")
            pulsante.setCheckable(True)
            pulsante.clicked.connect(lambda _, n=nome: self._seleziona_filtro(n))
            gruppo.addButton(pulsante)
            layout.addWidget(pulsante)
            if nome == NOME_TUTTE:
                pulsante.setChecked(True)
        layout.addStretch()


        barra = riga_scorrevole(contenitore)
        barra.setProperty("ruolo", "filtri_gestione_radio")
        return barra

    def _seleziona_filtro(self, nome: str):
        if nome == NOME_AURICOLARI:
            self._modo = "auricolari"
        elif nome == NOME_MANUTENTORI:
            self._modo = "manutentori"
        else:
            self._modo = "radio"
            self._filtro_stato = None if nome == NOME_TUTTE else _stato_da_etichetta(nome)
        self._aggiorna()


    def _aggiorna(self):
        self._aggiorna_conteggi()
        self._svuota_risultati()

        if self._modo == "auricolari":
            self._mostra_auricolari_view()
            return
        if self._modo == "manutentori":
            self._mostra_manutentori_view()
            return

        risultati = cerca_radio(self._campo_ricerca.text(), stato=self._filtro_stato)
        if not risultati:
            self._mostra_messaggio("Nessun risultato.")
            return

        for tipo_apparato, radio in raggruppa_per_tipo(risultati):
            self._layout_risultati.addWidget(self._crea_intestazione_gruppo(tipo_apparato))
            for r in radio:
                self._layout_risultati.addWidget(self._crea_riga_radio(r))
        self._layout_risultati.addStretch()

    def _aggiorna_conteggi(self):
        per_stato = conteggi_per_stato()
        totale = sum(per_stato.values())
        parte_stati = "  ·  ".join(
            f"{ETICHETTE_STATO[s]}: {per_stato[s]}" for s in STATI_RADIO if per_stato[s]
        )

        gruppi = raggruppa_per_tipo(cerca_radio())


        parte_fissi = "  ·  ".join(
            f"{tipo}: {len(elenco)}" for tipo, elenco in gruppi if not any(r["selettiva"] for r in elenco)
        )
        parte_modelli = self._testo_funzionanti_guaste(gruppi)

        self._etichetta_conteggi.setText(
            f"Totale radio: {totale}   —   {parte_stati or 'nessuna'}\n"
            f"{parte_fissi}\n{parte_modelli}"
        )

    @staticmethod
    def _testo_funzionanti_guaste(gruppi: list[tuple[str, list[dict]]]) -> str:
        """Documentazione della versione portfolio."""
        parti = []
        for tipo, elenco in gruppi:
            if not any(r["selettiva"] for r in elenco):
                continue
            non_af = [r for r in elenco if not e_af_impianti(r)]
            funzionanti = sum(1 for r in non_af if stato_effettivo(r) in ("disponibile", "assegnata"))
            guaste = sum(1 for r in non_af if stato_effettivo(r) in ("guasta", "in_riparazione"))
            parti.append(f"{tipo} — Funzionanti: {funzionanti}, Guaste: {guaste}")
        return "  ·  ".join(parti)

    def _svuota_risultati(self):
        while self._layout_risultati.count():
            item = self._layout_risultati.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def _mostra_messaggio(self, testo: str):
        etichetta = QLabel(testo)
        etichetta.setObjectName("stato_vuoto_gestione_radio")
        self._layout_risultati.addWidget(etichetta)
        self._layout_risultati.addStretch()

    def _crea_intestazione_gruppo(self, tipo_apparato: str) -> QWidget:
        etichetta = QLabel(tipo_apparato)
        etichetta.setObjectName("sezione_gestione_radio")
        return etichetta


    def _crea_riga_radio(self, radio: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_gestione_radio")
        riga.setProperty("tipo", "radio")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()
        selettiva = f"Selettiva {radio['selettiva']}" if radio["selettiva"] else "Senza selettiva"
        intestazione = QLabel(
            f"{selettiva}   —   Matricola {radio['matricola'] or '—'}   —   "
            f"[{ETICHETTE_STATO[stato_effettivo(radio)]}]"
        )
        intestazione.setObjectName("identita_gestione_radio")
        intestazione.setWordWrap(True)
        layout_testo.addWidget(intestazione)

        parti = [f"Custodito da: {radio['custodito_da'] or '—'}"]
        if radio["assegnata_a"]:
            parti.append(f"Assegnata a: {radio['assegnata_a']}")
        dettaglio = QLabel("   —   ".join(parti))
        dettaglio.setObjectName("dettaglio_gestione_radio")
        dettaglio.setWordWrap(True)
        layout_testo.addWidget(dettaglio)

        if radio.get("note"):
            note = QLabel(radio["note"])
            note.setObjectName("note_gestione_radio")
            note.setWordWrap(True)
            layout_testo.addWidget(note)

        layout.addLayout(layout_testo, stretch=1)

        pulsante_modifica = QPushButton("Modifica")
        pulsante_modifica.setObjectName("modifica_gestione_radio")
        pulsante_modifica.clicked.connect(lambda: self._modifica_radio(radio))
        layout.addWidget(pulsante_modifica, alignment=Qt.AlignTop)

        pulsante_rimuovi = QPushButton("Rimuovi")
        pulsante_rimuovi.setObjectName("rimuovi_gestione_radio")
        pulsante_rimuovi.clicked.connect(lambda: self._rimuovi_radio(radio))
        layout.addWidget(pulsante_rimuovi, alignment=Qt.AlignTop)

        return riga


    def _mostra_manutentori_view(self):
        """Documentazione della versione portfolio."""
        tutte = cerca_radio(self._campo_ricerca.text())
        radio_af = [r for r in tutte if e_af_impianti(r)]
        radio_af.sort(key=lambda r: (r["tipo_apparato"], r["selettiva"] or ""))

        if not radio_af:
            self._mostra_messaggio("Nessuna radio in custodia ad DatoOperativoDemo611 al momento.")
            return

        for r in radio_af:
            self._layout_risultati.addWidget(self._crea_riga_manutentore(r))
        self._layout_risultati.addStretch()

    def _crea_riga_manutentore(self, radio: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_gestione_radio")
        riga.setProperty("tipo", "manutentore")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()
        selettiva = f"Selettiva {radio['selettiva']}" if radio["selettiva"] else "Senza selettiva"
        intestazione = QLabel(
            f"{radio['tipo_apparato']}   —   {selettiva}   —   Matricola {radio['matricola'] or '—'}"
            f"   —   [{ETICHETTE_STATO[stato_effettivo(radio)]}]"
        )
        intestazione.setObjectName("identita_gestione_radio")
        intestazione.setWordWrap(True)
        layout_testo.addWidget(intestazione)

        parti = [f"Custodito da: {radio['custodito_da'] or '—'}"]
        if radio["assegnata_a"]:
            parti.append(f"Assegnata a: {radio['assegnata_a']}")
        dettaglio = QLabel("   —   ".join(parti))
        dettaglio.setObjectName("dettaglio_gestione_radio")
        dettaglio.setWordWrap(True)
        layout_testo.addWidget(dettaglio)

        if radio.get("note"):
            note = QLabel(radio["note"])
            note.setObjectName("note_gestione_radio")
            note.setWordWrap(True)
            layout_testo.addWidget(note)

        layout.addLayout(layout_testo, stretch=1)

        pulsante_modifica = QPushButton("Modifica")
        pulsante_modifica.setObjectName("modifica_gestione_radio")
        pulsante_modifica.clicked.connect(lambda: self._modifica_radio(radio))
        layout.addWidget(pulsante_modifica, alignment=Qt.AlignTop)

        return riga


    def _mostra_auricolari_view(self):
        conteggi = elenco_auricolari()

        barra = QHBoxLayout()
        barra.addStretch()
        pulsante_nuovo = QPushButton("+ Nuovo modello")
        pulsante_nuovo.setObjectName("nuovo_auricolare_gestione")
        pulsante_nuovo.clicked.connect(self._nuovo_conteggio_auricolare)
        barra.addWidget(pulsante_nuovo)
        contenitore_barra = QWidget()
        contenitore_barra.setObjectName("barra_auricolari_gestione")
        contenitore_barra.setLayout(barra)
        self._layout_risultati.addWidget(contenitore_barra)

        if not conteggi:
            self._mostra_messaggio("Nessun conteggio auricolari registrato.")
            return

        for voce in conteggi:
            self._layout_risultati.addWidget(self._crea_riga_auricolare(voce))
        self._layout_risultati.addStretch()

    def _crea_riga_auricolare(self, voce: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_gestione_radio")
        riga.setProperty("tipo", "auricolare")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        etichetta = QLabel(f"{voce['modello']} — {voce['stato'].capitalize()}: {voce['quantita']}")
        etichetta.setObjectName("identita_gestione_radio")
        etichetta.setWordWrap(True)
        layout.addWidget(etichetta, stretch=1)

        pulsante = QPushButton("Modifica quantità")
        pulsante.setObjectName("modifica_gestione_radio")
        pulsante.clicked.connect(lambda: self._modifica_conteggio_auricolare(voce))
        layout.addWidget(pulsante)

        return riga

    def _nuovo_conteggio_auricolare(self):
        finestra = _DialogoAuricolare(self)
        if finestra.exec() != QDialog.Accepted:
            return
        modello, stato, quantita = finestra.valori()
        if not modello:
            QMessageBox.warning(self, "Dati mancanti", "Il modello è obbligatorio.")
            return
        imposta_conteggio_auricolare(modello, stato, quantita)
        self._aggiorna()
        self._rigenera_prospetto()

    def _modifica_conteggio_auricolare(self, voce: dict):
        finestra = _DialogoAuricolare(
            self, modello=voce["modello"], stato=voce["stato"], quantita=voce["quantita"],
            modello_bloccato=True,
        )
        if finestra.exec() != QDialog.Accepted:
            return
        _, _, quantita = finestra.valori()
        imposta_conteggio_auricolare(voce["modello"], voce["stato"], quantita)
        self._aggiorna()
        self._rigenera_prospetto()


    def _conferma(self, messaggio: str) -> bool:
        risposta = QMessageBox.question(
            self,
            "Confermi la modifica?",
            f"{messaggio}\n\nIl prospetto Excel dell'inventario verrà aggiornato di conseguenza.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return risposta == QMessageBox.Yes

    def _aggiungi_radio(self):
        finestra = _DialogoRadio(self)
        if finestra.exec() != QDialog.Accepted:
            return
        tipo, selettiva, matricola, custodito_da, assegnata_a, stato, note = finestra.valori()
        if not tipo:
            QMessageBox.warning(self, "Dati mancanti", "Il tipo apparato è obbligatorio.")
            return
        if not self._conferma(f'Aggiungere la radio "{tipo}"?'):
            return
        aggiungi_radio(tipo, selettiva, matricola, custodito_da, assegnata_a, stato, note)
        self._aggiorna()
        self._rigenera_prospetto()

    def _modifica_radio(self, radio: dict):
        finestra = _DialogoRadio(
            self, tipo_apparato=radio["tipo_apparato"], selettiva=radio["selettiva"] or "",
            matricola=radio["matricola"] or "", custodito_da=radio["custodito_da"] or "",
            assegnata_a=radio["assegnata_a"] or "", stato=radio["stato"], note=radio["note"] or "",
        )
        if finestra.exec() != QDialog.Accepted:
            return
        tipo, selettiva, matricola, custodito_da, assegnata_a, stato, note = finestra.valori()
        if not tipo:
            QMessageBox.warning(self, "Dati mancanti", "Il tipo apparato è obbligatorio.")
            return
        if not self._conferma(f'Modificare la radio "{tipo}" (matricola {radio["matricola"] or "—"})?'):
            return
        modifica_radio(radio["id"], tipo, selettiva, matricola, custodito_da, assegnata_a, stato, note)
        self._aggiorna()
        self._rigenera_prospetto()

    def _rimuovi_radio(self, radio: dict):
        if self._conferma(f'Rimuovere la radio "{radio["tipo_apparato"]}" '
                          f'(matricola {radio["matricola"] or "—"})?'):
            rimuovi_radio(radio["id"])
            self._aggiorna()
            self._rigenera_prospetto()


    def _apri_storico(self):
        self._crea_dialogo_storico().exec()

    def _crea_dialogo_storico(self) -> DialogoArchivioAnnoMese:
        dialogo = DialogoArchivioAnnoMese(
            self, "Storico Gestione Radio",
            colonne=[
                ("DATA", "data"), ("ORA", "ora"), ("CAMPO", "campo_etichetta"),
                ("RADIO", "radio_etichetta"), ("MODIFICA", "modifica_testo"),
            ],
            periodi=periodi_eventi_radio,
            carica_mese=lambda anno, mese, testo: [
                self._evento_da_evento_radio(e)
                for e in eventi_radio(testo_ricerca=testo, anno=anno, mese=mese)
            ],
            dettaglio=self._dettaglio_evento_radio,
        )
        dialogo.setObjectName("storico_gestione_radio_modern_control_room")
        dialogo.setStyleSheet(FOGLIO_DI_STILE_GESTIONE_RADIO)
        return dialogo

    @staticmethod
    def _evento_da_evento_radio(e: dict) -> dict:
        radio_etichetta = e["tipo_apparato"] or "[radio non più in anagrafica]"
        if e["selettiva"]:
            radio_etichetta += f" — selettiva {e['selettiva']}"

        def testo_valore(valore):
            if valore is None:
                return None
            return ETICHETTE_STATO.get(valore, valore) if e["campo"] == "stato" else valore

        vp = testo_valore(e["valore_precedente"])
        vn = testo_valore(e["valore_nuovo"])
        if e["campo"] == "creazione":
            modifica = vn or ""
        elif e["campo"] == "rimozione":
            modifica = vp or ""
        else:
            modifica = f"{vp or '—'} → {vn or '—'}"

        return {
            "data": e["data"], "ora": e["ora"],
            "campo_etichetta": ETICHETTE_CAMPO_EVENTO.get(e["campo"], e["campo"]),
            "radio_etichetta": radio_etichetta,
            "modifica_testo": modifica,
            "valore_precedente": vp, "valore_nuovo": vn,
        }

    @staticmethod
    def _dettaglio_evento_radio(evento: dict):
        return f"{evento['campo_etichetta']} — {evento['radio_etichetta']}", [
            ("Data", evento["data"]), ("Ora", evento["ora"]),
            ("Campo", evento["campo_etichetta"]), ("Radio", evento["radio_etichetta"]),
            ("Valore precedente", evento["valore_precedente"]),
            ("Valore nuovo", evento["valore_nuovo"]),
        ]


    def _rigenera_prospetto(self):
        cartella = carica_impostazioni().get(CHIAVE_PROSPETTI_GESTIONE_RADIO, "")
        if not cartella_esiste(cartella):
            QMessageBox.warning(
                self,
                "Cartella non configurata",
                "La modifica è stata salvata, ma non è stato possibile generare il prospetto Excel "
                "perché la cartella \"Prospetto Radio\" non è configurata o non è raggiungibile. "
                "Configurala nelle Impostazioni.",
            )
            return
        try:
            genera_prospetto(cartella)
        except OSError as errore:
            QMessageBox.warning(self, "Errore", f"Impossibile generare il prospetto Excel: {errore}")


def _stato_da_etichetta(etichetta: str) -> str:
    for valore, testo in ETICHETTE_STATO.items():
        if testo == etichetta:
            return valore
    raise ValueError(etichetta)
