"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_CONSEGNA_RADIO = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#consegna_radio_modern_control_room,
QScrollArea#elenco_radio_fuori,
QScrollArea#elenco_radio_fuori > QWidget > QWidget,
QWidget#contenitore_radio_fuori {
    background: transparent;
    border: none;
}

QFrame#pannello_consegna_radio {
    background-color: rgba(11, 30, 53, 176);
    border: 1px solid rgba(87, 134, 182, 120);
    border-radius: 16px;
}

QLabel#titolo_consegna_radio {
    color: #F2F2F2;
    font-size: 20px;
    font-weight: 600;
}

QLabel#stato_consegna_radio {
    color: #C0E3FF;
    font-size: 15px;
    font-weight: 600;
}

QLabel#nessuna_radio_fuori {
    color: #B8C4D9;
    padding: 18px 4px;
}

QFrame#riga_radio_fuori {
    background-color: rgba(8, 21, 39, 220);
    border: 1px solid rgba(87, 134, 182, 92);
    border-radius: 10px;
}

QLabel#identita_radio_fuori {
    color: #F2F2F2;
    font-size: 14px;
    font-weight: 600;
}
QLabel#dettaglio_radio_fuori { color: #C0CEE2; font-size: 13px; }
QLabel#note_radio_fuori { color: #8EA2BE; font-size: 12px; }

QPushButton#nuova_consegna_radio {
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 10px;
    padding: 9px 15px;
    font-weight: 600;
    color: #FFFFFF;
}
QPushButton#nuova_consegna_radio:hover { background-color: #2C80DF; }
QPushButton#nuova_consegna_radio:pressed { background-color: #1958A4; }

QPushButton#storico_consegna_radio,
QPushButton#riconsegna_radio {
    color: #B8C4D9;
    background: transparent;
    border: 1px solid #32577E;
    border-radius: 9px;
    padding: 8px 14px;
}
QPushButton#storico_consegna_radio:hover,
QPushButton#riconsegna_radio:hover {
    color: #F2F2F2;
    background-color: rgba(31, 112, 206, 36);
}

/* Dialoghi del modulo: stessi raggi, bordi e gerarchia del Calendario,
   ma regole locali che non cambiano gli archivi degli altri moduli. */
QDialog#dialogo_nuova_consegna_radio,
QInputDialog#dialogo_riconsegna_radio,
QDialog#dialogo_storico_consegna_radio,
QDialog#dialogo_storico_consegna_radio QDialog {
    background-color: #0B1E35;
    color: #F2F2F2;
}

QDialog#dialogo_storico_consegna_radio QWidget,
QDialog#dialogo_storico_consegna_radio QScrollArea,
QDialog#dialogo_storico_consegna_radio QScrollArea > QWidget > QWidget {
    background: transparent;
    border: none;
}

QDialog#dialogo_nuova_consegna_radio QLineEdit,
QDialog#dialogo_nuova_consegna_radio QComboBox,
QInputDialog#dialogo_riconsegna_radio QLineEdit,
QDialog#dialogo_storico_consegna_radio QLineEdit {
    min-height: 34px;
    padding: 4px 10px;
    color: #F2F2F2;
    background-color: rgba(8, 21, 39, 220);
    border: 1px solid #32577E;
    border-radius: 8px;
    selection-background-color: #1F70CE;
}
QDialog#dialogo_nuova_consegna_radio QLineEdit:focus,
QDialog#dialogo_nuova_consegna_radio QComboBox:focus,
QInputDialog#dialogo_riconsegna_radio QLineEdit:focus,
QDialog#dialogo_storico_consegna_radio QLineEdit:focus {
    border-color: #5FA6F2;
}

QDialog#dialogo_nuova_consegna_radio QComboBox::drop-down {
    width: 30px;
    border: none;
}
QDialog#dialogo_nuova_consegna_radio QComboBox QAbstractItemView {
    color: #F2F2F2;
    background-color: #0B1E35;
    border: 1px solid #32577E;
    selection-background-color: #1F70CE;
}

QDialog#dialogo_nuova_consegna_radio QPushButton,
QInputDialog#dialogo_riconsegna_radio QPushButton,
QDialog#dialogo_storico_consegna_radio QPushButton {
    min-height: 32px;
    padding: 5px 14px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 24);
    border: 1px solid #32577E;
    border-radius: 8px;
}
QDialog#dialogo_nuova_consegna_radio QPushButton:hover,
QInputDialog#dialogo_riconsegna_radio QPushButton:hover,
QDialog#dialogo_storico_consegna_radio QPushButton:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 64);
    border-color: #4A83BC;
}
QDialog#dialogo_storico_consegna_radio QPushButton:checked {
    color: #FFFFFF;
    background-color: #1F70CE;
    border-color: #3988E1;
}

QDialog#dialogo_nuova_consegna_radio QPushButton#conferma_nuova_consegna_radio,
QInputDialog#dialogo_riconsegna_radio QPushButton#conferma_riconsegna_radio,
QDialog#dialogo_storico_consegna_radio QPushButton#chiudi_storico_consegna_radio {
    color: #FFFFFF;
    background-color: #1F70CE;
    border-color: #3988E1;
    font-weight: 600;
}

QDialog#dialogo_storico_consegna_radio QFrame#riga_risultato_chiave {
    background-color: rgba(8, 21, 39, 205);
    border: 1px solid rgba(87, 134, 182, 92);
    border-radius: 9px;
}
QDialog#dialogo_storico_consegna_radio QFrame#riga_risultato_chiave:hover {
    background-color: rgba(31, 112, 206, 36);
    border-color: #527EAE;
}
"""
