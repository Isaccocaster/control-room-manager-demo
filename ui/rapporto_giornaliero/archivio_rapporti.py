"""Documentazione della versione portfolio."""
import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from data.rapporti_giornalieri import (
    MESI_ITALIANO,
    anni_mesi_archiviati,
    rapporti_archiviati_di,
    tutti_i_rapporti_archiviati,
)
from documents.word.rapporto_giornaliero import cerca_nei_rapporti
from ui.rapporto_giornaliero.stile import FOGLIO_DI_STILE_RAPPORTO


class DialogoArchivioRapporti(QDialog):
    def __init__(self, parent, cartella_rapporti: str, al_apri_per_modifica, al_anteprima_pdf):
        """Documentazione della versione portfolio."""
        super().__init__(parent)
        self.setObjectName("archivio_rapporti_modern_control_room")
        self.setStyleSheet(FOGLIO_DI_STILE_RAPPORTO)
        self.setWindowTitle("Archivio Rapporti Giornalieri")
        self.setMinimumSize(720, 520)
        self.resize(920, 680)
        self._cartella_rapporti = cartella_rapporti
        self._al_apri_per_modifica = al_apri_per_modifica
        self._al_anteprima_pdf = al_anteprima_pdf

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        self._pagine = QStackedWidget()
        self._pagine.setObjectName("pagine_archivio_rapporti")
        layout.addWidget(self._pagine, stretch=1)

        pulsante_chiudi = QPushButton("Chiudi")
        pulsante_chiudi.setObjectName("chiudi_archivio_rapporti")
        pulsante_chiudi.clicked.connect(self.accept)
        layout.addWidget(pulsante_chiudi)

        self._mostra_anni()


    def _vai_a(self, pagina: QWidget):
        self._pagine.addWidget(pagina)
        self._pagine.setCurrentWidget(pagina)

    def _crea_area_scorrevole(self) -> tuple[QScrollArea, QVBoxLayout]:
        area = QScrollArea()
        area.setObjectName("elenco_archivio_rapporti")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        contenitore = QWidget()
        contenitore.setObjectName("contenuto_archivio_rapporti")
        layout = QVBoxLayout(contenitore)
        layout.setSpacing(8)
        area.setWidget(contenitore)
        return area, layout

    def _crea_intestazione_livello(self, titolo: str, al_indietro) -> QHBoxLayout:
        intestazione = QHBoxLayout()
        if al_indietro is not None:
            pulsante_indietro = QPushButton("←")
            pulsante_indietro.setObjectName("indietro_archivio_rapporti")
            pulsante_indietro.setFixedWidth(40)
            pulsante_indietro.clicked.connect(al_indietro)
            intestazione.addWidget(pulsante_indietro)
        etichetta = QLabel(titolo)
        etichetta.setObjectName("titolo_livello_archivio_rapporti")
        intestazione.addWidget(etichetta)
        intestazione.addStretch()
        return intestazione

    def _mostra_anni(self):
        coppie = anni_mesi_archiviati(self._cartella_rapporti)
        anni = sorted({anno for anno, _ in coppie}, reverse=True)

        pagina = QWidget()
        pagina.setObjectName("pagina_archivio_rapporti")
        layout = QVBoxLayout(pagina)
        layout.addLayout(self._crea_intestazione_livello("Archivio — Anni", None))
        layout.addLayout(self._crea_riga_ricerca())

        area, layout_elenco = self._crea_area_scorrevole()
        if not anni:
            etichetta = QLabel("Nessun rapporto archiviato.")
            etichetta.setObjectName("stato_vuoto_archivio_rapporti")
            layout_elenco.addWidget(etichetta)
        for anno in anni:
            pulsante = QPushButton(str(anno))
            pulsante.setProperty("ruolo", "navigazione_archivio")
            pulsante.clicked.connect(lambda _, a=anno: self._mostra_mesi(a, coppie))
            layout_elenco.addWidget(pulsante)
        layout_elenco.addStretch()
        layout.addWidget(area, stretch=1)

        self._vai_a(pagina)

    def _mostra_mesi(self, anno: int, coppie: list[tuple[int, int]]):
        mesi = sorted({mese for a, mese in coppie if a == anno})

        pagina = QWidget()
        pagina.setObjectName("pagina_archivio_rapporti")
        layout = QVBoxLayout(pagina)
        layout.addLayout(self._crea_intestazione_livello(f"Archivio — {anno}", self._mostra_anni))

        area, layout_elenco = self._crea_area_scorrevole()
        for mese in mesi:
            pulsante = QPushButton(MESI_ITALIANO[mese - 1].capitalize())
            pulsante.setProperty("ruolo", "navigazione_archivio")
            pulsante.clicked.connect(lambda _, m=mese: self._mostra_rapporti(anno, m))
            layout_elenco.addWidget(pulsante)
        layout_elenco.addStretch()
        layout.addWidget(area, stretch=1)

        self._vai_a(pagina)

    def _mostra_rapporti(self, anno: int, mese: int):
        rapporti = rapporti_archiviati_di(self._cartella_rapporti, anno, mese)
        nome_mese = MESI_ITALIANO[mese - 1].capitalize()

        pagina = QWidget()
        pagina.setObjectName("pagina_archivio_rapporti")
        layout = QVBoxLayout(pagina)
        layout.addLayout(
            self._crea_intestazione_livello(f"Archivio — {nome_mese} {anno}",
                                             lambda: self._mostra_anni_o_mesi(anno))
        )

        area, layout_elenco = self._crea_area_scorrevole()
        if not rapporti:
            etichetta = QLabel("Nessun rapporto archiviato in questo periodo.")
            etichetta.setObjectName("stato_vuoto_archivio_rapporti")
            etichetta.setAlignment(Qt.AlignCenter)
            layout_elenco.addWidget(etichetta)
        for rapporto in rapporti:
            layout_elenco.addWidget(self._crea_riga(rapporto))
        layout_elenco.addStretch()
        layout.addWidget(area, stretch=1)

        self._vai_a(pagina)

    def _mostra_anni_o_mesi(self, anno: int):
        """Documentazione della versione portfolio."""
        coppie = anni_mesi_archiviati(self._cartella_rapporti)
        self._mostra_mesi(anno, coppie)


    def _crea_riga_ricerca(self) -> QHBoxLayout:
        riga = QHBoxLayout()
        campo = QLineEdit()
        campo.setObjectName("ricerca_archivio_rapporti")
        campo.setClearButtonEnabled(True)
        campo.setPlaceholderText("🔎 Cerca nei rapporti...")
        campo.returnPressed.connect(lambda: self._cerca(campo.text()))
        riga.addWidget(campo, stretch=1)

        pulsante = QPushButton("Cerca")
        pulsante.setObjectName("avvia_ricerca_archivio_rapporti")
        pulsante.clicked.connect(lambda: self._cerca(campo.text()))
        riga.addWidget(pulsante)
        return riga

    def _cerca(self, termine: str):
        if not termine.strip():
            return
        self._mostra_risultati_ricerca(termine.strip())

    def _mostra_risultati_ricerca(self, termine: str):
        tutti = tutti_i_rapporti_archiviati(self._cartella_rapporti)
        risultati, file_con_errore = cerca_nei_rapporti(tutti, termine)

        pagina = QWidget()
        pagina.setObjectName("pagina_archivio_rapporti")
        layout = QVBoxLayout(pagina)
        layout.addLayout(
            self._crea_intestazione_livello(f'Risultati per "{termine}"', self._mostra_anni)
        )

        area, layout_elenco = self._crea_area_scorrevole()
        if not risultati:
            etichetta = QLabel("Nessun rapporto contiene questo termine.")
            etichetta.setObjectName("stato_vuoto_archivio_rapporti")
            layout_elenco.addWidget(etichetta)
        for rapporto in risultati:
            layout_elenco.addWidget(self._crea_riga(rapporto, termine))

        if file_con_errore:
            avviso = QLabel(
                f"{len(file_con_errore)} documento(i) non leggibile(i) e ignorato(i) da questa ricerca."
            )
            avviso.setWordWrap(True)
            avviso.setObjectName("avviso_archivio_rapporti")
            layout_elenco.addWidget(avviso)

        layout_elenco.addStretch()
        layout.addWidget(area, stretch=1)

        self._vai_a(pagina)

    @staticmethod
    def _evidenzia(estratto: str, termine: str) -> str:
        """Documentazione della versione portfolio."""
        indice = estratto.lower().find(termine.strip().lower())
        if indice == -1:
            return html.escape(estratto)
        fine = indice + len(termine.strip())
        return (
            f"{html.escape(estratto[:indice])}"
            f"<b>{html.escape(estratto[indice:fine])}</b>"
            f"{html.escape(estratto[fine:])}"
        )

    def _crea_riga(self, rapporto: dict, termine_ricerca: str | None = None) -> QWidget:
        riga = QFrame()
        riga.setObjectName("riga_risultato_chiave")
        riga.setProperty("modulo", "rapporto")
        layout = QHBoxLayout(riga)
        layout.setContentsMargins(10, 8, 10, 8)

        layout_testo = QVBoxLayout()
        titolo = QLabel(f"{rapporto['operatore_nome']} {rapporto['operatore_cognome']}")
        titolo.setObjectName("operatore_archivio_rapporti")
        layout_testo.addWidget(titolo)
        dettaglio = QLabel(f"{rapporto['data_turno']}   {rapporto['ora_inizio']} - {rapporto['ora_fine']}")
        dettaglio.setObjectName("metadati_archivio_rapporti")
        layout_testo.addWidget(dettaglio)


        if rapporto.get("estratto"):
            estratto = QLabel(self._evidenzia(rapporto["estratto"], termine_ricerca or ""))
            estratto.setTextFormat(Qt.RichText)
            estratto.setWordWrap(True)
            estratto.setObjectName("estratto_archivio_rapporti")
            layout_testo.addWidget(estratto)

        layout.addLayout(layout_testo, stretch=1)

        pulsante_apri = QPushButton("Apri per modifica")
        pulsante_apri.setProperty("ruolo", "primaria")
        pulsante_apri.clicked.connect(lambda: self._apri_e_chiudi_dialogo(rapporto))
        layout.addWidget(pulsante_apri)

        pulsante_anteprima = QPushButton("Anteprima PDF")
        pulsante_anteprima.setProperty("ruolo", "secondaria")
        pulsante_anteprima.clicked.connect(lambda: self._al_anteprima_pdf(rapporto))
        layout.addWidget(pulsante_anteprima)

        return riga

    def _apri_e_chiudi_dialogo(self, rapporto: dict):
        """Documentazione della versione portfolio."""
        self._al_apri_per_modifica(rapporto)
        self.accept()
