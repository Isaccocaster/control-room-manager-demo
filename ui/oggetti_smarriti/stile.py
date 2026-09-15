"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_OGGETTI = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#oggetti_smarriti_modern_control_room { background: transparent; }
QFrame#pannello_oggetti_smarriti {
    background-color: rgba(11, 30, 53, 188);
    border: 1px solid rgba(87, 134, 182, 122);
    border-radius: 16px;
}
QLabel#titolo_oggetti_smarriti { color: #F2F2F2; font-size: 20px; font-weight: 600; }
QLabel#sottotitolo_oggetti_smarriti { color: #AFC0D5; font-size: 12px; }
QScrollArea#riga_scorrevole[ruolo="viste_oggetti"],
QScrollArea#riga_scorrevole[ruolo="viste_oggetti"] > QWidget > QWidget,
QScrollArea#riga_scorrevole[ruolo="azioni_oggetti"],
QScrollArea#riga_scorrevole[ruolo="azioni_oggetti"] > QWidget > QWidget,
QWidget#contenitore_viste_oggetti,
QWidget#contenitore_azioni_oggetti,
QScrollArea#elenco_oggetti_smarriti,
QScrollArea#elenco_oggetti_smarriti > QWidget > QWidget,
QWidget#contenitore_oggetti_smarriti {
    background: transparent;
    border: none;
}
QPushButton#filtro_stato_oggetti {
    min-height: 33px;
    padding: 4px 14px;
    color: #B8C7D9;
    background-color: rgba(8, 21, 39, 194);
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#filtro_stato_oggetti:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 58); border-color: #4A83BC;
}
QPushButton#filtro_stato_oggetti:checked {
    color: #FFFFFF; background-color: #1F70CE; border-color: #5FA6F2; font-weight: 600;
}
QLineEdit#ricerca_oggetti_smarriti {
    min-height: 36px;
    padding: 4px 11px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid #32577E;
    border-radius: 9px;
    selection-background-color: #1F70CE;
}
QLineEdit#ricerca_oggetti_smarriti:focus { border-color: #5FA6F2; }
QPushButton#nuovo_oggetto_smarrito {
    min-height: 36px;
    padding: 4px 15px;
    color: #FFFFFF;
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 9px;
    font-weight: 600;
}
QPushButton#nuovo_oggetto_smarrito:hover { background-color: #2C80DF; }
QPushButton#aggiorna_excel_oggetti,
QPushButton#storico_oggetti_smarriti {
    min-height: 36px;
    padding: 4px 13px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 27);
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#aggiorna_excel_oggetti:hover,
QPushButton#storico_oggetti_smarriti:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 68); border-color: #4A83BC;
}
QLabel#stato_vuoto_oggetti { color: #B8C4D9; padding: 28px 14px; }
QFrame#riga_oggetto_smarrito {
    background-color: rgba(8, 21, 39, 228);
    border: 1px solid rgba(87, 134, 182, 98);
    border-radius: 10px;
}
QFrame#riga_oggetto_smarrito:hover {
    background-color: rgba(16, 43, 75, 238);
    border-color: rgba(95, 166, 242, 145);
}
QLabel#descrizione_oggetto_smarrito { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#dettaglio_oggetto_smarrito { color: #B9C8DA; font-size: 12px; }
QLabel#anomalia_oggetto_smarrito { color: #D8B77A; font-size: 12px; }
QPushButton#riconsegna_oggetto,
QPushButton#smaltisci_oggetto,
QPushButton#elimina_oggetto {
    min-height: 32px;
    padding: 3px 12px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 28);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QPushButton#riconsegna_oggetto:hover {
    color: #FFFFFF; background-color: #1F70CE; border-color: #5FA6F2;
}
QPushButton#smaltisci_oggetto:hover {
    color: #FFFFFF; background-color: rgba(206, 143, 48, 76); border-color: #B8873C;
}
QPushButton#elimina_oggetto:hover {
    color: #FFFFFF; background-color: rgba(201, 90, 90, 76); border-color: #A85D64;
}

QDialog#dialogo_operazione_oggetti,
QDialog#storico_oggetti_modern_control_room,
QDialog#storico_oggetti_modern_control_room QDialog,
QDialog#storico_oggetti_modern_control_room QWidget,
QDialog#storico_oggetti_modern_control_room QScrollArea,
QDialog#storico_oggetti_modern_control_room QScrollArea > QWidget > QWidget {
    background-color: #0B1E35;
    color: #F2F2F2;
}
QDialog#storico_oggetti_modern_control_room QStackedWidget { background: transparent; border: none; }
QLabel#intestazione_operazione_oggetti { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#avviso_excel_oggetti { color: #9FB3CE; font-size: 12px; padding: 8px 0; }
QDialog#dialogo_operazione_oggetti QLineEdit,
QDialog#storico_oggetti_modern_control_room QLineEdit {
    min-height: 34px;
    padding: 4px 10px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 228);
    border: 1px solid #32577E;
    border-radius: 8px;
    selection-background-color: #1F70CE;
}
QDialog#dialogo_operazione_oggetti QLineEdit:focus,
QDialog#storico_oggetti_modern_control_room QLineEdit:focus { border-color: #5FA6F2; }
QDialog#dialogo_operazione_oggetti QPushButton,
QDialog#storico_oggetti_modern_control_room QPushButton {
    min-height: 32px;
    padding: 4px 13px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 28);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QDialog#dialogo_operazione_oggetti QPushButton:hover,
QDialog#storico_oggetti_modern_control_room QPushButton:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 72); border-color: #4A83BC;
}
QPushButton#conferma_operazione_oggetti { color: #FFFFFF; background-color: #1F70CE; border-color: #3988E1; font-weight: 600; }
QDialog#storico_oggetti_modern_control_room QFrame#riga_risultato_chiave {
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid rgba(87, 134, 182, 94);
    border-radius: 9px;
}
QDialog#storico_oggetti_modern_control_room QFrame#riga_risultato_chiave:hover {
    background-color: rgba(31, 112, 206, 42); border-color: #527EAE;
}
QScrollBar:vertical, QScrollBar:horizontal { background: rgba(5, 16, 30, 120); margin: 2px; border-radius: 5px; }
QScrollBar:vertical { width: 10px; } QScrollBar:horizontal { height: 10px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #365F89; min-width: 26px; min-height: 26px; border-radius: 4px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #4D7EAE; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    width: 0px; height: 0px; background: transparent;
}
"""
