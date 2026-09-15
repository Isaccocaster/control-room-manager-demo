"""Documentazione della versione portfolio."""
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QPoint, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QBoxLayout,
    QDialog,
    QDialogButtonBox,
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

from config.impostazioni import CHIAVE_PASSAGGIO_CONSEGNE, cartella_esiste, carica_impostazioni
from data.passaggio_consegne import (
    aggiungi_comunicazione,
    archivia_comunicazione,
    comunicazione as leggi_comunicazione,
    conteggi_attivi,
    imposta_fissato,
    mese_di_riferimento,
    modifica_comunicazione,
    ottieni_comunicazioni,
    storico_visibile,
)
from documents.excel.storico_passaggi import genera_prospetto_mese, nome_file
from ui.comune.icone import SIMBOLO_STORICO, applica_icona_pulsante, pixmap_simbolo
from ui.passaggio_consegne.stile import FOGLIO_DI_STILE_PASSAGGIO
from ui.tema import TESTO_ATTENUATO

LARGHEZZA_NOTEPAD = 420
ALTEZZA_NOTEPAD = 520
MARGINE_NOTEPAD = 16
PERCORSO_FOTO_PASSAGGIO = (
    Path(__file__).resolve().parents[1] / "assets" / "images" / "demo_passaggio_consegne.jpg"
)


ORO_IMPORTANTE = "#E7BB67"
NAVY_SU_ORO = "#182334"
GRIGIO_NEUTRO = "#C6D3E6"


def icona_priorita(lato: int, colore_disco: str, colore_segno: str) -> QPixmap:
    """Documentazione della versione portfolio."""
    contorno = colore_segno if colore_disco == "none" else "none"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
        f'<circle cx="10" cy="10" r="9" fill="{colore_disco}" '
        f'stroke="{contorno}" stroke-width="1.6"/>'
        f'<rect x="8.85" y="4.6" width="2.3" height="7.1" rx="1.15" fill="{colore_segno}"/>'
        f'<circle cx="10" cy="14.9" r="1.35" fill="{colore_segno}"/>'
        '</svg>'
    )
    pixmap = QPixmap(lato * 2, lato * 2)
    pixmap.fill(Qt.transparent)
    pittore = QPainter(pixmap)
    pittore.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(svg.encode("utf-8")).render(pittore)
    pittore.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap


def testo_badge_importanti(quante: int) -> str:
    """Documentazione della versione portfolio."""
    return f"{quante} " + ("IMPORTANTE" if quante == 1 else "IMPORTANTI")


def testo_badge_normali(quante: int) -> str:
    """Documentazione della versione portfolio."""
    return f"{quante} " + ("PASSAGGIO" if quante == 1 else "PASSAGGI")


class _PillolaImportante(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, testo: str, nome_oggetto: str, lato_icona: int):
        super().__init__()
        self.setObjectName(nome_oggetto)
        self.setAttribute(Qt.WA_StyledBackground, True)

        disposizione = QHBoxLayout(self)
        disposizione.setContentsMargins(0, 0, 0, 0)
        disposizione.setSpacing(5)

        self._icona = QLabel()
        self._icona.setObjectName("icona_priorita_passaggio")
        self._icona.setFixedSize(lato_icona, lato_icona)
        self._icona.setPixmap(icona_priorita(lato_icona, NAVY_SU_ORO, ORO_IMPORTANTE))
        disposizione.addWidget(self._icona, 0, Qt.AlignVCenter)

        self._testo = QLabel(testo)
        self._testo.setObjectName("testo_priorita_passaggio")
        disposizione.addWidget(self._testo, 0, Qt.AlignVCenter)

    def imposta_testo(self, testo: str) -> None:
        self._testo.setText(testo)

    def testo(self) -> str:
        return self._testo.text()


def chip_importante() -> _PillolaImportante:
    """Documentazione della versione portfolio."""
    return _PillolaImportante("IMPORTANTE", "chip_importante_passaggio", 12)


class _IndicatoreConsegne(QWidget):
    """Documentazione della versione portfolio."""

    def __init__(self):
        super().__init__()
        self.setObjectName("indicatore_passaggio_consegne")

        self._disposizione = QBoxLayout(QBoxLayout.LeftToRight, self)
        self._disposizione.setContentsMargins(6, 0, 0, 0)
        self._disposizione.setSpacing(6)


        self._badge_importanti = _PillolaImportante("", "badge_importanti_passaggio", 14)
        self._badge_normali = QLabel()
        self._badge_normali.setObjectName("badge_normali_passaggio")
        self._badge_normali.setAlignment(Qt.AlignCenter)

        for badge in (self._badge_importanti, self._badge_normali):
            badge.hide()
            self._disposizione.addWidget(badge, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self._disposizione.addStretch()

    def aggiorna(self, conteggi: dict) -> None:
        """Documentazione della versione portfolio."""
        fissate, normali = conteggi["fissate"], conteggi["normali"]
        self._badge_importanti.imposta_testo(testo_badge_importanti(fissate) if fissate else "")
        self._badge_importanti.setVisible(bool(fissate))
        self._badge_normali.setText(testo_badge_normali(normali) if normali else "")
        self._badge_normali.setVisible(bool(normali))

    def imposta_impilato(self, impilato: bool) -> None:
        """Documentazione della versione portfolio."""
        self._disposizione.setDirection(
            QBoxLayout.TopToBottom if impilato else QBoxLayout.LeftToRight
        )


        margine_sinistro = 0 if impilato else 6
        self._disposizione.setContentsMargins(margine_sinistro, 0, 0, 0)
        self._disposizione.setSpacing(4 if impilato else 6)

    def testo(self) -> str:
        """Documentazione della versione portfolio."""
        parti = (self._badge_importanti.testo(), self._badge_normali.text())
        return " · ".join(parte for parte in parti if parte)


class _CampoTesto(QLineEdit):
    """Documentazione della versione portfolio."""

    annullato = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.annullato.emit()
        else:
            super().keyPressEvent(event)


class _BarraCliccabile(QFrame):
    cliccata = Signal()

    def mousePressEvent(self, event):
        self.cliccata.emit()
        super().mousePressEvent(event)


class _RigaComunicazione(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, comunicazione: dict, al_modifica, al_elimina, al_inizio_modifica,
                 al_fine_modifica, al_fissa):
        super().__init__()
        self.setObjectName("riga_passaggio")
        self._id = comunicazione["id"]
        self._testo = comunicazione["testo"]
        self._creato_il = comunicazione["creato_il"]
        self._fissato = comunicazione["fissato"]
        self._al_modifica = al_modifica
        self._al_inizio_modifica = al_inizio_modifica
        self._al_fine_modifica = al_fine_modifica


        self.setProperty("fissato", "true" if self._fissato else "false")

        esterno = QVBoxLayout(self)
        esterno.setContentsMargins(4, 4, 4, 4)
        esterno.setSpacing(4)

        if self._fissato:
            esterno.addWidget(chip_importante(), 0, Qt.AlignLeft)

        contenuto = QWidget()
        contenuto.setObjectName("contenuto_riga_passaggio")
        layout = QHBoxLayout(contenuto)
        layout.setContentsMargins(0, 0, 0, 0)
        esterno.addWidget(contenuto)


        self._etichetta = QLabel(f"[{self._creato_il}]  {self._testo}")
        self._etichetta.setObjectName("testo_passaggio")
        self._etichetta.setWordWrap(True)
        layout.addWidget(self._etichetta, stretch=1)

        self._campo_modifica = _CampoTesto(self._testo)
        self._campo_modifica.setObjectName("modifica_comunicazione_passaggio")
        self._campo_modifica.hide()
        self._campo_modifica.returnPressed.connect(self._conferma_modifica)
        self._campo_modifica.annullato.connect(self._annulla)
        layout.addWidget(self._campo_modifica, stretch=1)


        self._pulsante_fissa = QPushButton()
        self._pulsante_fissa.setObjectName("fissa_passaggio")
        self._pulsante_fissa.setFixedWidth(28)
        self._pulsante_fissa.setIconSize(QSize(14, 14))
        self._pulsante_fissa.setCheckable(True)
        self._pulsante_fissa.setChecked(self._fissato)
        self._aggiorna_pulsante_fissa(self._fissato)


        self._pulsante_fissa.toggled.connect(self._aggiorna_pulsante_fissa)
        self._pulsante_fissa.clicked.connect(lambda: al_fissa(self._id, not self._fissato))
        layout.addWidget(self._pulsante_fissa)

        pulsante_elimina = QPushButton("×")
        pulsante_elimina.setObjectName("archivia_passaggio")
        pulsante_elimina.setFixedWidth(28)
        pulsante_elimina.setToolTip("Togli dal blocco note (resta nello storico)")
        pulsante_elimina.clicked.connect(lambda: al_elimina(self._id, self._testo))
        layout.addWidget(pulsante_elimina)

    def _aggiorna_pulsante_fissa(self, acceso: bool):
        self._pulsante_fissa.setIcon(QIcon(
            icona_priorita(14, NAVY_SU_ORO if acceso else "none",
                           ORO_IMPORTANTE if acceso else GRIGIO_NEUTRO)
        ))
        self._pulsante_fissa.setToolTip(
            "Togli da IMPORTANTI" if acceso else "Segna come IMPORTANTE"
        )

    def mouseDoubleClickEvent(self, event):
        self._al_inizio_modifica(self)
        self._etichetta.hide()
        self._campo_modifica.setText(self._testo)
        self._campo_modifica.show()
        self._campo_modifica.setFocus()
        self._campo_modifica.selectAll()

    def annulla_modifica(self):
        self._campo_modifica.hide()
        self._etichetta.show()

    def _annulla(self):
        self.annulla_modifica()
        self._al_fine_modifica()

    def _conferma_modifica(self):
        nuovo_testo = self._campo_modifica.text().strip()
        self.annulla_modifica()
        self._al_fine_modifica()
        if nuovo_testo and nuovo_testo != self._testo:
            self._al_modifica(self._id, nuovo_testo)


class _DialogoDettaglio(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, id_comunicazione: int):
        super().__init__(parent)
        self.setObjectName("dettaglio_passaggio_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_PASSAGGIO)
        self.setWindowTitle("Dettaglio comunicazione")
        self.setMinimumWidth(460)

        dati = leggi_comunicazione(id_comunicazione)
        layout = QVBoxLayout(self)

        if dati is None:
            layout.addWidget(QLabel("Comunicazione non trovata."))
        else:
            testo = QLabel(dati["testo"])
            testo.setObjectName("testo_dettaglio_passaggio")
            testo.setWordWrap(True)
            layout.addWidget(testo)


            if dati["fissato"]:
                layout.addWidget(chip_importante(), 0, Qt.AlignLeft)

            righe = [f"Scritta il {dati['creato_il']}"]
            if dati["archiviata"]:
                righe.append(f"Tolta dal blocco note il {dati['archiviato_il']}")
            else:
                righe.append("Presente nel blocco note")

            dettaglio = QLabel("\n".join(righe))
            dettaglio.setObjectName("metadati_passaggio")
            dettaglio.setWordWrap(True)
            layout.addWidget(dettaglio)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Close)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)


class _DialogoStorico(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("storico_passaggio_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_PASSAGGIO)
        self.setWindowTitle("Storico Passaggi di Consegne")
        self.setMinimumSize(560, 520)

        layout = QVBoxLayout(self)

        area = QScrollArea()
        area.setObjectName("elenco_storico_passaggio")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        contenuto = QWidget()
        contenuto.setObjectName("contenuto_storico_passaggio")
        self._layout_righe = QVBoxLayout(contenuto)
        self._layout_righe.setContentsMargins(0, 0, 0, 0)
        self._layout_righe.setSpacing(6)
        area.setWidget(contenuto)
        layout.addWidget(area, stretch=1)

        tutte = storico_visibile()
        fissate = [c for c in tutte if c["fissato"]]

        self._sezione(f"PASSAGGI IMPORTANTI ({len(fissate)})", con_priorita=True)
        if not fissate:
            self._messaggio("Nessun passaggio fissato in alto.")
        for c in fissate:
            self._layout_righe.addWidget(self._riga(c))

        self._sezione(f"PASSAGGI RECENTI / STORICO ({len(tutte)})", con_storico=True)
        if not tutte:
            self._messaggio("Nessuna comunicazione registrata.")
        for c in tutte:
            self._layout_righe.addWidget(self._riga(c))

        self._layout_righe.addStretch()

        nota = QLabel(
            "Questo elenco mostra il mese corrente e tutto cio' che e' ancora nel "
            "blocco note. I mesi precedenti si consultano dai file Excel mensili "
            "nella cartella \"Passaggio di Consegne\"."
        )
        nota.setObjectName("nota_storico_passaggio")
        nota.setWordWrap(True)
        layout.addWidget(nota)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Close)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def _sezione(self, titolo: str, con_priorita: bool = False, con_storico: bool = False):
        etichetta = QLabel(titolo)
        etichetta.setObjectName("sezione_storico_passaggio")
        if not con_priorita and not con_storico:
            self._layout_righe.addWidget(etichetta)
            return


        riga = QWidget()
        riga.setObjectName("intestazione_sezione_storico_passaggio")
        disposizione = QHBoxLayout(riga)
        disposizione.setContentsMargins(0, 10, 0, 0)
        disposizione.setSpacing(6)

        disco = QLabel()
        disco.setObjectName(
            "icona_priorita_passaggio" if con_priorita else "icona_storico_passaggio"
        )
        disco.setFixedSize(14, 14)
        disco.setPixmap(
            icona_priorita(14, ORO_IMPORTANTE, NAVY_SU_ORO)
            if con_priorita else pixmap_simbolo(SIMBOLO_STORICO, 14, "#9FC8F2")
        )
        disposizione.addWidget(disco, 0, Qt.AlignVCenter)

        etichetta.setStyleSheet("padding-top: 0px;")
        disposizione.addWidget(etichetta, 0, Qt.AlignVCenter)
        disposizione.addStretch()
        self._layout_righe.addWidget(riga)

    def _messaggio(self, testo: str):
        etichetta = QLabel(testo)
        etichetta.setObjectName("stato_vuoto_storico_passaggio")
        self._layout_righe.addWidget(etichetta)

    def _riga(self, comunicazione: dict) -> QWidget:
        riga = _BarraCliccabile()
        riga.setObjectName("riga_storico_passaggio")
        riga.setProperty("fissato", "true" if comunicazione["fissato"] else "false")
        riga.setCursor(Qt.PointingHandCursor)
        riga.setToolTip("Apri il dettaglio")
        riga.cliccata.connect(lambda _=None, i=comunicazione["id"]: _DialogoDettaglio(self, i).exec())

        layout = QVBoxLayout(riga)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)


        if comunicazione["fissato"]:
            layout.addWidget(chip_importante(), 0, Qt.AlignLeft)

        testo = QLabel(comunicazione["testo"])
        testo.setObjectName("testo_storico_passaggio")
        testo.setWordWrap(True)
        layout.addWidget(testo)

        stato = "archiviata" if comunicazione["archiviata"] else "nel blocco note"
        dettaglio = QLabel(f"{comunicazione['creato_il']}   —   {stato}")
        dettaglio.setObjectName("metadati_passaggio")
        layout.addWidget(dettaglio)

        return riga


class _NotepadComunicazioni(QFrame):
    """Documentazione della versione portfolio."""

    def __init__(self, contenitore_finestra: QWidget, al_cambiamento, al_chiudi):
        super().__init__(contenitore_finestra)
        self.setObjectName("notepad_passaggio_consegne")
        self.setStyleSheet(FOGLIO_DI_STILE_PASSAGGIO)
        self.setFixedSize(LARGHEZZA_NOTEPAD, ALTEZZA_NOTEPAD)
        self._foto_sfondo = QPixmap(str(PERCORSO_FOTO_PASSAGGIO))

        self._al_cambiamento = al_cambiamento
        self._riga_in_modifica = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        intestazione = QHBoxLayout()
        titolo = QLabel("PASSAGGIO DI CONSEGNE")
        titolo.setObjectName("titolo_notepad_passaggio")
        intestazione.addWidget(titolo)
        intestazione.addStretch()


        pulsante_storico = QPushButton("Storico")
        pulsante_storico.setObjectName("storico_passaggio")
        applica_icona_pulsante(pulsante_storico, SIMBOLO_STORICO)
        pulsante_storico.setToolTip("Tutte le comunicazioni, comprese quelle archiviate")
        pulsante_storico.clicked.connect(self._apri_storico)
        intestazione.addWidget(pulsante_storico)

        pulsante_riduci = QPushButton("▲")
        pulsante_riduci.setObjectName("riduci_passaggio")
        pulsante_riduci.setFixedWidth(28)
        pulsante_riduci.setToolTip("Riduci")
        pulsante_riduci.clicked.connect(al_chiudi)
        intestazione.addWidget(pulsante_riduci)

        layout.addLayout(intestazione)

        self._area_scorrevole = QScrollArea()
        self._area_scorrevole.setObjectName("elenco_passaggio")
        self._area_scorrevole.setWidgetResizable(True)
        self._area_scorrevole.setFrameShape(QFrame.NoFrame)

        self._contenitore_righe = QWidget()
        self._contenitore_righe.setObjectName("contenitore_righe_passaggio")
        self._layout_righe = QVBoxLayout(self._contenitore_righe)
        self._layout_righe.setContentsMargins(0, 0, 0, 0)
        self._area_scorrevole.setWidget(self._contenitore_righe)

        layout.addWidget(self._area_scorrevole, stretch=1)

        riga_inserimento = QHBoxLayout()

        self._campo_nuova = QLineEdit()
        self._campo_nuova.setObjectName("nuova_comunicazione_passaggio")
        self._campo_nuova.setPlaceholderText("Scrivi una nuova comunicazione...")
        self._campo_nuova.returnPressed.connect(self._aggiungi)
        riga_inserimento.addWidget(self._campo_nuova, stretch=1)

        pulsante_aggiungi = QPushButton("Aggiungi")
        pulsante_aggiungi.setObjectName("aggiungi_passaggio")
        pulsante_aggiungi.clicked.connect(self._aggiungi)
        riga_inserimento.addWidget(pulsante_aggiungi)

        layout.addLayout(riga_inserimento)

        self.aggiorna_elenco()

    def paintEvent(self, event):
        """Documentazione della versione portfolio."""
        pittore = QPainter(self)
        pittore.setRenderHint(QPainter.Antialiasing)
        rettangolo = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        sagoma = QPainterPath()
        sagoma.addRoundedRect(rettangolo, 14, 14)
        pittore.setClipPath(sagoma)
        if not self._foto_sfondo.isNull():
            foto = self._foto_sfondo.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            pittore.drawPixmap(
                QPoint((self.width() - foto.width()) // 2, (self.height() - foto.height()) // 2),
                foto,
            )
        else:
            pittore.fillPath(sagoma, QColor("#0B1E35"))
        pittore.fillPath(sagoma, QColor(4, 18, 36, 214))
        pittore.setClipping(False)
        pittore.setPen(QPen(QColor(87, 134, 182, 150), 1))
        pittore.drawPath(sagoma)

    def mostra_sopra(self, riferimento: QWidget):
        posizione = riferimento.mapTo(self.parentWidget(), QPoint(MARGINE_NOTEPAD, 0))
        y = posizione.y() - self.height()
        self.move(posizione.x(), y)
        self.raise_()
        self.show()


        self.repaint()
        for figlio in self._contenitore_righe.findChildren(QWidget):
            figlio.repaint()

    def aggiorna_elenco(self) -> int:
        """Documentazione della versione portfolio."""
        self._riga_in_modifica = None
        comunicazioni = ottieni_comunicazioni()

        while self._layout_righe.count():
            item = self._layout_righe.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

        if not comunicazioni:
            segnaposto = QLabel("Nessuna comunicazione al momento.")
            segnaposto.setObjectName("stato_vuoto_passaggio")
            self._layout_righe.addWidget(segnaposto)
        else:
            for comunicazione in comunicazioni:
                riga = _RigaComunicazione(
                    comunicazione, self._modifica, self._chiedi_archiviazione,
                    self._inizio_modifica, self._fine_modifica, self._fissa,
                )
                self._layout_righe.addWidget(riga)

        self._layout_righe.addStretch()
        return len(comunicazioni)

    def _inizio_modifica(self, riga: _RigaComunicazione):
        if self._riga_in_modifica is not None and self._riga_in_modifica is not riga:
            self._riga_in_modifica.annulla_modifica()
        self._riga_in_modifica = riga

    def _fine_modifica(self):
        self._riga_in_modifica = None

    def _aggiungi(self):
        aggiungi_comunicazione(self._campo_nuova.text())
        self._campo_nuova.clear()
        self.aggiorna_elenco()


        self._al_cambiamento()

    def _modifica(self, id_comunicazione: int, nuovo_testo: str):
        modifica_comunicazione(id_comunicazione, nuovo_testo)
        self.aggiorna_elenco()
        self._al_cambiamento(id_comunicazione)

    def _chiedi_archiviazione(self, id_comunicazione: int, testo: str):
        """Documentazione della versione portfolio."""
        risposta = QMessageBox.question(
            self,
            "Togliere questa comunicazione dal blocco note?",
            f'"{testo}"\n\nResterà consultabile nello storico.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if risposta == QMessageBox.Yes:
            archivia_comunicazione(id_comunicazione)
            self.aggiorna_elenco()
            self._al_cambiamento(id_comunicazione)

    def _fissa(self, id_comunicazione: int, fissato: bool):
        """Documentazione della versione portfolio."""
        imposta_fissato(id_comunicazione, fissato)
        self.aggiorna_elenco()
        self._al_cambiamento(id_comunicazione)

    def _apri_storico(self):
        _DialogoStorico(self).exec()


class PannelloPassaggioConsegne(QWidget):
    """Documentazione della versione portfolio."""

    def __init__(self, contenitore_finestra: QWidget):
        super().__init__()
        self.setObjectName("pannello_passaggio_consegne")
        self.setStyleSheet(FOGLIO_DI_STILE_PASSAGGIO)
        self._espanso = False
        self._avviso_cartella_mostrato = False


        self._variante_sidebar = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._crea_barra())

        self._notepad = _NotepadComunicazioni(contenitore_finestra, self._al_cambiamento_notepad, self._riduci)
        self._notepad.hide()

        self._aggiorna_indicatore()

    def _al_cambiamento_notepad(self, id_comunicazione: int | None = None):
        """Documentazione della versione portfolio."""
        self._aggiorna_indicatore()
        self._rigenera_file_del_mese(id_comunicazione)
        self._forza_relayout()

    def _rigenera_file_del_mese(self, id_comunicazione: int | None):
        """Documentazione della versione portfolio."""
        cartella = carica_impostazioni().get(CHIAVE_PASSAGGIO_CONSEGNE, "")
        if not cartella_esiste(cartella):
            if not self._avviso_cartella_mostrato:
                self._avviso_cartella_mostrato = True
                QMessageBox.warning(
                    self,
                    "Cartella non configurata",
                    "Le comunicazioni vengono salvate regolarmente, ma non è possibile "
                    "creare il file Excel mensile dello storico perché la cartella "
                    "\"Passaggio di Consegne\" non è configurata o non è raggiungibile.\n\n"
                    "Configurala nelle Impostazioni.",
                )
            return

        if id_comunicazione is None:
            adesso = datetime.now()
            anno, mese = adesso.year, adesso.month
        else:
            dati = leggi_comunicazione(id_comunicazione)
            if dati is None:
                return
            anno, mese = mese_di_riferimento(dati["creato_il"])

        try:
            genera_prospetto_mese(anno, mese, cartella)
        except OSError as errore:
            QMessageBox.warning(
                self,
                "File dello storico non aggiornato",
                f"La comunicazione è stata salvata, ma non è stato possibile scrivere "
                f"{nome_file(anno, mese)}: {errore}",
            )

    def _crea_barra(self) -> QWidget:
        barra = _BarraCliccabile()
        barra.setObjectName("barra_passaggio_consegne")
        barra.setProperty("variante", "barra")
        barra.setCursor(Qt.PointingHandCursor)
        barra.cliccata.connect(self._alterna_espansione)
        self._barra = barra


        self._layout_barra = QVBoxLayout(barra)
        self._layout_barra.setContentsMargins(16, 8, 16, 8)
        self._layout_barra.setSpacing(0)

        self._riga_titolo = QWidget()
        riga = QHBoxLayout(self._riga_titolo)
        riga.setContentsMargins(0, 0, 0, 0)

        self._titolo = QLabel("PASSAGGIO DI CONSEGNE")
        self._titolo.setObjectName("titolo_barra_passaggio")
        riga.addWidget(self._titolo)


        self._indicatore = _IndicatoreConsegne()
        riga.addWidget(self._indicatore)

        riga.addStretch()

        self._freccia = QLabel("▼")
        self._freccia.setObjectName("freccia_passaggio")
        riga.addWidget(self._freccia)

        self._layout_barra.addWidget(self._riga_titolo)
        return barra


    def imposta_variante_sidebar(self, attiva: bool):
        """Documentazione della versione portfolio."""
        if attiva == self._variante_sidebar:
            return
        self._variante_sidebar = attiva

        self._barra.setProperty("variante", "sidebar" if attiva else "barra")
        self._barra.style().unpolish(self._barra)
        self._barra.style().polish(self._barra)

        self._titolo.setWordWrap(attiva)


        self._indicatore.imposta_impilato(attiva)
        layout_riga = self._riga_titolo.layout()
        if attiva:
            layout_riga.removeWidget(self._indicatore)
            self._layout_barra.addWidget(self._indicatore)
            self._layout_barra.setSpacing(4)
        else:
            self._layout_barra.removeWidget(self._indicatore)
            layout_riga.insertWidget(1, self._indicatore)
            self._layout_barra.setSpacing(0)

        self._aggiorna_indicatore()

    def chiudi_blocco_note(self):
        """Documentazione della versione portfolio."""
        self._riduci()

    def _alterna_espansione(self):
        self._espanso = not self._espanso
        if self._espanso:
            self._notepad.aggiorna_elenco()
            self._notepad.mostra_sopra(self._barra)
        else:
            self._notepad.hide()
        self._freccia.setText("▲" if self._espanso else "▼")
        self._aggiorna_indicatore()
        self._forza_relayout()

    def _riduci(self):
        """Documentazione della versione portfolio."""
        if self._espanso:
            self._alterna_espansione()

    def _aggiorna_indicatore(self):
        """Documentazione della versione portfolio."""
        conteggi = conteggi_attivi()
        self._indicatore.aggiorna(conteggi)
        self._indicatore.setToolTip(self._descrizione_indicatore(conteggi))


        self._indicatore.setVisible(
            (not self._espanso) and bool(conteggi["fissate"] or conteggi["normali"])
        )

    def testo_indicatore(self) -> str:
        """Documentazione della versione portfolio."""
        return self._indicatore.testo()

    @staticmethod
    def _descrizione_indicatore(conteggi: dict) -> str:
        parti = []
        if conteggi["fissate"]:
            quante = conteggi["fissate"]
            parti.append(f"{quante} " + ("importante fissata in alto" if quante == 1
                                         else "importanti fissate in alto"))
        if conteggi["normali"]:
            parti.append(f"{conteggi['normali']} da leggere")
        return "Passaggio di consegne: " + ", ".join(parti) if parti else ""

    def _forza_relayout(self):
        """Documentazione della versione portfolio."""
        self._ridisegna_tutto()
        QTimer.singleShot(0, self._forza_relayout_differito)

    def _forza_relayout_differito(self):
        self._ridisegna_tutto()

    def _ridisegna_tutto(self):
        self.updateGeometry()
        genitore = self.parentWidget()
        if genitore is not None and genitore.layout() is not None:
            genitore.layout().invalidate()
            genitore.layout().activate()
        self.update()
        self.repaint()


        finestra_top = self.window()
        if finestra_top is not None:
            finestra_top.update()
            finestra_top.repaint()
