"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_CASSAFORTE = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#cassaforte_modern_control_room { background: transparent; }
QFrame#pannello_cassaforte {
    background-color: rgba(11, 30, 53, 188);
    border: 1px solid rgba(87, 134, 182, 122);
    border-radius: 16px;
}
QLabel#titolo_cassaforte { color: #F2F2F2; font-size: 20px; font-weight: 600; }
QLabel#sottotitolo_cassaforte { color: #AFC0D5; font-size: 12px; }
QScrollArea#riga_scorrevole[ruolo="azioni_cassaforte"],
QScrollArea#riga_scorrevole[ruolo="azioni_cassaforte"] > QWidget > QWidget,
QWidget#contenitore_azioni_cassaforte,
QScrollArea#elenco_cassaforte,
QScrollArea#elenco_cassaforte > QWidget > QWidget,
QWidget#contenitore_cassaforte {
    background: transparent;
    border: none;
}
QLineEdit#ricerca_cassaforte {
    min-height: 36px;
    padding: 4px 11px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid #32577E;
    border-radius: 9px;
    selection-background-color: #1F70CE;
}
QLineEdit#ricerca_cassaforte:focus { border-color: #5FA6F2; }
QPushButton#nuova_uscita_cassaforte,
QPushButton#nuovo_elemento_cassaforte {
    min-height: 36px;
    padding: 4px 14px;
    color: #FFFFFF;
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 9px;
    font-weight: 600;
}
QPushButton#nuova_uscita_cassaforte:hover,
QPushButton#nuovo_elemento_cassaforte:hover { background-color: #2C80DF; }
QPushButton#aggiorna_excel_cassaforte,
QPushButton#storico_cassaforte {
    min-height: 36px;
    padding: 4px 13px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 27);
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#aggiorna_excel_cassaforte:hover,
QPushButton#storico_cassaforte:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 68);
    border-color: #4A83BC;
}
QLabel#sezione_cassaforte {
    color: #9FC8F2;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.7px;
    padding: 12px 4px 3px 4px;
}
QLabel#stato_vuoto_cassaforte { color: #B8C4D9; padding: 10px 6px; }
QFrame#riga_elemento_cassaforte {
    background-color: rgba(8, 21, 39, 228);
    border: 1px solid rgba(87, 134, 182, 98);
    border-radius: 10px;
}
QFrame#riga_elemento_cassaforte:hover {
    background-color: rgba(16, 43, 75, 238);
    border-color: rgba(95, 166, 242, 145);
}
QLabel#descrizione_elemento_cassaforte { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#dettaglio_elemento_cassaforte { color: #B9C8DA; font-size: 12px; }
QLabel#nota_elemento_cassaforte { color: #D8B77A; font-size: 12px; }
QPushButton#uscita_elemento_cassaforte,
QPushButton#rientro_elemento_cassaforte {
    min-height: 32px;
    padding: 3px 12px;
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 48);
    border: 1px solid #3D6E9E;
    border-radius: 8px;
}
QPushButton#uscita_elemento_cassaforte:hover,
QPushButton#rientro_elemento_cassaforte:hover { background-color: #1F70CE; border-color: #5FA6F2; }

QDialog#dialogo_operazione_cassaforte,
QDialog#storico_cassaforte_modern_control_room,
QDialog#storico_cassaforte_modern_control_room QDialog,
QDialog#storico_cassaforte_modern_control_room QWidget,
QDialog#storico_cassaforte_modern_control_room QScrollArea,
QDialog#storico_cassaforte_modern_control_room QScrollArea > QWidget > QWidget {
    background-color: #0B1E35;
    color: #F2F2F2;
}
QDialog#storico_cassaforte_modern_control_room QStackedWidget { background: transparent; border: none; }
QLabel#intestazione_operazione_cassaforte { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#avviso_excel_cassaforte { color: #9FB3CE; font-size: 12px; padding: 8px 0; }
QDialog#dialogo_operazione_cassaforte QLineEdit,
QDialog#dialogo_operazione_cassaforte QComboBox,
QDialog#storico_cassaforte_modern_control_room QLineEdit {
    min-height: 34px;
    padding: 4px 10px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 228);
    border: 1px solid #32577E;
    border-radius: 8px;
    selection-background-color: #1F70CE;
}
QDialog#dialogo_operazione_cassaforte QLineEdit:focus,
QDialog#dialogo_operazione_cassaforte QComboBox:focus,
QDialog#storico_cassaforte_modern_control_room QLineEdit:focus { border-color: #5FA6F2; }
QDialog#dialogo_operazione_cassaforte QComboBox QAbstractItemView {
    color: #F2F2F2;
    background-color: #0B1E35;
    border: 1px solid #32577E;
    selection-background-color: #1F70CE;
}
QDialog#dialogo_operazione_cassaforte QCheckBox { color: #D5DFEB; spacing: 8px; }
QDialog#dialogo_operazione_cassaforte QCheckBox::indicator {
    width: 17px; height: 17px; border: 1px solid #4B78A5; border-radius: 4px;
    background-color: rgba(8, 21, 39, 230);
}
QDialog#dialogo_operazione_cassaforte QCheckBox::indicator:checked {
    background-color: #1F70CE; border-color: #5FA6F2;
}
QDialog#dialogo_operazione_cassaforte QPushButton,
QDialog#storico_cassaforte_modern_control_room QPushButton {
    min-height: 32px;
    padding: 4px 13px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 28);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QDialog#dialogo_operazione_cassaforte QPushButton:hover,
QDialog#storico_cassaforte_modern_control_room QPushButton:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 72); border-color: #4A83BC;
}
QPushButton#conferma_operazione_cassaforte { color: #FFFFFF; background-color: #1F70CE; border-color: #3988E1; font-weight: 600; }
QDialog#storico_cassaforte_modern_control_room QPushButton:checked {
    color: #FFFFFF; background-color: #1F70CE; border-color: #3988E1;
}
QDialog#storico_cassaforte_modern_control_room QFrame#riga_risultato_chiave {
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid rgba(87, 134, 182, 94);
    border-radius: 9px;
}
QDialog#storico_cassaforte_modern_control_room QFrame#riga_risultato_chiave:hover {
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
