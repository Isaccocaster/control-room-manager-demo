"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_IMPOSTAZIONI = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#impostazioni_modern_control_room { background: transparent; }
QScrollArea#area_impostazioni,
QScrollArea#area_impostazioni > QWidget > QWidget { background: transparent; border: none; }
QFrame#pannello_impostazioni {
    background-color: rgba(11, 30, 53, 188);
    border: 1px solid rgba(87, 134, 182, 122);
    border-radius: 16px;
}
QLabel#titolo_impostazioni { color: #F2F2F2; font-size: 20px; font-weight: 600; }
QLabel#sottotitolo_impostazioni { color: #AFC0D5; font-size: 12px; }
QLabel#sezione_impostazioni {
    color: #9FC8F2; font-size: 12px; font-weight: 700;
    letter-spacing: 0.7px; padding: 10px 3px 2px 3px;
}
QFrame#contenitore_percorsi_impostazioni, QFrame#scheda_operatori_impostazioni {
    background-color: rgba(8, 21, 39, 214);
    border: 1px solid rgba(87, 134, 182, 98);
    border-radius: 11px;
}
QLabel#etichetta_percorso_impostazioni { color: #D6E0EB; font-size: 12px; font-weight: 600; }
QLabel#descrizione_operatori_impostazioni { color: #B9C8DA; font-size: 12px; }
QLabel#avviso_percorso_impostazioni { color: #FF9D8B; font-size: 11px; font-weight: 600; }
QLineEdit#percorso_impostazioni {
    min-height: 34px; padding: 4px 10px; color: #D8E4F1;
    background-color: rgba(5, 16, 30, 226); border: 1px solid #32577E;
    border-radius: 8px; selection-background-color: #1F70CE;
}
QLineEdit#percorso_impostazioni:focus { border-color: #5FA6F2; }
QPushButton#sfoglia_impostazioni, QPushButton#apri_operatori_impostazioni {
    min-height: 34px; padding: 4px 13px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 30); border: 1px solid #32577E; border-radius: 8px;
}
QPushButton#sfoglia_impostazioni:hover, QPushButton#apri_operatori_impostazioni:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 72); border-color: #4A83BC;
}
QPushButton#salva_impostazioni {
    min-height: 36px; padding: 4px 22px; color: #FFFFFF; background-color: #1F70CE;
    border: 1px solid #3988E1; border-radius: 9px; font-weight: 600;
}
QPushButton#salva_impostazioni:hover { background-color: #2C80DF; border-color: #5FA6F2; }

QDialog#dialogo_operatori_modern_control_room,
QDialog#dialogo_operatori_modern_control_room QWidget,
QDialog#dialogo_operatori_modern_control_room QTableWidget,
QDialog#dialogo_operatori_modern_control_room QHeaderView,
QDialog#dialogo_operatori_modern_control_room QAbstractItemView,
QMessageBox { background-color: #0B1E35; color: #F2F2F2; }
QDialog#dialogo_operatori_modern_control_room QLineEdit,
QDialog#dialogo_operatori_modern_control_room QComboBox {
    min-height: 34px; padding: 4px 10px; color: #F2F2F2;
    background-color: rgba(8, 21, 39, 228); border: 1px solid #32577E;
    border-radius: 8px; selection-background-color: #1F70CE;
}
QDialog#dialogo_operatori_modern_control_room QLineEdit:focus,
QDialog#dialogo_operatori_modern_control_room QComboBox:focus { border-color: #5FA6F2; }
QDialog#dialogo_operatori_modern_control_room QTableWidget {
    alternate-background-color: #102B4B; gridline-color: #294E73;
    border: 1px solid #32577E; border-radius: 8px;
}
QDialog#dialogo_operatori_modern_control_room QHeaderView::section {
    color: #C6D6E8; background-color: #122F50; border: none;
    border-right: 1px solid #294E73; border-bottom: 1px solid #3B658E;
    padding: 7px; font-weight: 600;
}
QDialog#dialogo_operatori_modern_control_room QTableWidget::item:selected {
    color: #FFFFFF; background-color: #1F70CE;
}
QDialog#dialogo_operatori_modern_control_room QPushButton, QMessageBox QPushButton {
    min-height: 31px; padding: 4px 12px; color: #C6D3E6;
    background-color: rgba(31, 112, 206, 30); border: 1px solid #32577E; border-radius: 8px;
}
QDialog#dialogo_operatori_modern_control_room QPushButton:hover, QMessageBox QPushButton:hover {
    color: #FFFFFF; background-color: rgba(31, 112, 206, 72); border-color: #4A83BC;
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
