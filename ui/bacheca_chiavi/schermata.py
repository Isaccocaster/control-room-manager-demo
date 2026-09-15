"""Documentazione della versione portfolio."""
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialogButtonBox,
    QDialog,
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

from config.impostazioni import cartella_esiste, carica_impostazioni
from data.chiavi import (
    chiave_e_fuori,
    chiavi_fuori,
    cicli_chiavi,
    periodi_storico_chiavi,
    registra_rientro_chiave,
    registra_uscita_chiave,
    storico_chiavi,
    aggiungi_cassaforte,
    aggiungi_chiave,
    cerca_cassaforte,
    cerca_chiavi,
    elenco_bacheche,
    modifica_cassaforte,
    modifica_chiave,
    raggruppa_per_blocco,
    rimuovi_cassaforte,
    rimuovi_chiave,
)
from documents.excel.prospetto_chiavi import genera_prospetto_bacheca, genera_prospetto_cassaforte
from ui.bacheca_chiavi.stile import FOGLIO_DI_STILE_BACHECA
from ui.comune.archivio_anno_mese import DialogoArchivioAnnoMese
from ui.comune.campo_operatore import richiedi_nome_operatore
from ui.comune.icone import SIMBOLI_MODULI, SIMBOLO_STORICO, applica_icona_pulsante
from ui.comune.riga_scorrevole import riga_scorrevole
from ui.sfondo import PaginaConSfondo
from ui.tema import HOME_OPACITA_VELO

PERCORSO_FOTO_SFONDO = Path(__file__).parent.parent / "assets" / "images" / "demo_bacheca_chiavi.jpg"

NOME_CASSAFORTE = "Cassaforte Area Demo"
NOME_CHIAVI_FUORI = "Chiavi fuori"


class _DialogoChiave(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, mostra_blocco: bool, numero=1, descrizione="", blocco=""):
        super().__init__(parent)
        self.setObjectName("dialogo_chiave_bacheca")
        self.setStyleSheet(FOGLIO_DI_STILE_BACHECA)
        self.setWindowTitle("Chiave")

        layout = QFormLayout(self)

        self.campo_numero = QSpinBox()
        self.campo_numero.setObjectName("numero_chiave_bacheca")
        self.campo_numero.setRange(1, 100000)
        self.campo_numero.setValue(numero)
        layout.addRow("Numero:", self.campo_numero)

        self.campo_descrizione = QLineEdit(descrizione)
        self.campo_descrizione.setObjectName("descrizione_chiave_bacheca")
        layout.addRow("Descrizione:", self.campo_descrizione)

        self.campo_blocco = QLineEdit(blocco or "")
        self.campo_blocco.setObjectName("blocco_chiave_bacheca")
        if mostra_blocco:
            layout.addRow("Blocco:", self.campo_blocco)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addRow(pulsanti)

    def valori(self):
        return self.campo_numero.value(), self.campo_descrizione.text().strip(), self.campo_blocco.text().strip()


class _DialogoCassaforte(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, piano="", targhetta=1, area_ufficio="", numero_chiavi=1, colore_targhetta=""):
        super().__init__(parent)
        self.setObjectName("dialogo_voce_cassaforte_bacheca")
        self.setStyleSheet(FOGLIO_DI_STILE_BACHECA)
        self.setWindowTitle("Voce cassaforte")

        layout = QFormLayout(self)

        self.campo_piano = QLineEdit(piano or "")
        self.campo_piano.setObjectName("piano_voce_cassaforte_bacheca")
        layout.addRow("Piano:", self.campo_piano)

        self.campo_targhetta = QSpinBox()
        self.campo_targhetta.setObjectName("targhetta_voce_cassaforte_bacheca")
        self.campo_targhetta.setRange(1, 100000)
        self.campo_targhetta.setValue(targhetta or 1)
        layout.addRow("Targhetta:", self.campo_targhetta)

        self.campo_area_ufficio = QLineEdit(area_ufficio or "")
        self.campo_area_ufficio.setObjectName("area_voce_cassaforte_bacheca")
        layout.addRow("Area/Ufficio:", self.campo_area_ufficio)

        self.campo_numero_chiavi = QSpinBox()
        self.campo_numero_chiavi.setObjectName("quantita_voce_cassaforte_bacheca")
        self.campo_numero_chiavi.setRange(1, 1000)
        self.campo_numero_chiavi.setValue(numero_chiavi or 1)
        layout.addRow("N. Chiavi:", self.campo_numero_chiavi)

        self.campo_colore = QLineEdit(colore_targhetta or "")
        self.campo_colore.setObjectName("colore_voce_cassaforte_bacheca")
        layout.addRow("Colore Targhetta:", self.campo_colore)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addRow(pulsanti)

    def valori(self):
        return (
            self.campo_piano.text().strip(),
            self.campo_targhetta.value(),
            self.campo_area_ufficio.text().strip(),
            self.campo_numero_chiavi.value(),
            self.campo_colore.text().strip(),
        )


class SchermataBachecaChiavi(PaginaConSfondo):
    def __init__(self):
        super().__init__(PERCORSO_FOTO_SFONDO, HOME_OPACITA_VELO)
        self.setObjectName("bacheca_chiavi_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_BACHECA)

        self._bacheche = elenco_bacheche()
        self._bacheca_selezionata = None

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(40, 16, 40, 24)

        pannello = QFrame()
        pannello.setObjectName("pannello_bacheca_chiavi")

        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(32, 28, 32, 28)
        layout_pannello.setSpacing(14)

        titolo = QLabel("Bacheca Chiavi")
        titolo.setObjectName("titolo_bacheca_chiavi")
        layout_pannello.addWidget(titolo)

        sottotitolo = QLabel("Controllo disponibilità, consegne e rientri delle chiavi Demo")
        sottotitolo.setObjectName("sottotitolo_bacheca_chiavi")
        sottotitolo.setWordWrap(True)
        layout_pannello.addWidget(sottotitolo)

        layout_pannello.addWidget(self._crea_selettore_bacheca())

        contenitore_ricerca = QWidget()
        contenitore_ricerca.setObjectName("contenitore_azioni_bacheca")
        riga_ricerca = QHBoxLayout(contenitore_ricerca)
        riga_ricerca.setContentsMargins(0, 0, 0, 0)
        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setObjectName("ricerca_bacheca_chiavi")
        self._campo_ricerca.setPlaceholderText("Scrivi per cercare una chiave...")
        self._campo_ricerca.textChanged.connect(self._aggiorna_risultati)
        riga_ricerca.addWidget(self._campo_ricerca, stretch=1)

        self._pulsante_aggiungi = QPushButton("+ Aggiungi chiave")
        self._pulsante_aggiungi.setObjectName("aggiungi_chiave_bacheca")
        self._pulsante_aggiungi.setEnabled(False)
        self._pulsante_aggiungi.clicked.connect(self._aggiungi)
        riga_ricerca.addWidget(self._pulsante_aggiungi)


        pulsante_storico = QPushButton("Storico chiavi")
        pulsante_storico.setObjectName("storico_bacheca_chiavi")
        applica_icona_pulsante(pulsante_storico, SIMBOLO_STORICO)
        pulsante_storico.clicked.connect(self._apri_storico)
        riga_ricerca.addWidget(pulsante_storico)


        area_azioni = riga_scorrevole(contenitore_ricerca)
        area_azioni.setProperty("ruolo", "azioni_bacheca")
        layout_pannello.addWidget(area_azioni)

        self._area_risultati = QScrollArea()
        self._area_risultati.setObjectName("risultati_bacheca_chiavi")
        self._area_risultati.setWidgetResizable(True)
        self._area_risultati.setFrameShape(QFrame.NoFrame)

        self._contenitore_risultati = QWidget()
        self._contenitore_risultati.setObjectName("contenitore_risultati_bacheca")
        self._layout_risultati = QVBoxLayout(self._contenitore_risultati)
        self._layout_risultati.setContentsMargins(0, 0, 0, 0)
        self._layout_risultati.setSpacing(8)
        self._area_risultati.setWidget(self._contenitore_risultati)

        layout_pannello.addWidget(self._area_risultati, stretch=1)

        layout_esterno.addWidget(pannello, stretch=1)

        self._mostra_messaggio("Seleziona una bacheca per iniziare a cercare.")

    def _apri_storico(self):
        self._crea_dialogo_storico().exec()

    def _crea_dialogo_storico(self) -> DialogoArchivioAnnoMese:
        """Documentazione della versione portfolio."""
        dialogo = DialogoArchivioAnnoMese(
            self, "Storico Chiavi",
            colonne=[
                ("DATA", "data"), ("ORA", "ora"), ("OPERAZIONE", "operazione"),
                ("CHIAVE", "elemento"), ("PERSONA", "persona"), ("BACHECA", "bacheca"),
            ],
            periodi=periodi_storico_chiavi,
            carica_mese=lambda anno, mese, testo: storico_chiavi(
                testo_ricerca=testo, anno=anno, mese=mese,
            ),
            dettaglio=self._dettaglio_evento,


            colonne_cicli=[
                ("CHIAVE", "elemento"), ("BACHECA", "bacheca"),
                ("USCITA", "uscita_testo"), ("RIENTRO", "rientro_testo"), ("STATO", "stato"),
            ],
            carica_cicli=lambda testo: [self._evento_da_ciclo(c) for c in cicli_chiavi(testo)],
            dettaglio_cicli=self._dettaglio_ciclo,
        )
        dialogo.setObjectName("storico_bacheca_chiavi_modern_control_room")
        dialogo.setStyleSheet(FOGLIO_DI_STILE_BACHECA)
        return dialogo

    @staticmethod
    def _dettaglio_evento(evento: dict):
        return f"{evento['operazione']} — {evento['elemento']}", [
            ("Data", evento["data"]), ("Ora", evento["ora"]),
            ("Operazione", evento["operazione"]), ("Chiave", evento["elemento"]),
            ("Bacheca", evento["bacheca"]), ("Persona", evento["persona"]),
            ("Note", evento.get("note")),
        ]

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
        return f"{ciclo['stato']} — {ciclo['elemento']}", [
            ("Chiave", ciclo["elemento"]), ("Bacheca", ciclo["bacheca"]),
            ("Uscita", ciclo["uscita_testo"]), ("Rientro", ciclo["rientro_testo"]),
            ("Stato", ciclo["stato"]),
        ]

    def _crea_riga_chiave_fuori(self, voce: dict) -> QWidget:
        """Documentazione della versione portfolio."""
        riga = QFrame()
        riga.setObjectName("riga_bacheca_chiavi")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        testo = QVBoxLayout()
        intestazione = QLabel(f"{voce['numero']} — {voce['descrizione']}")
        intestazione.setObjectName("identita_chiave_bacheca")
        intestazione.setWordWrap(True)
        testo.addWidget(intestazione)

        parti = [f"Bacheca: {voce['bacheca']}", f"Presa da {voce['persona']}",
                 f"il {voce['data']} alle {voce['ora']}"]
        if voce.get("note"):
            parti.append(voce["note"])
        dettaglio = QLabel("   —   ".join(parti))
        dettaglio.setObjectName("dettaglio_chiave_bacheca")
        dettaglio.setWordWrap(True)
        testo.addWidget(dettaglio)
        layout.addLayout(testo, stretch=1)

        pulsante = QPushButton("Registra rientro")
        pulsante.setObjectName("rientro_chiave")
        pulsante.clicked.connect(lambda: self._rientro_chiave(voce))
        layout.addWidget(pulsante, alignment=Qt.AlignTop)
        return riga

    def _uscita_chiave(self, chiave: dict, nome_bacheca: str):
        persona = richiedi_nome_operatore(
            self, "Uscita chiave",
            f"Chi prende la chiave {chiave['numero']} — {chiave['descrizione']}?",
        )
        if persona is None:
            return
        adesso = datetime.now()
        registra_uscita_chiave(
            chiave["id"], persona,
            adesso.strftime("%d-%m-%Y"), adesso.strftime("%H:%M"),
        )
        self._aggiorna_risultati(self._campo_ricerca.text())
        self._aggiorna_badge()

    def _rientro_chiave(self, voce: dict):
        persona = richiedi_nome_operatore(
            self, "Rientro chiave",
            f"Chi riporta la chiave {voce['numero']} — {voce['descrizione']}?",
            valore_iniziale=voce["persona"],
        )
        if persona is None:
            return
        adesso = datetime.now()
        registra_rientro_chiave(
            voce["chiave_id"], persona,
            adesso.strftime("%d-%m-%Y"), adesso.strftime("%H:%M"),
        )
        self._aggiorna_risultati(self._campo_ricerca.text())
        self._aggiorna_badge()

    def _aggiorna_badge(self):
        """Documentazione della versione portfolio."""
        finestra = self.window()
        aggiorna = getattr(finestra, "aggiorna_badge_chiavi", None)
        if callable(aggiorna):
            aggiorna()

    def _crea_selettore_bacheca(self) -> QScrollArea:
        contenitore = QWidget()
        contenitore.setObjectName("contenitore_selettore_bacheche")
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        gruppo = QButtonGroup(self)
        gruppo.setExclusive(True)
        self._gruppo_bacheche = gruppo

        nomi_pulsanti = (
            [bacheca["nome"] for bacheca in self._bacheche]
            + [NOME_CASSAFORTE, NOME_CHIAVI_FUORI]
        )
        for nome in nomi_pulsanti:
            pulsante = QPushButton(nome)
            pulsante.setObjectName("filtro_bacheca")
            if nome == NOME_CHIAVI_FUORI:
                applica_icona_pulsante(
                    pulsante, SIMBOLI_MODULI["Bacheca Chiavi"], colore="#9FC8F2"
                )
            pulsante.setCheckable(True)
            pulsante.clicked.connect(lambda _, n=nome: self._seleziona_bacheca(n))
            gruppo.addButton(pulsante)
            layout.addWidget(pulsante)
        layout.addStretch()


        area = riga_scorrevole(contenitore)
        area.setProperty("ruolo", "selettore_bacheche")
        return area

    def _seleziona_bacheca(self, nome: str):
        self._bacheca_selezionata = nome
        self._pulsante_aggiungi.setEnabled(True)
        self._campo_ricerca.clear()
        self._aggiorna_risultati("")

    def _bacheca_corrente(self) -> dict:
        return next(b for b in self._bacheche if b["nome"] == self._bacheca_selezionata)

    def _svuota_risultati(self):
        while self._layout_risultati.count():
            item = self._layout_risultati.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def _aggiorna_risultati(self, testo: str):
        self._svuota_risultati()

        if self._bacheca_selezionata is None:
            self._mostra_messaggio("Seleziona una bacheca per iniziare a cercare.")
            return

        if self._bacheca_selezionata == NOME_CHIAVI_FUORI:
            righe = [self._crea_riga_chiave_fuori(voce) for voce in chiavi_fuori()]
            if not righe:
                self._mostra_messaggio("Nessuna chiave fuori al momento.")
                return
        elif self._bacheca_selezionata == NOME_CASSAFORTE:
            righe = [self._crea_riga_cassaforte(voce) for voce in cerca_cassaforte(testo)]
        else:
            bacheca = self._bacheca_corrente()
            righe = []
            for nome_blocco, chiavi in raggruppa_per_blocco(cerca_chiavi(bacheca["id"], testo)):
                if nome_blocco:
                    righe.append(self._crea_intestazione_blocco(nome_blocco))
                righe.extend(self._crea_riga_chiave(chiave, bacheca["nome"]) for chiave in chiavi)

        if not righe:
            self._mostra_messaggio("Nessun risultato.")
            return

        for riga in righe:
            self._layout_risultati.addWidget(riga)
        self._layout_risultati.addStretch()

    def _mostra_messaggio(self, testo: str):
        etichetta = QLabel(testo)
        etichetta.setObjectName("stato_vuoto_bacheca")
        self._layout_risultati.addWidget(etichetta)
        self._layout_risultati.addStretch()


    def _crea_intestazione_blocco(self, nome_blocco: str) -> QWidget:
        """Documentazione della versione portfolio."""
        etichetta = QLabel(nome_blocco)
        etichetta.setObjectName("intestazione_blocco_bacheca")
        etichetta.setWordWrap(True)
        return etichetta

    def _crea_riga_chiave(self, chiave: dict, nome_bacheca: str) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_bacheca_chiavi")
        layout_esterno = QHBoxLayout(riga)
        layout_esterno.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()
        intestazione = QLabel(f"Numero: {chiave['numero']}   —   Bacheca: {nome_bacheca}")
        intestazione.setObjectName("identita_chiave_bacheca")
        layout_testo.addWidget(intestazione)

        descrizione = QLabel(chiave["descrizione"])
        descrizione.setObjectName("dettaglio_chiave_bacheca")
        descrizione.setWordWrap(True)
        layout_testo.addWidget(descrizione)


        layout_esterno.addLayout(layout_testo, stretch=1)


        if not chiave_e_fuori(chiave["id"]):
            pulsante_uscita = QPushButton("Uscita")
            pulsante_uscita.setObjectName("uscita_chiave")
            pulsante_uscita.setToolTip("Registra la consegna di questa chiave")
            pulsante_uscita.clicked.connect(lambda: self._uscita_chiave(chiave, nome_bacheca))
            layout_esterno.addWidget(pulsante_uscita)

        layout_esterno.addLayout(self._crea_pulsanti_riga(
            al_modifica=lambda: self._modifica_chiave(chiave),
            al_rimuovi=lambda: self._rimuovi_chiave(chiave),
        ))
        return riga

    def _crea_riga_cassaforte(self, voce: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_bacheca_chiavi")
        layout_esterno = QHBoxLayout(riga)
        layout_esterno.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()
        intestazione = QLabel(f"Targhetta: {voce['targhetta']}   —   Piano: {voce['piano']}")
        intestazione.setObjectName("identita_chiave_bacheca")
        layout_testo.addWidget(intestazione)

        dettaglio = QLabel(
            f"{voce['area_ufficio']}  ({voce['numero_chiavi']} chiavi, targhetta {voce['colore_targhetta']})"
        )
        dettaglio.setObjectName("dettaglio_chiave_bacheca")
        dettaglio.setWordWrap(True)
        layout_testo.addWidget(dettaglio)

        layout_esterno.addLayout(layout_testo, stretch=1)
        layout_esterno.addLayout(self._crea_pulsanti_riga(
            al_modifica=lambda: self._modifica_cassaforte(voce),
            al_rimuovi=lambda: self._rimuovi_cassaforte(voce),
        ))
        return riga

    def _crea_pulsanti_riga(self, al_modifica, al_rimuovi) -> QHBoxLayout:
        layout = QHBoxLayout()

        pulsante_modifica = QPushButton("Modifica")
        pulsante_modifica.setObjectName("modifica_chiave")
        pulsante_modifica.clicked.connect(al_modifica)
        layout.addWidget(pulsante_modifica)

        pulsante_rimuovi = QPushButton("Rimuovi")
        pulsante_rimuovi.setObjectName("rimuovi_chiave")
        pulsante_rimuovi.clicked.connect(al_rimuovi)
        layout.addWidget(pulsante_rimuovi)

        return layout


    def _conferma(self, messaggio: str) -> bool:
        risposta = QMessageBox.question(
            self,
            "Confermi la modifica?",
            f"{messaggio}\n\nIl prospetto Excel di questa bacheca verrà aggiornato di conseguenza.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return risposta == QMessageBox.Yes

    def _aggiungi(self):
        if self._bacheca_selezionata == NOME_CASSAFORTE:
            finestra = _DialogoCassaforte(self)
            if finestra.exec() == QDialog.Accepted:
                piano, targhetta, area_ufficio, numero_chiavi, colore = finestra.valori()
                if not area_ufficio:
                    return
                if not self._conferma(f'Aggiungere la voce "{area_ufficio}"?'):
                    return
                aggiungi_cassaforte(piano, targhetta, area_ufficio, numero_chiavi, colore)
            else:
                return
        else:
            bacheca = self._bacheca_corrente()
            finestra = _DialogoChiave(self, mostra_blocco=(bacheca["nome"] == "Tech"))
            if finestra.exec() == QDialog.Accepted:
                numero, descrizione, blocco = finestra.valori()
                if not descrizione:
                    return
                if not self._conferma(f'Aggiungere la chiave "{descrizione}"?'):
                    return
                aggiungi_chiave(bacheca["id"], numero, descrizione, blocco)
            else:
                return

        self._aggiorna_risultati(self._campo_ricerca.text())
        self._rigenera_prospetto()

    def _modifica_chiave(self, chiave: dict):
        bacheca = self._bacheca_corrente()
        finestra = _DialogoChiave(
            self, mostra_blocco=(bacheca["nome"] == "Tech"),
            numero=chiave["numero"], descrizione=chiave["descrizione"], blocco=chiave.get("blocco") or "",
        )
        if finestra.exec() == QDialog.Accepted:
            numero, descrizione, blocco = finestra.valori()
            if not descrizione:
                return
            if not self._conferma(f'Modificare la chiave "{chiave["descrizione"]}"?'):
                return
            modifica_chiave(chiave["id"], numero, descrizione, blocco)
            self._aggiorna_risultati(self._campo_ricerca.text())
            self._rigenera_prospetto()

    def _rimuovi_chiave(self, chiave: dict):
        if self._conferma(f'Rimuovere la chiave "{chiave["descrizione"]}"?'):
            rimuovi_chiave(chiave["id"])
            self._aggiorna_risultati(self._campo_ricerca.text())
            self._rigenera_prospetto()

    def _modifica_cassaforte(self, voce: dict):
        finestra = _DialogoCassaforte(
            self, piano=voce["piano"], targhetta=voce["targhetta"], area_ufficio=voce["area_ufficio"],
            numero_chiavi=voce["numero_chiavi"], colore_targhetta=voce["colore_targhetta"],
        )
        if finestra.exec() == QDialog.Accepted:
            piano, targhetta, area_ufficio, numero_chiavi, colore = finestra.valori()
            if not area_ufficio:
                return
            if not self._conferma(f'Modificare la voce "{voce["area_ufficio"]}"?'):
                return
            modifica_cassaforte(voce["id"], piano, targhetta, area_ufficio, numero_chiavi, colore)
            self._aggiorna_risultati(self._campo_ricerca.text())
            self._rigenera_prospetto()

    def _rimuovi_cassaforte(self, voce: dict):
        if self._conferma(f'Rimuovere la voce "{voce["area_ufficio"]}"?'):
            rimuovi_cassaforte(voce["id"])
            self._aggiorna_risultati(self._campo_ricerca.text())
            self._rigenera_prospetto()


    def _rigenera_prospetto(self):
        impostazioni = carica_impostazioni()
        cartella = impostazioni.get("cartella_prospetti_chiavi", "")

        if not cartella_esiste(cartella):
            QMessageBox.warning(
                self,
                "Cartella non configurata",
                "La modifica è stata salvata, ma non è stato possibile generare il prospetto Excel "
                "perché la cartella \"Prospetti Chiavi\" non è configurata o non è raggiungibile. "
                "Configurala nelle Impostazioni.",
            )
            return

        try:
            if self._bacheca_selezionata == NOME_CASSAFORTE:
                genera_prospetto_cassaforte(cartella)
            else:
                bacheca = self._bacheca_corrente()
                genera_prospetto_bacheca(bacheca["id"], bacheca["nome"], cartella)
        except OSError as errore:
            QMessageBox.warning(self, "Errore", f"Impossibile generare il prospetto Excel: {errore}")
