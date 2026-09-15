"""Documentazione della versione portfolio."""
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
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

from config.impostazioni import CHIAVE_CASSAFORTE, cartella_esiste, carica_impostazioni
from data.cassaforte import (
    CATEGORIE,
    ETICHETTE_CATEGORIE,
    aggiungi_elemento,
    cicli_cassaforte,
    data_valida,
    elenco_elementi,
    giorni_trascorsi,
    movimenti,
    movimenti_senza_data,
    periodi_storico_cassaforte,
    registra_deposito,
    registra_rientro,
    registra_uscita,
)
from documents.excel.prospetto_cassaforte import NOME_FILE, genera_prospetto
from ui.cassaforte.stile import FOGLIO_DI_STILE_CASSAFORTE
from ui.comune.archivio_anno_mese import DialogoArchivioAnnoMese
from ui.comune.campo_operatore import applica_autocomplete_operatori, risolvi_operatore_confermato
from ui.comune.icone import SIMBOLO_STORICO, applica_icona_pulsante
from ui.comune.riga_scorrevole import riga_scorrevole
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO

PERCORSO_FOTO_SFONDO = Path(__file__).parent.parent / "assets" / "images" / "demo_cassaforte.jpg"

_ETICHETTE_TIPO = {"deposito": "Deposito", "uscita": "Uscita", "rientro": "Rientro"}


def _cartella_configurata() -> str:
    percorso = carica_impostazioni().get(CHIAVE_CASSAFORTE, "")
    return percorso if cartella_esiste(percorso) else ""


def _avviso_file_excel() -> str:
    if not _cartella_configurata():
        return (
            "⚠ La cartella \"Cassaforte\" non è configurata o non è raggiungibile.\n"
            "L'operazione verrà salvata nel database, ma il file Excel non verrà aggiornato.\n"
            "Puoi configurare la cartella nelle Impostazioni."
        )
    return f"Verrà aggiornato e sovrascritto:\n    • {NOME_FILE}"


class _DialogoOperazione(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, titolo: str, descrizione: str):
        super().__init__(parent)
        self.setObjectName("dialogo_operazione_cassaforte")
        self.setStyleSheet(FOGLIO_DI_STILE_CASSAFORTE)
        self.setWindowTitle(titolo)
        self.setMinimumWidth(520)

        self._layout = QVBoxLayout(self)

        intestazione = QLabel(descrizione)
        intestazione.setObjectName("intestazione_operazione_cassaforte")
        intestazione.setWordWrap(True)
        self._layout.addWidget(intestazione)

        self._modulo = QFormLayout()
        self._layout.addLayout(self._modulo)

    def aggiungi_campo(self, etichetta: str, segnaposto: str = "") -> QLineEdit:
        campo = QLineEdit()
        campo.setObjectName("campo_operazione_cassaforte")
        if segnaposto:
            campo.setPlaceholderText(segnaposto)
        self._modulo.addRow(etichetta, campo)
        return campo

    def aggiungi_categorie(self) -> QComboBox:
        campo = QComboBox()
        campo.setObjectName("categoria_operazione_cassaforte")
        for categoria in CATEGORIE:
            campo.addItem(ETICHETTE_CATEGORIE[categoria], categoria)
        self._modulo.addRow("Categoria:", campo)
        return campo

    def aggiungi_widget(self, widget: QWidget):
        self._layout.addWidget(widget)

    def chiudi_con_avviso(self):
        """Documentazione della versione portfolio."""
        avviso = QLabel(_avviso_file_excel())
        avviso.setObjectName("avviso_excel_cassaforte")
        avviso.setWordWrap(True)
        self._layout.addWidget(avviso)

        pulsanti = QDialogButtonBox()
        conferma = pulsanti.addButton("Conferma", QDialogButtonBox.AcceptRole)
        conferma.setObjectName("conferma_operazione_cassaforte")
        annulla = pulsanti.addButton("Annulla", QDialogButtonBox.RejectRole)
        annulla.setObjectName("annulla_operazione_cassaforte")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        self._layout.addWidget(pulsanti)


class SchermataCassaforte(PaginaConSfondo):
    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, HOME_OPACITA_VELO)
        self.setObjectName("cassaforte_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_CASSAFORTE)

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(40, 16, 40, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_cassaforte")

        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(32, 28, 32, 28)
        layout_pannello.setSpacing(14)

        titolo = QLabel("Cassaforte")
        titolo.setObjectName("titolo_cassaforte")
        layout_pannello.addWidget(titolo)

        sottotitolo = QLabel("Custodia controllata di buste, chiavi ed elementi ad accesso diretto")
        sottotitolo.setObjectName("sottotitolo_cassaforte")
        sottotitolo.setWordWrap(True)
        layout_pannello.addWidget(sottotitolo)

        layout_pannello.addWidget(self._crea_barra_azioni())

        self._area = QScrollArea()
        self._area.setObjectName("elenco_cassaforte")
        self._area.setWidgetResizable(True)
        self._area.setFrameShape(QFrame.NoFrame)

        self._contenitore = QWidget()
        self._contenitore.setObjectName("contenitore_cassaforte")
        self._layout_righe = QVBoxLayout(self._contenitore)
        self._layout_righe.setContentsMargins(0, 0, 0, 0)
        self._layout_righe.setSpacing(8)
        self._area.setWidget(self._contenitore)

        layout_pannello.addWidget(self._area, stretch=1)
        layout_esterno.addWidget(pannello, stretch=1)

        self._aggiorna()


    def _crea_barra_azioni(self) -> QScrollArea:
        contenitore = QWidget()
        contenitore.setObjectName("contenitore_azioni_cassaforte")
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setObjectName("ricerca_cassaforte")
        self._campo_ricerca.setPlaceholderText("Cerca per elemento, persona, numero di busta...")
        self._campo_ricerca.textChanged.connect(lambda _: self._aggiorna())
        layout.addWidget(self._campo_ricerca, stretch=1)

        for etichetta, nome, azione in [
            ("+ Nuova uscita", "nuova_uscita_cassaforte", self._nuova_uscita),
            ("+ Nuovo elemento", "nuovo_elemento_cassaforte", self._nuovo_elemento),
            ("Aggiorna file Excel", "aggiorna_excel_cassaforte", self._aggiorna_file_excel),
        ]:
            pulsante = QPushButton(etichetta)
            pulsante.setObjectName(nome)
            pulsante.clicked.connect(azione)
            layout.addWidget(pulsante)


        pulsante_storico = QPushButton("Storico")
        pulsante_storico.setObjectName("storico_cassaforte")
        applica_icona_pulsante(pulsante_storico, SIMBOLO_STORICO)
        pulsante_storico.clicked.connect(self._apri_storico)
        layout.addWidget(pulsante_storico)


        area = riga_scorrevole(contenitore)
        area.setProperty("ruolo", "azioni_cassaforte")
        return area

    def _apri_storico(self):
        self._crea_dialogo_storico().exec()

    def _crea_dialogo_storico(self) -> DialogoArchivioAnnoMese:
        dialogo = DialogoArchivioAnnoMese(
            self, "Storico Cassaforte",
            colonne=[
                ("DATA", "data"), ("ORA", "ora"), ("OPERAZIONE", "operazione"),
                ("ELEMENTO", "elemento"), ("PERSONA", "persona"), ("DETTAGLI", "dettagli"),
            ],
            periodi=periodi_storico_cassaforte,
            carica_mese=lambda anno, mese, testo: [
                self._evento_da_movimento(m) for m in movimenti(testo_ricerca=testo, anno=anno, mese=mese)
            ],
            dettaglio=self._dettaglio_movimento,
            con_senza_data=True,
            carica_senza_data=lambda testo: [
                self._evento_da_movimento(m) for m in movimenti_senza_data(testo_ricerca=testo)
            ],


            colonne_cicli=[
                ("ELEMENTO", "elemento"), ("USCITA", "uscita_testo"),
                ("RIENTRO", "rientro_testo"), ("STATO", "stato"),
            ],
            carica_cicli=lambda testo: [self._evento_da_ciclo(c) for c in cicli_cassaforte(testo)],
            dettaglio_cicli=self._dettaglio_ciclo,
        )
        dialogo.setObjectName("storico_cassaforte_modern_control_room")
        dialogo.setStyleSheet(FOGLIO_DI_STILE_CASSAFORTE)
        return dialogo

    @staticmethod
    def _evento_da_movimento(m: dict) -> dict:
        dettagli = []
        if m["numero_busta"]:
            busta = f"Busta {m['numero_busta']}"
            if m["data_busta"]:
                busta += f" del {m['data_busta']}"
            dettagli.append(busta)
        if m["note"]:
            dettagli.append(m["note"])
        return {
            "data": m["data"] or "", "ora": m["ora"] or "",
            "operazione": _ETICHETTE_TIPO.get(m["tipo"], m["tipo"]).upper(),
            "elemento": m["descrizione"], "persona": m["persona"] or "",
            "dettagli": "   —   ".join(dettagli),
        }

    @staticmethod
    def _dettaglio_movimento(evento: dict):
        return f"{evento['operazione']} — {evento['elemento']}", [
            ("Data", evento["data"] or "senza data"), ("Ora", evento["ora"]),
            ("Operazione", evento["operazione"]), ("Elemento", evento["elemento"]),
            ("Persona", evento["persona"]), ("Dettagli", evento["dettagli"]),
        ]

    @staticmethod
    def _evento_da_ciclo(ciclo: dict) -> dict:
        def testo(data, ora, persona, busta):
            parti = [f"{data} {ora or ''}".strip()]
            if persona:
                parti.append(persona)
            if busta:
                parti.append(f"busta {busta}")
            return "   —   ".join(parti)

        return {
            **ciclo,
            "uscita_testo": testo(
                ciclo["uscita_data"], ciclo["uscita_ora"], ciclo["uscita_persona"], ciclo["uscita_busta"],
            ),
            "rientro_testo": (
                testo(ciclo["rientro_data"], ciclo["rientro_ora"], ciclo["rientro_persona"], ciclo["rientro_busta"])
                if ciclo["rientro_data"] else "— ancora fuori —"
            ),
        }

    @staticmethod
    def _dettaglio_ciclo(ciclo: dict):
        return f"{ciclo['stato']} — {ciclo['elemento']}", [
            ("Elemento", ciclo["elemento"]),
            ("Categoria", ETICHETTE_CATEGORIE.get(ciclo["categoria"], ciclo["categoria"])),
            ("Uscita", ciclo["uscita_testo"]), ("Rientro", ciclo["rientro_testo"]),
            ("Stato", ciclo["stato"]),
        ]


    def _svuota(self):
        while self._layout_righe.count():
            item = self._layout_righe.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def _aggiorna(self):
        self._svuota()
        self._mostra_situazione(self._campo_ricerca.text())
        self._layout_righe.addStretch()

    def _mostra_situazione(self, testo: str):
        fuori = elenco_elementi(fuori=True, testo_ricerca=testo)
        dentro = elenco_elementi(fuori=False, testo_ricerca=testo)
        diretti = [e for e in dentro if not e["in_busta"]]
        imbustati = [e for e in dentro if e["in_busta"]]

        self._titolo_sezione(f"FUORI CASSAFORTE ({len(fuori)})")
        if not fuori:
            self._messaggio("Nessun elemento fuori.")
        for elemento in fuori:
            self._layout_righe.addWidget(self._riga_elemento(elemento))

        self._titolo_sezione("IN CASSAFORTE — accesso diretto")
        if not diretti:
            self._messaggio("Nessun elemento ad accesso diretto.")
        for elemento in diretti:
            self._layout_righe.addWidget(self._riga_elemento(elemento))

        self._titolo_sezione("IN CASSAFORTE — in busta sigillata")
        if not imbustati:
            self._messaggio("Nessuna busta in cassaforte.")
        for elemento in imbustati:
            self._layout_righe.addWidget(self._riga_elemento(elemento))

    def _titolo_sezione(self, testo: str):
        etichetta = QLabel(testo)
        etichetta.setObjectName("sezione_cassaforte")
        self._layout_righe.addWidget(etichetta)

    def _messaggio(self, testo: str):
        etichetta = QLabel(testo)
        etichetta.setObjectName("stato_vuoto_cassaforte")
        self._layout_righe.addWidget(etichetta)


    def _riga_elemento(self, elemento: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_elemento_cassaforte")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        testo = QVBoxLayout()

        descrizione = QLabel(elemento["descrizione"])
        descrizione.setObjectName("descrizione_elemento_cassaforte")
        descrizione.setWordWrap(True)
        testo.addWidget(descrizione)

        dettaglio = QLabel(self._dettaglio_elemento(elemento))
        dettaglio.setObjectName("dettaglio_elemento_cassaforte")
        dettaglio.setWordWrap(True)
        testo.addWidget(dettaglio)

        if elemento["note"]:
            nota = QLabel(f"⚠ {elemento['note']}")
            nota.setObjectName("nota_elemento_cassaforte")
            nota.setWordWrap(True)
            testo.addWidget(nota)

        layout.addLayout(testo, stretch=1)

        if elemento["fuori"]:
            pulsante = QPushButton("Rientro")
            pulsante.setObjectName("rientro_elemento_cassaforte")
            pulsante.clicked.connect(lambda: self._rientro(elemento))
        else:
            pulsante = QPushButton("Uscita")
            pulsante.setObjectName("uscita_elemento_cassaforte")
            pulsante.clicked.connect(lambda: self._nuova_uscita(preselezionato=elemento["id"]))
        layout.addWidget(pulsante, alignment=Qt.AlignTop)

        return riga

    def _dettaglio_elemento(self, elemento: dict) -> str:
        parti = [ETICHETTE_CATEGORIE.get(elemento["categoria"], elemento["categoria"])]

        if elemento["numero_busta"]:
            busta = f"Busta {elemento['numero_busta']}"
            busta += f" del {elemento['data_busta']}" if elemento["data_busta"] else "  ⚠ data non indicata"
            parti.append(busta)
        else:
            parti.append("Senza busta")

        if elemento["fuori"]:
            parti.append(f"Preso da {elemento['ultima_persona']}")
            parti.append(f"il {elemento['ultima_data']} alle {elemento['ultima_ora']}")
            giorni = giorni_trascorsi(elemento["ultima_data"])
            if giorni is not None:
                parti.append(f"fuori da {giorni} giorni")

        return "   —   ".join(parti)


    def _nuovo_elemento(self):
        finestra = _DialogoOperazione(
            self, "Nuovo elemento in cassaforte",
            "Stai per aggiungere un elemento alla cassaforte e registrarne il deposito.",
        )
        campo_descrizione = finestra.aggiungi_campo("Elemento:", "Es. DatoOperativoDemo560")
        campo_categoria = finestra.aggiungi_categorie()
        campo_busta = finestra.aggiungi_campo("Nr. busta:", "Facoltativo — vuoto se accesso diretto")
        campo_data_busta = finestra.aggiungi_campo("Data busta:", "GG-MM-AAAA, facoltativa")
        campo_persona = finestra.aggiungi_campo("Depositato da:", "Facoltativo")
        applica_autocomplete_operatori(campo_persona)
        campo_note = finestra.aggiungi_campo("Note:", "Facoltative")
        finestra.chiudi_con_avviso()

        if finestra.exec() != QDialog.Accepted:
            return

        descrizione = campo_descrizione.text().strip()
        if not descrizione:
            QMessageBox.warning(self, "Dati mancanti", "La descrizione dell'elemento è obbligatoria.")
            return
        if not data_valida(campo_data_busta.text()):
            QMessageBox.warning(
                self, "Data non valida",
                "La data sulla busta non è nel formato GG-MM-AAAA (es. 08-09-2026). "
                "Lasciala vuota se non la conosci.",
            )
            return

        persona = risolvi_operatore_confermato(self, campo_persona.text())
        if persona is None:
            return

        adesso = datetime.now()
        id_elemento = aggiungi_elemento(
            descrizione, campo_categoria.currentData(), campo_note.text()
        )
        registra_deposito(
            id_elemento,
            numero_busta=campo_busta.text(),
            data_busta=campo_data_busta.text(),


            data=adesso.strftime("%d-%m-%Y") if persona else None,
            ora=adesso.strftime("%H:%M") if persona else None,
            persona=persona or None,
        )
        self._aggiorna()
        self._rigenera_excel()

    def _nuova_uscita(self, preselezionato: int | None = None):
        disponibili = elenco_elementi(fuori=False)
        if not disponibili:
            QMessageBox.information(self, "Nessun elemento", "Non c'è nulla in cassaforte da prelevare.")
            return

        finestra = _DialogoOperazione(
            self, "Nuova uscita dalla cassaforte",
            "Stai per registrare il prelievo di uno o più elementi dalla cassaforte.",
        )
        campo_persona = finestra.aggiungi_campo("Ritirato da:", "Nome e cognome di chi preleva")
        applica_autocomplete_operatori(campo_persona)
        campo_note = finestra.aggiungi_campo("Note:", "Facoltative")

        elenco = QWidget()
        layout_elenco = QVBoxLayout(elenco)
        layout_elenco.setContentsMargins(0, 0, 0, 0)
        layout_elenco.addWidget(QLabel("Elementi da prelevare:"))

        selezione = []
        for elemento in disponibili:
            riga = QWidget()
            layout_riga = QHBoxLayout(riga)
            layout_riga.setContentsMargins(0, 0, 0, 0)

            casella = QCheckBox(elemento["descrizione"])
            casella.setChecked(elemento["id"] == preselezionato)
            layout_riga.addWidget(casella, stretch=1)

            campo_busta = QLineEdit(elemento["numero_busta"] or "")
            campo_busta.setPlaceholderText("senza busta")
            campo_busta.setFixedWidth(130)
            layout_riga.addWidget(campo_busta)

            layout_elenco.addWidget(riga)
            selezione.append((elemento, casella, campo_busta))

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setWidget(elenco)
        area.setMinimumHeight(180)
        finestra.aggiungi_widget(area)
        finestra.chiudi_con_avviso()

        if finestra.exec() != QDialog.Accepted:
            return

        persona = risolvi_operatore_confermato(self, campo_persona.text())
        if persona is None:
            return

        scelti = [
            {"elemento_id": e["id"], "numero_busta": campo.text(), "data_busta": e["data_busta"]}
            for e, casella, campo in selezione if casella.isChecked()
        ]

        if not persona or not scelti:
            QMessageBox.warning(
                self, "Dati mancanti",
                "Servono il nome di chi preleva e almeno un elemento selezionato.",
            )
            return

        adesso = datetime.now()
        registra_uscita(
            scelti, persona=persona,
            data=adesso.strftime("%d-%m-%Y"), ora=adesso.strftime("%H:%M"),
            note=campo_note.text(),
        )
        self._aggiorna()
        self._rigenera_excel()

    def _rientro(self, elemento: dict):
        finestra = _DialogoOperazione(
            self, "Rientro in cassaforte",
            f"Stai per registrare il rientro di:\n«{elemento['descrizione']}»\n"
            f"Uscito il {elemento['ultima_data']} con {elemento['ultima_persona']}.",
        )
        campo_persona = finestra.aggiungi_campo("Riconsegnato da:", "Nome e cognome")
        applica_autocomplete_operatori(campo_persona)
        campo_busta = finestra.aggiungi_campo(
            "Nr. busta al rientro:", "Può essere diversa da quella di uscita"
        )
        campo_data_busta = finestra.aggiungi_campo("Data busta:", "GG-MM-AAAA, facoltativa")
        campo_note = finestra.aggiungi_campo("Note:", "Facoltative")
        finestra.chiudi_con_avviso()

        if finestra.exec() != QDialog.Accepted:
            return

        persona = risolvi_operatore_confermato(self, campo_persona.text())
        if persona is None:
            return
        if not persona:
            QMessageBox.warning(self, "Dati mancanti", "Il nome di chi riconsegna è obbligatorio.")
            return
        if not data_valida(campo_data_busta.text()):
            QMessageBox.warning(
                self, "Data non valida",
                "La data sulla busta non è nel formato GG-MM-AAAA (es. 08-09-2026). "
                "Lasciala vuota se non la conosci.",
            )
            return

        adesso = datetime.now()
        registra_rientro(
            elemento["id"], persona=persona,
            data=adesso.strftime("%d-%m-%Y"), ora=adesso.strftime("%H:%M"),
            numero_busta=campo_busta.text(), data_busta=campo_data_busta.text(),
            note=campo_note.text(),
        )
        self._aggiorna()
        self._rigenera_excel()

    def _aggiorna_file_excel(self):
        risposta = QMessageBox.question(
            self, "Aggiornare il file Excel?",
            f"Stai per rigenerare il file delle movimentazioni.\n\n{_avviso_file_excel()}",
        )
        if risposta != QMessageBox.Yes:
            return

        if not _cartella_configurata():
            QMessageBox.warning(
                self, "Cartella non configurata",
                "La cartella \"Cassaforte\" non è configurata o non è raggiungibile. "
                "Configurala nelle Impostazioni.",
            )
            return

        if self._rigenera_excel():
            QMessageBox.information(self, "File aggiornato", f"{NOME_FILE} è stato aggiornato.")

    def _rigenera_excel(self) -> bool:
        """Documentazione della versione portfolio."""
        cartella = _cartella_configurata()
        if not cartella:
            return False
        try:
            genera_prospetto(cartella)
        except OSError as errore:
            QMessageBox.warning(
                self, "File Excel non aggiornato",
                "Il movimento è stato salvato nel database, ma non è stato possibile "
                f"aggiornare il file Excel: {errore}\n\n"
                "Puoi riprovare con il pulsante \"Aggiorna file Excel\".",
            )
            return False
        return True
