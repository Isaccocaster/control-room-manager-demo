"""Documentazione della versione portfolio."""
import tempfile
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
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

from config.impostazioni import cartella_esiste, carica_impostazioni
from data.rapporti_giornalieri import (
    STATO_APERTO,
    aggiorna_cartella,
    cartella_archivio,
    crea_rapporto,
    formatta_nome_file,
    modifica_dati_operatore,
    rapporti_aperti_di,
    rapporti_non_archiviati,
    rapporto_esistente,
    segna_aperto,
    segna_chiuso,
    tutti_i_rapporti,
)
from documents.word.rapporto_giornaliero import (
    aggiorna_campi_automatici,
    crea_documento_da_modello,
    esporta_pdf,
    percorso_modello,
)
from ui.comune.campo_operatore import (
    applica_autocomplete_operatore_doppio,
    risolvi_operatore_nome_cognome_confermato,
)
from ui.comune.campo_orario import crea_campo_orario, testo_orario
from ui.comune.riga_scorrevole import riga_scorrevole
from ui.rapporto_giornaliero.archivio_rapporti import DialogoArchivioRapporti
from ui.rapporto_giornaliero.stile import FOGLIO_DI_STILE_RAPPORTO, PERCORSO_FOTO_RAPPORTO
from ui.sfondo import PaginaConSfondo
from ui.tema import BLU_NAVY_SCURO, HOME_OPACITA_VELO, TESTO_ATTENUATO, TESTO_CHIARO

CHIAVE_CARTELLA_RAPPORTI = "cartella_rapporti"
PERCORSO_FOTO_SFONDO = PERCORSO_FOTO_RAPPORTO


_CATEGORIA_COMPILATORI_RAPPORTO = "sala_controllo"


class _IconaRapportoFotografica(QWidget):
    """Documentazione della versione portfolio."""

    DIMENSIONE = 58

    def __init__(self):
        super().__init__()
        self.setFixedSize(self.DIMENSIONE, self.DIMENSIONE)
        self._foto = QPixmap(str(PERCORSO_FOTO_SFONDO))

    def paintEvent(self, evento):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rettangolo = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        percorso = QPainterPath()
        percorso.addRoundedRect(rettangolo, 10, 10)

        painter.save()
        painter.setClipPath(percorso)
        if not self._foto.isNull():
            foto = self._foto.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - foto.width()) // 2
            y = (self.height() - foto.height()) // 2
            painter.drawPixmap(x, y, foto)
        velo = QColor(BLU_NAVY_SCURO)
        velo.setAlpha(176)
        painter.fillPath(percorso, velo)
        painter.restore()

        painter.setPen(QPen(QColor("#5B8DCF"), 1))
        painter.drawPath(percorso)


        painter.setPen(QPen(QColor(TESTO_CHIARO), 2))
        painter.drawRoundedRect(QRectF(19, 13, 20, 30), 2, 2)
        painter.drawLine(32, 13, 39, 20)
        painter.drawLine(32, 13, 32, 20)
        painter.drawLine(32, 20, 39, 20)
        painter.drawLine(23, 27, 35, 27)
        painter.drawLine(23, 33, 35, 33)


def _cartella_rapporti() -> str:
    percorso = carica_impostazioni().get(CHIAVE_CARTELLA_RAPPORTI, "")
    return percorso if cartella_esiste(percorso) else ""


class _DialogoNuovoRapporto(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("dialogo_operativo_rapporto")
        self.setProperty("tipo", "nuovo")
        self.setWindowTitle("Nuovo rapporto")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        data_oggi = datetime.now().strftime("%d-%m-%Y")
        intestazione = QLabel(f"Data del turno: {data_oggi} (giorno corrente)")
        intestazione.setObjectName("titolo_dialogo_rapporto")
        layout.addWidget(intestazione)

        modulo = QFormLayout()
        self.campo_nome = QLineEdit()
        self.campo_nome.setObjectName("campo_nome_operatore_rapporto")
        self.campo_cognome = QLineEdit()
        self.campo_cognome.setObjectName("campo_cognome_operatore_rapporto")
        applica_autocomplete_operatore_doppio(
            self.campo_nome, self.campo_cognome, categoria=_CATEGORIA_COMPILATORI_RAPPORTO,
        )


        self.campo_ora_inizio = crea_campo_orario("22:00")
        self.campo_ora_fine = crea_campo_orario("06:00")
        modulo.addRow("Nome operatore:", self.campo_nome)
        modulo.addRow("Cognome operatore:", self.campo_cognome)
        modulo.addRow("Ora inizio turno:", self.campo_ora_inizio)
        modulo.addRow("Ora fine turno:", self.campo_ora_fine)
        layout.addLayout(modulo)

        pulsanti = QDialogButtonBox()
        conferma = pulsanti.addButton("Crea rapporto", QDialogButtonBox.AcceptRole)
        conferma.setObjectName("conferma_dialogo_rapporto")
        annulla = pulsanti.addButton("Annulla", QDialogButtonBox.RejectRole)
        annulla.setObjectName("annulla_dialogo_rapporto")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)


class _DialogoModificaRapporto(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, rapporto: dict):
        super().__init__(parent)
        self.setObjectName("dialogo_operativo_rapporto")
        self.setProperty("tipo", "modifica")
        self.setWindowTitle("Modifica rapporto")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        intestazione = QLabel(f"Data del turno: {rapporto['data_turno']} (non modificabile)")
        intestazione.setObjectName("titolo_dialogo_rapporto")
        layout.addWidget(intestazione)

        modulo = QFormLayout()
        self.campo_nome = QLineEdit(rapporto["operatore_nome"])
        self.campo_nome.setObjectName("campo_nome_operatore_rapporto")
        self.campo_cognome = QLineEdit(rapporto["operatore_cognome"])
        self.campo_cognome.setObjectName("campo_cognome_operatore_rapporto")
        applica_autocomplete_operatore_doppio(
            self.campo_nome, self.campo_cognome, categoria=_CATEGORIA_COMPILATORI_RAPPORTO,
        )
        self.campo_ora_inizio = crea_campo_orario(rapporto["ora_inizio"])
        self.campo_ora_fine = crea_campo_orario(rapporto["ora_fine"])
        modulo.addRow("Nome operatore:", self.campo_nome)
        modulo.addRow("Cognome operatore:", self.campo_cognome)
        modulo.addRow("Ora inizio turno:", self.campo_ora_inizio)
        modulo.addRow("Ora fine turno:", self.campo_ora_fine)
        layout.addLayout(modulo)

        pulsanti = QDialogButtonBox()
        conferma = pulsanti.addButton("Salva correzione", QDialogButtonBox.AcceptRole)
        conferma.setObjectName("conferma_dialogo_rapporto")
        annulla = pulsanti.addButton("Annulla", QDialogButtonBox.RejectRole)
        annulla.setObjectName("annulla_dialogo_rapporto")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)


class _DialogoArchiviazione(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("dialogo_operativo_rapporto")
        self.setProperty("tipo", "archiviazione")
        self.setWindowTitle("Archivia rapporti")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        istruzione = QLabel("Data dei rapporti da archiviare (GG-MM-AAAA):")
        istruzione.setObjectName("titolo_dialogo_rapporto")
        layout.addWidget(istruzione)

        self.campo_data = QLineEdit(datetime.now().strftime("%d-%m-%Y"))
        self.campo_data.setObjectName("campo_data_archiviazione_rapporto")
        layout.addWidget(self.campo_data)

        pulsanti = QDialogButtonBox()
        conferma = pulsanti.addButton("Archivia", QDialogButtonBox.AcceptRole)
        conferma.setObjectName("conferma_dialogo_rapporto")
        annulla = pulsanti.addButton("Annulla", QDialogButtonBox.RejectRole)
        annulla.setObjectName("annulla_dialogo_rapporto")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)


class SchermataRapportoGiornaliero(PaginaConSfondo):
    def __init__(self, finestra_principale):
        """Documentazione della versione portfolio."""
        super().__init__(PERCORSO_FOTO_SFONDO, opacita_velo=HOME_OPACITA_VELO)
        self._finestra_principale = finestra_principale
        self.setObjectName("rapporto_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_RAPPORTO)

        layout_esterno = QVBoxLayout(self)
        layout_esterno.setContentsMargins(24, 22, 24, 22)
        layout_esterno.setSpacing(14)

        titolo = QLabel("Rapporto Giornaliero")
        titolo.setObjectName("titolo_rapporto")
        layout_esterno.addWidget(titolo)

        sottotitolo = QLabel(
            "Crea, compila e consulta i rapporti operativi dei turni di oggi."
        )
        sottotitolo.setObjectName("sottotitolo_rapporto")
        sottotitolo.setWordWrap(True)
        layout_esterno.addWidget(sottotitolo)

        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(20)

        pannello = QFrame()
        pannello.setObjectName("pannello_home")
        layout_pannello = QVBoxLayout(pannello)
        layout_pannello.setContentsMargins(18, 16, 18, 18)
        layout_pannello.setSpacing(12)

        intestazione_elenco = QHBoxLayout()
        intestazione_elenco.setContentsMargins(0, 0, 0, 0)
        intestazione_elenco.setSpacing(10)
        self._titolo_elenco = QLabel("RAPPORTI DI OGGI")
        self._titolo_elenco.setObjectName("titolo_sezione_rapporto")
        intestazione_elenco.addWidget(self._titolo_elenco)
        intestazione_elenco.addStretch()
        self._conteggio_rapporti = QLabel("0 rapporti")
        self._conteggio_rapporti.setObjectName("conteggio_rapporti")
        intestazione_elenco.addWidget(self._conteggio_rapporti)
        layout_pannello.addLayout(intestazione_elenco)

        layout_pannello.addWidget(self._crea_barra_azioni())

        self._area_risultati = QScrollArea()
        self._area_risultati.setObjectName("elenco_rapporti")
        self._area_risultati.setWidgetResizable(True)
        self._area_risultati.setFrameShape(QFrame.NoFrame)
        self._area_risultati.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._contenitore_righe = QWidget()
        self._layout_righe = QVBoxLayout(self._contenitore_righe)
        self._layout_righe.setContentsMargins(0, 0, 0, 0)
        self._layout_righe.setSpacing(8)
        self._area_risultati.setWidget(self._contenitore_righe)

        layout_pannello.addWidget(self._area_risultati, stretch=1)

        corpo.addWidget(pannello, stretch=1)
        corpo.addWidget(self._crea_pannello_gestione())
        layout_esterno.addLayout(corpo, stretch=1)

        self._aggiorna_elenco()

    def showEvent(self, evento):
        """Documentazione della versione portfolio."""
        super().showEvent(evento)
        self._aggiorna_elenco()


    def _crea_barra_azioni(self) -> QScrollArea:
        contenitore = QWidget()
        layout = QHBoxLayout(contenitore)
        layout.setContentsMargins(0, 0, 0, 0)

        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setObjectName("ricerca_rapporti")
        self._campo_ricerca.setPlaceholderText("Cerca tra i rapporti non archiviati...")
        self._campo_ricerca.setClearButtonEnabled(True)
        self._campo_ricerca.textChanged.connect(lambda _: self._aggiorna_elenco())
        layout.addWidget(self._campo_ricerca, stretch=1)
        return riga_scorrevole(contenitore)

    def _crea_pannello_gestione(self) -> QWidget:
        """Documentazione della versione portfolio."""
        pannello = QFrame()
        pannello.setObjectName("pannello_home")
        pannello.setMaximumWidth(292)

        layout = QVBoxLayout(pannello)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        titolo = QLabel("GESTIONE RAPPORTI")
        titolo.setObjectName("titolo_sezione_rapporto")
        layout.addWidget(titolo)

        supporto = QLabel("Le azioni principali del turno, sempre nello stesso punto.")
        supporto.setObjectName("testo_supporto_rapporto")
        supporto.setWordWrap(True)
        layout.addWidget(supporto)
        layout.addSpacing(4)

        self._pulsante_nuovo = QPushButton("+ Nuovo rapporto")


        self._pulsante_nuovo.setObjectName("apri_giornata")
        self._pulsante_nuovo.setCursor(Qt.PointingHandCursor)
        self._pulsante_nuovo.clicked.connect(self._nuovo_rapporto)
        layout.addWidget(self._pulsante_nuovo)

        nota_nuovo = QLabel("Crea il documento Word del turno corrente e lo apre nell'editor.")
        nota_nuovo.setObjectName("testo_supporto_rapporto")
        nota_nuovo.setWordWrap(True)
        layout.addWidget(nota_nuovo)

        layout.addSpacing(6)
        separatore = QFrame()
        separatore.setObjectName("separatore_azioni_rapporto")
        layout.addWidget(separatore)
        layout.addSpacing(6)

        self._pulsante_archivio = QPushButton("Archivio rapporti  ›")
        self._pulsante_archivio.setObjectName("azione_laterale_rapporto")
        self._pulsante_archivio.setCursor(Qt.PointingHandCursor)
        self._pulsante_archivio.clicked.connect(self._apri_archivio)
        layout.addWidget(self._pulsante_archivio)

        self._pulsante_archivia = QPushButton("Archivia giornata...")
        self._pulsante_archivia.setObjectName("azione_laterale_rapporto")
        self._pulsante_archivia.setCursor(Qt.PointingHandCursor)
        self._pulsante_archivia.clicked.connect(self._archivia)
        layout.addWidget(self._pulsante_archivia)

        nota_archivio = QLabel(
            "L'archiviazione resta manuale e richiede che tutti i rapporti della data siano chiusi."
        )
        nota_archivio.setObjectName("testo_supporto_rapporto")
        nota_archivio.setWordWrap(True)
        layout.addWidget(nota_archivio)
        layout.addStretch()
        return pannello


    def _svuota_elenco(self):
        while self._layout_righe.count():
            item = self._layout_righe.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def _aggiorna_elenco(self):
        """Documentazione della versione portfolio."""
        self._svuota_elenco()

        cartella = _cartella_rapporti()
        testo_ricerca = self._campo_ricerca.text()
        non_archiviati = rapporti_non_archiviati(cartella, testo_ricerca)
        if testo_ricerca.strip():
            rapporti = non_archiviati
            self._titolo_elenco.setText("RISULTATI RICERCA")
        else:
            oggi = datetime.now().strftime("%d-%m-%Y")
            rapporti = [r for r in non_archiviati if r["data_turno"] == oggi]
            self._titolo_elenco.setText("RAPPORTI DI OGGI")

        quanti = len(rapporti)
        self._conteggio_rapporti.setText("1 rapporto" if quanti == 1 else f"{quanti} rapporti")

        if not rapporti:
            self._layout_righe.addWidget(self._crea_stato_vuoto(bool(testo_ricerca.strip())))
        else:
            for rapporto in rapporti:
                self._layout_righe.addWidget(self._crea_riga(rapporto))

        self._layout_righe.addStretch()

    def _crea_stato_vuoto(self, ricerca_attiva: bool) -> QWidget:
        riquadro = QFrame()
        riquadro.setObjectName("stato_vuoto_rapporti")
        layout = QVBoxLayout(riquadro)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(6)

        titolo = QLabel("Nessun risultato" if ricerca_attiva else "Nessun rapporto per oggi")
        titolo.setObjectName("titolo_stato_vuoto")
        titolo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titolo)

        testo = QLabel(
            "Prova a modificare i termini della ricerca."
            if ricerca_attiva
            else "Crea il primo rapporto del turno con il comando a destra."
        )
        testo.setObjectName("testo_stato_vuoto")
        testo.setAlignment(Qt.AlignCenter)
        testo.setWordWrap(True)
        layout.addWidget(testo)
        return riquadro

    def _apri_archivio(self):
        cartella = _cartella_rapporti()
        if not cartella:
            QMessageBox.warning(
                self, "Cartella non configurata",
                "La cartella \"Rapporti Giornalieri\" non è configurata o non è "
                "raggiungibile. Configurala nelle Impostazioni.",
            )
            return

        dialogo = DialogoArchivioRapporti(self, cartella, self._apri_per_modifica, self._anteprima_pdf)
        dialogo.exec()
        self._aggiorna_elenco()

    def _crea_riga(self, rapporto: dict) -> QWidget:
        riga = QFrame()
        riga.setObjectName("card_rapporto")
        riga.setProperty("stato", "aperto" if rapporto["stato"] == STATO_APERTO else "chiuso")
        layout_card = QVBoxLayout(riga)
        layout_card.setContentsMargins(14, 12, 14, 12)
        layout_card.setSpacing(9)

        intestazione = QHBoxLayout()
        intestazione.setContentsMargins(0, 0, 0, 0)
        intestazione.setSpacing(14)
        intestazione.addWidget(_IconaRapportoFotografica())

        contenitore_testi = QWidget()
        contenitore_testi.setObjectName("testi_card_rapporto")
        layout_testo = QVBoxLayout(contenitore_testi)
        layout_testo.setContentsMargins(0, 2, 0, 2)
        layout_testo.setSpacing(5)
        titolo = QLabel(f"{rapporto['operatore_nome']} {rapporto['operatore_cognome']}")
        titolo.setObjectName("operatore_rapporto")
        titolo.setWordWrap(True)
        layout_testo.addWidget(titolo)

        dettaglio = QLabel(
            f"Data {rapporto['data_turno']}   ·   Turno {rapporto['ora_inizio']} - {rapporto['ora_fine']}"
        )
        dettaglio.setObjectName("metadati_rapporto")
        dettaglio.setWordWrap(True)
        layout_testo.addWidget(dettaglio)
        intestazione.addWidget(contenitore_testi, stretch=1)

        stato_aperto = rapporto["stato"] == STATO_APERTO
        stato = QLabel("APERTO" if stato_aperto else "CHIUSO")
        stato.setObjectName("stato_rapporto")
        stato.setProperty("stato", "aperto" if stato_aperto else "chiuso")
        stato.setAlignment(Qt.AlignCenter)
        intestazione.addWidget(stato, alignment=Qt.AlignTop)
        layout_card.addLayout(intestazione)

        contenitore_azioni = QWidget()
        contenitore_azioni.setObjectName("azioni_card_rapporto")
        azioni = QHBoxLayout(contenitore_azioni)
        azioni.setContentsMargins(72, 0, 0, 0)
        azioni.setSpacing(7)

        pulsante_apri = QPushButton("Apri per modifica")
        pulsante_apri.setProperty("ruolo", "primaria")
        pulsante_apri.setCursor(Qt.PointingHandCursor)
        pulsante_apri.clicked.connect(lambda: self._apri_per_modifica(rapporto))
        azioni.addWidget(pulsante_apri)

        pulsante_correggi = QPushButton("Modifica dati")
        pulsante_correggi.setCursor(Qt.PointingHandCursor)
        pulsante_correggi.clicked.connect(lambda: self._modifica_dati_rapporto(rapporto))
        azioni.addWidget(pulsante_correggi)

        pulsante_anteprima = QPushButton("Anteprima PDF")
        pulsante_anteprima.setCursor(Qt.PointingHandCursor)
        pulsante_anteprima.clicked.connect(lambda: self._anteprima_pdf(rapporto))
        azioni.addWidget(pulsante_anteprima)

        if stato_aperto:
            pulsante_chiudi = QPushButton("Salva e chiudi")
            pulsante_chiudi.setProperty("ruolo", "chiusura")
            pulsante_chiudi.setCursor(Qt.PointingHandCursor)
            pulsante_chiudi.clicked.connect(lambda: self.salva_e_chiudi_rapporto(rapporto["id"]))
            azioni.addWidget(pulsante_chiudi)

        azioni.addStretch()
        layout_card.addWidget(riga_scorrevole(contenitore_azioni))

        return riga

    def _percorso_file(self, rapporto: dict) -> Path:
        return Path(rapporto["cartella_corrente"]) / rapporto["nome_file"]


    def _nuovo_rapporto(self):
        cartella = _cartella_rapporti()
        if not cartella:
            QMessageBox.warning(
                self, "Cartella non configurata",
                "La cartella \"Rapporti Giornalieri\" non è configurata o non è "
                "raggiungibile. Configurala nelle Impostazioni.",
            )
            return

        finestra = _DialogoNuovoRapporto(self)
        if finestra.exec() != QDialog.Accepted:
            return

        nome = finestra.campo_nome.text().strip()
        cognome = finestra.campo_cognome.text().strip()


        ora_inizio = testo_orario(finestra.campo_ora_inizio)
        ora_fine = testo_orario(finestra.campo_ora_fine)
        if not (nome and cognome):
            QMessageBox.warning(self, "Dati mancanti", "Nome e cognome dell'operatore sono obbligatori.")
            return


        risolto = risolvi_operatore_nome_cognome_confermato(self, nome, cognome)
        if risolto is None:
            return
        nome, cognome, operatore_id = risolto

        data_turno = datetime.now().strftime("%d-%m-%Y")

        if rapporto_esistente(data_turno, nome, cognome, ora_inizio, ora_fine):
            QMessageBox.warning(
                self, "Rapporto già esistente",
                "Esiste già un rapporto per questa data, operatore e turno. "
                "Usa \"Apri per modifica\" dall'elenco per correggerlo.",
            )
            return

        nome_file = formatta_nome_file(data_turno, ora_inizio, ora_fine, nome, cognome)
        percorso_destinazione = Path(cartella) / nome_file
        orario_testo = f"{ora_inizio} - {ora_fine}"

        try:
            crea_documento_da_modello(
                percorso_modello(cartella), percorso_destinazione,
                operatore_nome=nome, operatore_cognome=cognome,
                data_turno=data_turno, orario_testo=orario_testo,
            )
        except FileNotFoundError as errore:
            QMessageBox.warning(self, "Modello non trovato", str(errore))
            return
        except OSError as errore:
            QMessageBox.warning(self, "Errore nella creazione del file", str(errore))
            return

        id_rapporto = crea_rapporto(
            data_turno, nome, cognome, ora_inizio, ora_fine,
            nome_file, cartella, datetime.now().isoformat(timespec="seconds"),
            operatore_id=operatore_id,
        )

        self._apri_nell_editor(
            id_rapporto, percorso_destinazione,
            operatore=f"{nome} {cognome}", data_turno=data_turno, orario=orario_testo,
            nome=nome, cognome=cognome, ora_inizio=ora_inizio, ora_fine=ora_fine,
        )

    def apri_rapporto(self, rapporto: dict):
        """Documentazione della versione portfolio."""
        self._apri_per_modifica(rapporto)

    def consulta_rapporto(self, rapporto: dict, al_ritorno):
        """Documentazione della versione portfolio."""
        percorso = self._percorso_file(rapporto)
        if not percorso.is_file():
            QMessageBox.warning(
                self, "File non trovato",
                f"Il file del rapporto non si trova più in:\n{percorso}",
            )
            return

        self._finestra_principale.mostra_consultazione_rapporto(
            percorso,
            operatore=f"{rapporto['operatore_nome']} {rapporto['operatore_cognome']}",
            data_turno=rapporto["data_turno"],
            orario=f"{rapporto['ora_inizio']} - {rapporto['ora_fine']}",
            al_ritorno=al_ritorno,
        )

    def _apri_per_modifica(self, rapporto: dict):
        percorso = self._percorso_file(rapporto)
        if not percorso.is_file():
            QMessageBox.warning(
                self, "File non trovato",
                f"Il file del rapporto non si trova più in:\n{percorso}",
            )
            return

        if rapporto["stato"] != STATO_APERTO:
            segna_aperto(rapporto["id"], datetime.now().isoformat(timespec="seconds"))

        self._apri_nell_editor(
            rapporto["id"], percorso,
            operatore=f"{rapporto['operatore_nome']} {rapporto['operatore_cognome']}",
            data_turno=rapporto["data_turno"],
            orario=f"{rapporto['ora_inizio']} - {rapporto['ora_fine']}",
            nome=rapporto["operatore_nome"], cognome=rapporto["operatore_cognome"],
            ora_inizio=rapporto["ora_inizio"], ora_fine=rapporto["ora_fine"],
        )

    def _apri_nell_editor(
        self, id_rapporto: int, percorso: Path,
        operatore: str, data_turno: str, orario: str,
        nome: str, cognome: str, ora_inizio: str, ora_fine: str,
    ):
        etichetta_bar = f"{nome} {cognome} · {ora_inizio}/{ora_fine}"
        self._finestra_principale.mostra_documento_word(
            id_rapporto, percorso, operatore, data_turno, orario, etichetta_bar,
        )

    def _modifica_dati_rapporto(self, rapporto: dict):
        """Documentazione della versione portfolio."""
        finestra = _DialogoModificaRapporto(self, rapporto)
        if finestra.exec() != QDialog.Accepted:
            return

        nome = finestra.campo_nome.text().strip()
        cognome = finestra.campo_cognome.text().strip()
        ora_inizio = testo_orario(finestra.campo_ora_inizio)
        ora_fine = testo_orario(finestra.campo_ora_fine)
        if not (nome and cognome):
            QMessageBox.warning(self, "Dati mancanti", "Nome e cognome dell'operatore sono obbligatori.")
            return

        risolto = risolvi_operatore_nome_cognome_confermato(self, nome, cognome)
        if risolto is None:
            return
        nome, cognome, operatore_id = risolto

        id_rapporto = rapporto["id"]
        data_turno = rapporto["data_turno"]

        if rapporto_esistente(data_turno, nome, cognome, ora_inizio, ora_fine, escludi_id=id_rapporto):
            QMessageBox.warning(
                self, "Rapporto già esistente",
                "Esiste già un altro rapporto per questa data, operatore e turno.",
            )
            return

        percorso_attuale = self._percorso_file(rapporto)
        if not percorso_attuale.is_file():
            QMessageBox.warning(
                self, "File non trovato",
                f"Il file del rapporto non si trova più in:\n{percorso_attuale}\n\n"
                "Impossibile applicare la correzione.",
            )
            return

        nuovo_nome_file = formatta_nome_file(data_turno, ora_inizio, ora_fine, nome, cognome)
        nuovo_percorso = percorso_attuale.parent / nuovo_nome_file

        if nuovo_percorso != percorso_attuale:
            try:
                percorso_attuale.rename(nuovo_percorso)
            except OSError as errore:
                QMessageBox.warning(
                    self, "Errore nella rinomina del file",
                    f"Non è stato possibile rinominare il file: {errore}",
                )
                return

        orario_testo = f"{ora_inizio} - {ora_fine}"
        try:
            aggiorna_campi_automatici(nuovo_percorso, nome, cognome, orario_testo)
        except Exception as errore:
            QMessageBox.warning(
                self, "Errore nella correzione del documento",
                f"Il file è stato rinominato ma non è stato possibile aggiornare i campi "
                f"al suo interno: {errore}\n\nRiprova con \"Modifica dati\".",
            )

        modifica_dati_operatore(
            id_rapporto, nome, cognome, ora_inizio, ora_fine, nuovo_nome_file,
            datetime.now().isoformat(timespec="seconds"), operatore_id=operatore_id,
        )

        etichetta_bar = f"{nome} {cognome} · {ora_inizio}/{ora_fine}"
        self._finestra_principale.aggiorna_metadati_documento_word(
            id_rapporto, nuovo_percorso, f"{nome} {cognome}", orario_testo, etichetta_bar,
        )

        self._aggiorna_elenco()

    def salva_e_chiudi_rapporto(self, id_rapporto: int):
        """Documentazione della versione portfolio."""
        if not self._finestra_principale.chiudi_documento_word(id_rapporto):
            return
        segna_chiuso(id_rapporto, datetime.now().isoformat(timespec="seconds"))
        self._aggiorna_elenco()

    def _anteprima_pdf(self, rapporto: dict):
        percorso = self._percorso_file(rapporto)
        if not percorso.is_file():
            QMessageBox.warning(
                self, "File non trovato",
                f"Il file del rapporto non si trova più in:\n{percorso}",
            )
            return

        percorso_pdf = Path(tempfile.gettempdir()) / f"{percorso.stem}.pdf"

        try:
            esporta_pdf(percorso, percorso_pdf)
        except Exception as errore:
            QMessageBox.warning(
                self, "Anteprima non disponibile",
                f"Non è stato possibile generare l'anteprima PDF: {errore}",
            )
            return

        self._mostra_pdf(percorso_pdf, rapporto)

    def _mostra_pdf(self, percorso_pdf: Path, rapporto: dict):
        from PySide6.QtPdf import QPdfDocument
        from PySide6.QtPdfWidgets import QPdfView

        finestra = QDialog(self)
        finestra.setObjectName("anteprima_pdf_rapporto")
        finestra.setWindowTitle(f"Anteprima — {rapporto['nome_file']}")
        finestra.resize(700, 900)
        layout = QVBoxLayout(finestra)
        layout.setContentsMargins(12, 12, 12, 12)

        documento_pdf = QPdfDocument(finestra)
        documento_pdf.load(str(percorso_pdf))

        visore = QPdfView(finestra)
        visore.setDocument(documento_pdf)
        visore.setPageMode(QPdfView.PageMode.MultiPage)
        layout.addWidget(visore)

        finestra.exec()

    def _archivia(self):
        cartella = _cartella_rapporti()
        if not cartella:
            QMessageBox.warning(
                self, "Cartella non configurata",
                "La cartella \"Rapporti Giornalieri\" non è configurata o non è "
                "raggiungibile. Configurala nelle Impostazioni.",
            )
            return

        finestra = _DialogoArchiviazione(self)
        if finestra.exec() != QDialog.Accepted:
            return

        data_turno = finestra.campo_data.text().strip()
        aperti = rapporti_aperti_di(data_turno)
        if aperti:
            elenco = "\n".join(
                f"    • {r['operatore_nome']} {r['operatore_cognome']} "
                f"({r['ora_inizio']} - {r['ora_fine']})"
                for r in aperti
            )
            QMessageBox.warning(
                self, "Rapporti ancora aperti",
                f"Prima di archiviare i rapporti del {data_turno} devi salvarli e "
                f"chiuderli tutti. Risultano ancora aperti:\n\n{elenco}\n\n"
                "Chiudili dall'elenco (\"Salva e chiudi\") e riprova.",
            )
            return

        rapporti = [r for r in tutti_i_rapporti() if r["data_turno"] == data_turno]
        if not rapporti:
            QMessageBox.information(self, "Nessun rapporto", f"Nessun rapporto trovato per il {data_turno}.")
            return

        destinazione = cartella_archivio(cartella, data_turno)
        destinazione.mkdir(parents=True, exist_ok=True)

        spostati, mancanti = 0, []
        for rapporto in rapporti:
            origine = self._percorso_file(rapporto)
            if not origine.is_file():
                mancanti.append(rapporto["nome_file"])
                continue
            origine.rename(destinazione / rapporto["nome_file"])
            aggiorna_cartella(rapporto["id"], str(destinazione))
            spostati += 1

        self._aggiorna_elenco()

        messaggio = f"Archiviati {spostati} rapporti in:\n{destinazione}"
        if mancanti:
            messaggio += "\n\nNon trovati sul disco (non spostati):\n" + "\n".join(mancanti)
        QMessageBox.information(self, "Archiviazione completata", messaggio)
