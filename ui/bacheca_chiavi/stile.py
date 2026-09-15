"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_BACHECA = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#bacheca_chiavi_modern_control_room { background: transparent; }
QFrame#pannello_bacheca_chiavi {
    background-color: rgba(11, 30, 53, 184);
    border: 1px solid rgba(87, 134, 182, 122);
    border-radius: 16px;
}
QLabel#titolo_bacheca_chiavi {
    color: #F2F2F2;
    font-size: 20px;
    font-weight: 600;
}
QLabel#sottotitolo_bacheca_chiavi { color: #AFC0D5; font-size: 12px; }

QScrollArea#riga_scorrevole[ruolo="selettore_bacheche"],
QScrollArea#riga_scorrevole[ruolo="selettore_bacheche"] > QWidget > QWidget,
QWidget#contenitore_selettore_bacheche,
QScrollArea#riga_scorrevole[ruolo="azioni_bacheca"],
QScrollArea#riga_scorrevole[ruolo="azioni_bacheca"] > QWidget > QWidget,
QWidget#contenitore_azioni_bacheca,
QScrollArea#risultati_bacheca_chiavi,
QScrollArea#risultati_bacheca_chiavi > QWidget > QWidget,
QWidget#contenitore_risultati_bacheca {
    background: transparent;
    border: none;
}
QPushButton#filtro_bacheca {
    min-height: 32px;
    padding: 4px 13px;
    color: #B8C7D9;
    background-color: rgba(8, 21, 39, 188);
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#filtro_bacheca:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 58);
    border-color: #4A83BC;
}
QPushButton#filtro_bacheca:checked {
    color: #FFFFFF;
    background-color: #1F70CE;
    border-color: #5FA6F2;
    font-weight: 600;
}
QLineEdit#ricerca_bacheca_chiavi {
    min-height: 36px;
    padding: 4px 11px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 224);
    border: 1px solid #32577E;
    border-radius: 9px;
    selection-background-color: #1F70CE;
}
QLineEdit#ricerca_bacheca_chiavi:focus { border-color: #5FA6F2; }
QPushButton#aggiungi_chiave_bacheca {
    min-height: 36px;
    padding: 4px 15px;
    color: #FFFFFF;
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 9px;
    font-weight: 600;
}
QPushButton#aggiungi_chiave_bacheca:hover { background-color: #2C80DF; }
QPushButton#aggiungi_chiave_bacheca:disabled {
    color: #64758A;
    background-color: rgba(8, 21, 39, 140);
    border-color: #263E59;
}
QPushButton#storico_bacheca_chiavi {
    min-height: 36px;
    padding: 4px 14px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 26);
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#storico_bacheca_chiavi:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 64);
    border-color: #4A83BC;
}

QLabel#stato_vuoto_bacheca {
    color: #B8C4D9;
    padding: 28px 14px;
    font-size: 13px;
}
QLabel#intestazione_blocco_bacheca {
    color: #9FC8F2;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.7px;
    padding: 12px 4px 3px 4px;
}
QFrame#riga_bacheca_chiavi {
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid rgba(87, 134, 182, 98);
    border-radius: 10px;
}
QFrame#riga_bacheca_chiavi:hover {
    background-color: rgba(16, 43, 75, 236);
    border-color: rgba(95, 166, 242, 145);
}
QLabel#identita_chiave_bacheca { color: #F2F2F2; font-size: 14px; font-weight: 600; }
QLabel#dettaglio_chiave_bacheca { color: #B9C8DA; font-size: 12px; }
QPushButton#uscita_chiave,
QPushButton#rientro_chiave,
QPushButton#modifica_chiave,
QPushButton#rimuovi_chiave {
    min-height: 31px;
    padding: 3px 11px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 25);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QPushButton#uscita_chiave:hover,
QPushButton#rientro_chiave:hover,
QPushButton#modifica_chiave:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 68);
    border-color: #4A83BC;
}
QPushButton#rimuovi_chiave:hover {
    color: #FFFFFF;
    background-color: rgba(201, 90, 90, 74);
    border-color: #A85D64;
}

QDialog#dialogo_chiave_bacheca,
QDialog#dialogo_voce_cassaforte_bacheca,
QDialog#storico_bacheca_chiavi_modern_control_room,
QDialog#storico_bacheca_chiavi_modern_control_room QDialog,
QDialog#storico_bacheca_chiavi_modern_control_room QWidget,
QDialog#storico_bacheca_chiavi_modern_control_room QScrollArea,
QDialog#storico_bacheca_chiavi_modern_control_room QScrollArea > QWidget > QWidget {
    background-color: #0B1E35;
    color: #F2F2F2;
}
QDialog#storico_bacheca_chiavi_modern_control_room QStackedWidget {
    background: transparent;
    border: none;
}
QDialog#dialogo_chiave_bacheca QLineEdit,
QDialog#dialogo_chiave_bacheca QSpinBox,
QDialog#dialogo_voce_cassaforte_bacheca QLineEdit,
QDialog#dialogo_voce_cassaforte_bacheca QSpinBox,
QDialog#storico_bacheca_chiavi_modern_control_room QLineEdit {
    min-height: 34px;
    padding: 4px 10px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid #32577E;
    border-radius: 8px;
    selection-background-color: #1F70CE;
}
QDialog#dialogo_chiave_bacheca QLineEdit:focus,
QDialog#dialogo_chiave_bacheca QSpinBox:focus,
QDialog#dialogo_voce_cassaforte_bacheca QLineEdit:focus,
QDialog#dialogo_voce_cassaforte_bacheca QSpinBox:focus,
QDialog#storico_bacheca_chiavi_modern_control_room QLineEdit:focus { border-color: #5FA6F2; }
QDialog#dialogo_chiave_bacheca QPushButton,
QDialog#dialogo_voce_cassaforte_bacheca QPushButton,
QDialog#storico_bacheca_chiavi_modern_control_room QPushButton {
    min-height: 32px;
    padding: 4px 13px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 27);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QDialog#dialogo_chiave_bacheca QPushButton:hover,
QDialog#dialogo_voce_cassaforte_bacheca QPushButton:hover,
QDialog#storico_bacheca_chiavi_modern_control_room QPushButton:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 70);
    border-color: #4A83BC;
}
QDialog#storico_bacheca_chiavi_modern_control_room QPushButton:checked {
    color: #FFFFFF;
    background-color: #1F70CE;
    border-color: #3988E1;
}
QDialog#storico_bacheca_chiavi_modern_control_room QFrame#riga_risultato_chiave {
    background-color: rgba(8, 21, 39, 224);
    border: 1px solid rgba(87, 134, 182, 94);
    border-radius: 9px;
}
QDialog#storico_bacheca_chiavi_modern_control_room QFrame#riga_risultato_chiave:hover {
    background-color: rgba(31, 112, 206, 42);
    border-color: #527EAE;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background: rgba(5, 16, 30, 120);
    margin: 2px;
    border-radius: 5px;
}
QScrollBar:vertical { width: 10px; }
QScrollBar:horizontal { height: 10px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #365F89;
    min-width: 26px;
    min-height: 26px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #4D7EAE; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    width: 0px;
    height: 0px;
    background: transparent;
}
"""
