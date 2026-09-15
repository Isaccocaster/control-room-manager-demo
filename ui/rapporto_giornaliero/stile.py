"""Documentazione della versione portfolio."""

from pathlib import Path

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


PERCORSO_FOTO_RAPPORTO = (
    Path(__file__).parent.parent / "assets" / "images" / "demo_rapporto_giornaliero.jpg"
)

FOGLIO_DI_STILE_RAPPORTO = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#rapporto_control_room,
QWidget#editor_rapporto_moderno {
    font-family: "Segoe UI";
    background: transparent;
    color: #F2F2F2;
}

/* La struttura resta quella del Calendario, ma la superficie assume la
   traslucenza fotografica della Home. Tabelle e note, più sotto, restano
   volutamente più opache perché la leggibilità operativa ha priorità. */
QWidget#rapporto_control_room QFrame#pannello_home,
QWidget#editor_rapporto_moderno QFrame#pannello_home {
    background-color: rgba(11, 30, 53, 176);
    border: 1px solid rgba(87, 134, 182, 120);
}

QLabel#titolo_rapporto {
    font-size: 20px;
    font-weight: 600;
    color: #F2F2F2;
}
QLabel#sottotitolo_rapporto,
QLabel#testo_supporto_rapporto {
    color: #B8C4D9;
}
QLabel#titolo_sezione_rapporto {
    color: #C0E3FF;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
}
QLabel#conteggio_rapporti {
    background-color: rgba(255,255,255,16);
    border: 1px solid rgba(87,134,182,70);
    border-radius: 10px;
    padding: 2px 9px;
    color: #C0E3FF;
    font-size: 11px;
    font-weight: 600;
}

QLineEdit#ricerca_rapporti {
    min-height: 24px;
    padding: 7px 10px;
    color: #F2F2F2;
    background-color: rgba(13, 35, 64, 215);
    border: 1px solid #32577E;
    border-radius: 9px;
    selection-background-color: #1F70CE;
}
QLineEdit#ricerca_rapporti:focus { border-color: #5790CC; }

QFrame#card_rapporto {
    background-color: rgba(255,255,255,15);
    border: 1px solid rgba(87,134,182,70);
    border-radius: 12px;
}
QFrame#card_rapporto:hover {
    background-color: rgba(255,255,255,22);
    border-color: rgba(87,134,182,125);
}
QWidget#testi_card_rapporto,
QWidget#azioni_card_rapporto,
QScrollArea#elenco_rapporti,
QScrollArea#elenco_rapporti > QWidget > QWidget {
    background: transparent;
    border: none;
}
QLabel#operatore_rapporto {
    color: #F2F2F2;
    font-size: 16px;
    font-weight: 600;
}
QLabel#metadati_rapporto {
    color: #B8C4D9;
    font-size: 12.5px;
}
QLabel#stato_rapporto {
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.7px;
}
QLabel#stato_rapporto[stato="aperto"] {
    color: #FFD2C9;
    background-color: rgba(255,138,115,30);
    border: 1px solid rgba(255,138,115,105);
}
QLabel#stato_rapporto[stato="chiuso"] {
    color: #B8D9CA;
    background-color: rgba(77,154,119,30);
    border: 1px solid rgba(105,184,146,90);
}

QFrame#card_rapporto QPushButton {
    min-height: 22px;
    padding: 6px 11px;
    color: #B8C4D9;
    background: transparent;
    border: 1px solid rgba(87,134,182,85);
    border-radius: 8px;
    font-size: 12px;
}
QFrame#card_rapporto QPushButton:hover {
    color: #F2F2F2;
    background-color: rgba(31,112,206,36);
    border-color: #527EAE;
}
QFrame#card_rapporto QPushButton[ruolo="primaria"] {
    color: #FFFFFF;
    background-color: #1F70CE;
    border-color: #3988E1;
    font-weight: 600;
}
QFrame#card_rapporto QPushButton[ruolo="primaria"]:hover {
    background-color: #2C80DF;
}
QFrame#card_rapporto QPushButton[ruolo="chiusura"] {
    color: #FFD2C9;
    border-color: rgba(255,138,115,105);
}

QFrame#stato_vuoto_rapporti {
    background-color: rgba(255,255,255,10);
    border: 1px dashed rgba(87,134,182,75);
    border-radius: 12px;
}
QLabel#titolo_stato_vuoto {
    color: #F2F2F2;
    font-size: 15px;
    font-weight: 600;
}
QLabel#testo_stato_vuoto {
    color: #7E90AB;
    font-size: 12px;
}

QFrame#separatore_azioni_rapporto {
    min-height: 1px;
    max-height: 1px;
    background-color: rgba(87,134,182,60);
    border: none;
}
QPushButton#azione_laterale_rapporto {
    min-height: 28px;
    padding: 8px 12px;
    color: #B8C4D9;
    background: transparent;
    border: 1px solid rgba(87,134,182,90);
    border-radius: 9px;
    text-align: left;
}
QPushButton#azione_laterale_rapporto:hover {
    color: #F2F2F2;
    background-color: rgba(31,112,206,36);
}

QLabel#titolo_editor_rapporto {
    color: #C0E3FF;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.8px;
}
QTableWidget#tabella_antintrusione,
QTextEdit#note_rapporto {
    color: #F2F2F2;
    background-color: #0D2340;
    border: 1px solid rgba(87,134,182,100);
    border-radius: 10px;
    selection-background-color: #1F70CE;
    gridline-color: rgba(87,134,182,55);
}
QTableWidget#tabella_antintrusione QHeaderView::section {
    color: #C0E3FF;
    background-color: #102A49;
    border: none;
    border-bottom: 1px solid rgba(87,134,182,85);
    padding: 7px;
    font-weight: 600;
}
QTextEdit#note_rapporto { padding: 8px; }

/* Ecosistema completo del modulo: dialoghi operativi, archivio e anteprima
   mantengono la stessa gerarchia visiva senza cambiare i rispettivi flussi. */
QDialog#dialogo_operativo_rapporto,
QDialog#archivio_rapporti_modern_control_room,
QDialog#anteprima_pdf_rapporto,
QMessageBox {
    color: #F2F2F2;
    background-color: #0B1E35;
}
QDialog#dialogo_operativo_rapporto QLabel#titolo_dialogo_rapporto,
QLabel#titolo_livello_archivio_rapporti {
    color: #F2F2F2;
    font-size: 16px;
    font-weight: 600;
}
QDialog#dialogo_operativo_rapporto QLineEdit,
QDialog#archivio_rapporti_modern_control_room QLineEdit {
    min-height: 34px;
    padding: 4px 10px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 220);
    border: 1px solid #32577E;
    border-radius: 8px;
    selection-background-color: #1F70CE;
}
QDialog#dialogo_operativo_rapporto QLineEdit:focus,
QDialog#archivio_rapporti_modern_control_room QLineEdit:focus {
    border-color: #5FA6F2;
}
QDialog#dialogo_operativo_rapporto QPushButton,
QDialog#archivio_rapporti_modern_control_room QPushButton,
QMessageBox QPushButton {
    min-height: 32px;
    padding: 5px 14px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 24);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QDialog#dialogo_operativo_rapporto QPushButton:hover,
QDialog#archivio_rapporti_modern_control_room QPushButton:hover,
QMessageBox QPushButton:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 64);
    border-color: #4A83BC;
}
QDialog#dialogo_operativo_rapporto QPushButton#conferma_dialogo_rapporto,
QDialog#archivio_rapporti_modern_control_room QPushButton#avvia_ricerca_archivio_rapporti,
QDialog#archivio_rapporti_modern_control_room QPushButton[ruolo="primaria"] {
    color: #FFFFFF;
    background-color: #1F70CE;
    border-color: #3988E1;
    font-weight: 600;
}
QStackedWidget#pagine_archivio_rapporti,
QWidget#pagina_archivio_rapporti,
QScrollArea#elenco_archivio_rapporti,
QScrollArea#elenco_archivio_rapporti > QWidget > QWidget,
QWidget#contenuto_archivio_rapporti {
    background: transparent;
    border: none;
}
QPushButton#indietro_archivio_rapporti {
    min-width: 36px;
    max-width: 36px;
    padding: 4px 0;
}
QDialog#archivio_rapporti_modern_control_room QPushButton[ruolo="navigazione_archivio"] {
    min-height: 38px;
    text-align: left;
    padding-left: 16px;
}
QDialog#archivio_rapporti_modern_control_room QFrame#riga_risultato_chiave {
    background-color: rgba(8, 21, 39, 205);
    border: 1px solid rgba(87, 134, 182, 92);
    border-radius: 10px;
}
QDialog#archivio_rapporti_modern_control_room QFrame#riga_risultato_chiave:hover {
    background-color: rgba(31, 112, 206, 36);
    border-color: #527EAE;
}
QLabel#operatore_archivio_rapporti { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#metadati_archivio_rapporti { color: #C0CEE2; font-size: 12.5px; }
QLabel#estratto_archivio_rapporti { color: #9FB3CE; font-size: 12px; }
QLabel#stato_vuoto_archivio_rapporti {
    color: #8EA2BE;
    padding: 24px;
    border: 1px dashed rgba(87,134,182,75);
    border-radius: 10px;
}
QLabel#avviso_archivio_rapporti { color: #D8B77A; font-size: 11px; padding: 8px; }
QDialog#anteprima_pdf_rapporto QPdfView {
    background-color: #081527;
    border: 1px solid #32577E;
    border-radius: 10px;
}
"""
