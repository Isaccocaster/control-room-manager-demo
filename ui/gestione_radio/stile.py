"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_GESTIONE_RADIO = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#gestione_radio_modern_control_room { background: transparent; }
QFrame#pannello_gestione_radio {
    background-color: rgba(11, 30, 53, 188);
    border: 1px solid rgba(87, 134, 182, 122);
    border-radius: 16px;
}
QLabel#titolo_gestione_radio { color: #F2F2F2; font-size: 20px; font-weight: 600; }
QLabel#sottotitolo_gestione_radio { color: #AFC0D5; font-size: 12px; }
QScrollArea#riga_scorrevole[ruolo="filtri_gestione_radio"],
QScrollArea#riga_scorrevole[ruolo="filtri_gestione_radio"] > QWidget > QWidget,
QScrollArea#riga_scorrevole[ruolo="azioni_gestione_radio"],
QScrollArea#riga_scorrevole[ruolo="azioni_gestione_radio"] > QWidget > QWidget,
QWidget#contenitore_filtri_gestione_radio, QWidget#contenitore_azioni_gestione_radio,
QWidget#barra_auricolari_gestione, QScrollArea#elenco_gestione_radio,
QScrollArea#elenco_gestione_radio > QWidget > QWidget, QWidget#contenitore_gestione_radio {
    background: transparent; border: none;
}
QPushButton#filtro_gestione_radio {
    min-height: 33px; padding: 4px 14px; color: #B8C7D9;
    background-color: rgba(8, 21, 39, 194); border: 1px solid #32577E; border-radius: 9px;
}
QPushButton#filtro_gestione_radio:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 58); border-color: #4A83BC;
}
QPushButton#filtro_gestione_radio:checked {
    color: #FFFFFF; background-color: #1F70CE; border-color: #5FA6F2; font-weight: 600;
}
QLineEdit#ricerca_gestione_radio {
    min-height: 36px; padding: 4px 11px; color: #F2F2F2;
    background-color: rgba(8, 21, 39, 226); border: 1px solid #32577E;
    border-radius: 9px; selection-background-color: #1F70CE;
}
QLineEdit#ricerca_gestione_radio:focus { border-color: #5FA6F2; }
QPushButton#aggiungi_radio, QPushButton#nuovo_auricolare_gestione {
    min-height: 36px; padding: 4px 15px; color: #FFFFFF; background-color: #1F70CE;
    border: 1px solid #3988E1; border-radius: 9px; font-weight: 600;
}
QPushButton#aggiungi_radio:hover, QPushButton#nuovo_auricolare_gestione:hover { background-color: #2C80DF; }
QPushButton#aggiorna_excel_gestione_radio, QPushButton#storico_gestione_radio {
    min-height: 36px; padding: 4px 13px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 27); border: 1px solid #32577E; border-radius: 9px;
}
QPushButton#aggiorna_excel_gestione_radio:hover, QPushButton#storico_gestione_radio:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 68); border-color: #4A83BC;
}
QLabel#sezione_gestione_radio {
    color: #9FC8F2; font-size: 12px; font-weight: 700; letter-spacing: 0.7px;
    padding: 12px 4px 3px 4px;
}
QLabel#stato_vuoto_gestione_radio { color: #B8C4D9; padding: 28px 14px; }
QFrame#riga_gestione_radio {
    background-color: rgba(8, 21, 39, 228); border: 1px solid rgba(87, 134, 182, 98);
    border-radius: 10px;
}
QFrame#riga_gestione_radio:hover {
    background-color: rgba(16, 43, 75, 238); border-color: rgba(95, 166, 242, 145);
}
QFrame#riga_gestione_radio[tipo="manutentore"] { border-left: 3px solid #D8A64B; }
QFrame#riga_gestione_radio[tipo="auricolare"] { border-left: 3px solid #4E97DF; }
QLabel#identita_gestione_radio { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#dettaglio_gestione_radio { color: #B9C8DA; font-size: 12px; }
QLabel#note_gestione_radio { color: #D8B77A; font-size: 12px; }
QPushButton#modifica_gestione_radio, QPushButton#rimuovi_gestione_radio {
    min-height: 32px; padding: 3px 12px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 32); border: 1px solid #3D6E9E; border-radius: 8px;
}
QPushButton#modifica_gestione_radio:hover { color: #FFFFFF; background-color: #1F70CE; border-color: #5FA6F2; }
QPushButton#rimuovi_gestione_radio { color: #F1B8B8; border-color: #7C4650; background-color: rgba(151, 55, 65, 34); }
QPushButton#rimuovi_gestione_radio:hover { color: #FFFFFF; background-color: #9B3945; border-color: #D56B76; }

QDialog#dialogo_radio_gestione, QDialog#dialogo_auricolare_gestione,
QDialog#storico_gestione_radio_modern_control_room,
QDialog#storico_gestione_radio_modern_control_room QDialog,
QDialog#storico_gestione_radio_modern_control_room QWidget,
QDialog#storico_gestione_radio_modern_control_room QScrollArea,
QDialog#storico_gestione_radio_modern_control_room QScrollArea > QWidget > QWidget {
    background-color: #0B1E35; color: #F2F2F2;
}
QDialog#storico_gestione_radio_modern_control_room QStackedWidget { background: transparent; border: none; }
QDialog#dialogo_radio_gestione QLineEdit, QDialog#dialogo_radio_gestione QComboBox,
QDialog#dialogo_auricolare_gestione QLineEdit, QDialog#dialogo_auricolare_gestione QComboBox,
QDialog#dialogo_auricolare_gestione QSpinBox,
QDialog#storico_gestione_radio_modern_control_room QLineEdit {
    min-height: 34px; padding: 4px 10px; color: #F2F2F2;
    background-color: rgba(8, 21, 39, 228); border: 1px solid #32577E;
    border-radius: 8px; selection-background-color: #1F70CE;
}
QDialog#dialogo_radio_gestione QLineEdit:focus, QDialog#dialogo_radio_gestione QComboBox:focus,
QDialog#dialogo_auricolare_gestione QLineEdit:focus, QDialog#dialogo_auricolare_gestione QComboBox:focus,
QDialog#dialogo_auricolare_gestione QSpinBox:focus,
QDialog#storico_gestione_radio_modern_control_room QLineEdit:focus { border-color: #5FA6F2; }
QDialog#dialogo_radio_gestione QComboBox QAbstractItemView,
QDialog#dialogo_auricolare_gestione QComboBox QAbstractItemView {
    color: #F2F2F2; background-color: #0B1E35; border: 1px solid #32577E;
    selection-background-color: #1F70CE;
}
QLabel#avviso_dialogo_radio { color: #9FB3CE; font-size: 11px; padding: 8px 0; }
QDialog#dialogo_radio_gestione QPushButton, QDialog#dialogo_auricolare_gestione QPushButton,
QDialog#storico_gestione_radio_modern_control_room QPushButton {
    min-height: 32px; padding: 4px 13px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 28); border: 1px solid #32577E; border-radius: 8px;
}
QDialog#dialogo_radio_gestione QPushButton:hover, QDialog#dialogo_auricolare_gestione QPushButton:hover,
QDialog#storico_gestione_radio_modern_control_room QPushButton:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 72); border-color: #4A83BC;
}
QDialog#storico_gestione_radio_modern_control_room QPushButton:checked {
    color: #FFFFFF; background-color: #1F70CE; border-color: #3988E1;
}
QDialog#storico_gestione_radio_modern_control_room QFrame#riga_risultato_chiave {
    background-color: rgba(8, 21, 39, 226); border: 1px solid rgba(87, 134, 182, 94); border-radius: 9px;
}
QDialog#storico_gestione_radio_modern_control_room QFrame#riga_risultato_chiave:hover {
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
