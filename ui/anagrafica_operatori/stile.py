"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_ANAGRAFICA_OPERATORI = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#anagrafica_operatori_modern_control_room,
QWidget#contenuto_anagrafica_operatori,
QWidget#azioni_riga_anagrafica { background: transparent; }
QFrame#pannello_anagrafica_operatori {
    background-color: rgba(11, 30, 53, 188);
    border: 1px solid rgba(87, 134, 182, 122);
    border-radius: 16px;
}
QLabel#titolo_anagrafica_operatori {
    color: #F2F2F2; font-size: 20px; font-weight: 600;
}
QLabel#sottotitolo_anagrafica_operatori,
QLabel#conteggio_anagrafica_operatori {
    color: #AFC0D5; font-size: 12px;
}
QLabel#stato_vuoto_anagrafica_operatori {
    color: #B8C4D9; padding: 12px;
}
QLineEdit#ricerca_anagrafica_operatori,
QComboBox#filtro_categoria_anagrafica,
QComboBox#filtro_stato_anagrafica {
    min-height: 36px; padding: 4px 11px; color: #F2F2F2;
    background-color: rgba(8, 21, 39, 226);
    border: 1px solid #32577E; border-radius: 9px;
    selection-background-color: #1F70CE;
}
QLineEdit#ricerca_anagrafica_operatori:focus,
QComboBox#filtro_categoria_anagrafica:focus,
QComboBox#filtro_stato_anagrafica:focus { border-color: #5FA6F2; }
QComboBox#filtro_categoria_anagrafica QAbstractItemView,
QComboBox#filtro_stato_anagrafica QAbstractItemView {
    color: #F2F2F2; background-color: #0B1E35;
    border: 1px solid #32577E; selection-background-color: #1F70CE;
}
QPushButton#nuovo_operatore_anagrafica {
    min-height: 36px; padding: 4px 15px; color: #FFFFFF;
    background-color: #1F70CE; border: 1px solid #3988E1;
    border-radius: 9px; font-weight: 600;
}
QPushButton#nuovo_operatore_anagrafica:hover {
    background-color: #2C80DF; border-color: #5FA6F2;
}
QTableWidget#tabella_anagrafica_operatori {
    color: #EAF0F7; background-color: rgba(8, 21, 39, 226);
    alternate-background-color: rgba(16, 43, 75, 224);
    gridline-color: #294E73; border: 1px solid #32577E; border-radius: 9px;
    selection-background-color: #1F70CE; selection-color: #FFFFFF;
}
QTableWidget#tabella_anagrafica_operatori::item { padding: 7px; }
QTableWidget#tabella_anagrafica_operatori::item:selected {
    color: #FFFFFF; background-color: #1F70CE;
}
QTableWidget#tabella_anagrafica_operatori QHeaderView::section {
    color: #C6D6E8; background-color: #122F50; border: none;
    border-right: 1px solid #294E73; border-bottom: 1px solid #3B658E;
    padding: 8px; font-weight: 600;
}
QPushButton#modifica_operatore_anagrafica,
QPushButton#disattiva_operatore_anagrafica,
QPushButton#riattiva_operatore_anagrafica {
    min-height: 30px; padding: 3px 10px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 32);
    border: 1px solid #3D6E9E; border-radius: 7px;
}
QPushButton#modifica_operatore_anagrafica:hover,
QPushButton#riattiva_operatore_anagrafica:hover {
    color: #FFFFFF; background-color: #1F70CE; border-color: #5FA6F2;
}
QPushButton#disattiva_operatore_anagrafica {
    color: #F1B8B8; border-color: #7C4650; background-color: rgba(151, 55, 65, 34);
}
QPushButton#disattiva_operatore_anagrafica:hover {
    color: #FFFFFF; background-color: #9B3945; border-color: #D56B76;
}
QDialog#dialogo_nuovo_operatore,
QDialog#dialogo_modifica_operatore,
QDialog#dialogo_anagrafica_operatori {
    background-color: #0B1E35; color: #F2F2F2;
}
QDialog#dialogo_nuovo_operatore QLineEdit,
QDialog#dialogo_nuovo_operatore QComboBox,
QDialog#dialogo_modifica_operatore QLineEdit,
QDialog#dialogo_modifica_operatore QComboBox {
    min-height: 34px; padding: 4px 10px; color: #F2F2F2;
    background-color: rgba(8, 21, 39, 228);
    border: 1px solid #32577E; border-radius: 8px;
    selection-background-color: #1F70CE;
}
QLabel#avviso_modifica_operatore { color: #9FB3CE; font-size: 11px; }
QDialog#dialogo_nuovo_operatore QPushButton,
QDialog#dialogo_modifica_operatore QPushButton,
QDialog#dialogo_anagrafica_operatori QPushButton {
    min-height: 31px; padding: 4px 12px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 30);
    border: 1px solid #32577E; border-radius: 8px;
}
QDialog#dialogo_nuovo_operatore QPushButton:hover,
QDialog#dialogo_modifica_operatore QPushButton:hover,
QDialog#dialogo_anagrafica_operatori QPushButton:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 72); border-color: #4A83BC;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: rgba(5, 16, 30, 120); margin: 2px; border-radius: 5px;
}
QScrollBar:vertical { width: 10px; }
QScrollBar:horizontal { height: 10px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #365F89; min-width: 26px; min-height: 26px; border-radius: 4px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #4D7EAE; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    width: 0px; height: 0px; background: transparent;
}
"""
