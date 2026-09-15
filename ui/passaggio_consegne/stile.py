"""Documentazione della versione portfolio."""

from ui.tema import FOGLIO_DI_STILE_CALENDARIO


FOGLIO_DI_STILE_PASSAGGIO = FOGLIO_DI_STILE_CALENDARIO + """
QWidget#pannello_passaggio_consegne {
    background: transparent;
}

QFrame#barra_passaggio_consegne {
    background-color: #081527;
    border: none;
    border-radius: 0px;
}
QFrame#barra_passaggio_consegne:hover {
    background-color: #0F2744;
}
QFrame#barra_passaggio_consegne[variante="sidebar"] {
    background-color: rgba(11, 30, 53, 214);
    border: 1px solid rgba(87, 134, 182, 126);
    border-radius: 11px;
}
QFrame#barra_passaggio_consegne[variante="sidebar"]:hover {
    background-color: rgba(31, 112, 206, 40);
    border-color: #4A83BC;
}
QLabel#titolo_barra_passaggio {
    color: #EAF2FC;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#freccia_passaggio { color: #91BCE9; font-size: 12px; }

/* ------------------------------------------------------------------
   Badge del Passaggio di Consegne — due pillole, un solo sistema.

   Stessa geometria (pillola, raggio 11, 11px/700, maiuscoletto spaziato)
   e stessa famiglia di superfici del resto del Modern Control Room:
   cambia soltanto il **peso** del colore, ed e' quello a fare la
   gerarchia che l'utente ha chiesto.

     normale    -> accento blu traslucido, evidente ma operativo
     importante -> oro pieno, massima priorita' visiva

   L'oro e' lo stesso gia' usato dal pulsante di fissaggio quando e'
   attivo (`QPushButton#fissa_passaggio:checked`): il colore vuol dire
   "importante" in ogni punto del modulo, non due cose diverse a
   seconda di dove lo si guarda.
   ------------------------------------------------------------------ */
QWidget#indicatore_passaggio_consegne,
QWidget#intestazione_sezione_storico_passaggio { background: transparent; border: none; }

QLabel#badge_normali_passaggio {
    color: #DCEBFF;
    background-color: rgba(31, 112, 206, 92);
    border: 1px solid #3988E1;
    border-radius: 11px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}
/* La pillola oro e' un QFrame, non una QLabel: dentro ci stanno il disco
   di priorita' e il testo, uno accanto all'altro. Il disco e' un pixmap a
   dimensione fissa — e' questo che gli impedisce di essere tagliato, cosa
   che alla vecchia puntina succedeva perche' era un glifo dentro la riga di
   testo. Il padding sta qui, sulla superficie, e vale per entrambi. */
QFrame#badge_importanti_passaggio,
QFrame#chip_importante_passaggio {
    background-color: #E7BB67;
    border: 1px solid #F1D08B;
    border-radius: 11px;
    padding: 3px 10px;
}
QFrame#badge_importanti_passaggio QLabel#testo_priorita_passaggio,
QFrame#chip_importante_passaggio QLabel#testo_priorita_passaggio {
    color: #10233C;
    background: transparent;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}
QLabel#icona_priorita_passaggio,
QLabel#icona_storico_passaggio { background: transparent; border: none; }
/* Il chip della singola comunicazione e' la stessa pillola in piccolo:
   deve segnalare, non gridare sopra il testo che accompagna. */
QFrame#chip_importante_passaggio {
    border-radius: 10px;
    padding: 2px 9px;
}
QFrame#chip_importante_passaggio QLabel#testo_priorita_passaggio {
    font-size: 10px;
}

/* Lo sfondo fotografico e l'overlay del blocco note sono dipinti dal widget,
   così la foto scala e ritaglia correttamente a ogni DPI. */
QFrame#notepad_passaggio_consegne {
    background: transparent;
    border: none;
}
QLabel#titolo_notepad_passaggio {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.8px;
}
QScrollArea#elenco_passaggio,
QScrollArea#elenco_passaggio > QWidget > QWidget,
QWidget#contenitore_righe_passaggio {
    background: transparent;
    border: none;
}
QFrame#riga_passaggio {
    background-color: rgba(8, 21, 39, 222);
    border: 1px solid rgba(87, 134, 182, 96);
    border-radius: 9px;
}
QFrame#riga_passaggio:hover {
    background-color: rgba(18, 48, 83, 232);
    border-color: rgba(95, 166, 242, 136);
}
/* Comunicazione importante: accento oro sul bordo sinistro, lo stesso
   linguaggio della voce attiva della sidebar. Il fondo resta navy e il
   testo resta bianco pieno: l'evidenza non deve costare leggibilita'. */
QFrame#riga_passaggio[fissato="true"] {
    background-color: rgba(26, 32, 43, 228);
    border: 1px solid rgba(231, 187, 103, 132);
    border-left: 3px solid #E7BB67;
}
QFrame#riga_passaggio[fissato="true"]:hover {
    background-color: rgba(43, 50, 60, 236);
    border-color: rgba(241, 208, 139, 170);
    border-left: 3px solid #F1D08B;
}
/* Il contenitore interno della riga esiste solo per reggere il chip
   sopra il testo: senza questa regola erediterebbe il fondo navy pieno
   del foglio globale e coprirebbe la superficie della riga. */
QWidget#contenuto_riga_passaggio { background: transparent; border: none; }
QLabel#testo_passaggio { color: #F2F2F2; font-size: 13px; }
QLabel#stato_vuoto_passaggio {
    color: #B8C4D9;
    padding: 22px 12px;
}
QLineEdit#nuova_comunicazione_passaggio,
QLineEdit#modifica_comunicazione_passaggio {
    min-height: 34px;
    padding: 4px 10px;
    color: #F2F2F2;
    background-color: rgba(5, 16, 30, 232);
    border: 1px solid #32577E;
    border-radius: 8px;
    selection-background-color: #1F70CE;
}
QLineEdit#nuova_comunicazione_passaggio:focus,
QLineEdit#modifica_comunicazione_passaggio:focus { border-color: #5FA6F2; }

QPushButton#aggiungi_passaggio {
    min-height: 34px;
    padding: 4px 14px;
    color: #FFFFFF;
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 8px;
    font-weight: 600;
}
QPushButton#aggiungi_passaggio:hover { background-color: #2C80DF; }
QPushButton#storico_passaggio,
QPushButton#riduci_passaggio,
QPushButton#fissa_passaggio,
QPushButton#archivia_passaggio {
    min-height: 28px;
    color: #C6D3E6;
    background-color: rgba(31, 112, 206, 28);
    border: 1px solid #32577E;
    border-radius: 7px;
    padding: 2px 9px;
}
QPushButton#storico_passaggio:hover,
QPushButton#riduci_passaggio:hover,
QPushButton#fissa_passaggio:hover {
    color: #FFFFFF;
    background-color: rgba(31, 112, 206, 70);
    border-color: #4A83BC;
}
/* Il pulsante di fissaggio acceso **e'** il badge importante in
   miniatura: stesso oro, stesso testo scuro. Cambia solo la
   presentazione — callback, stato e significato restano quelli di
   sempre. La regola con hover esiste perche' senza di lei l'hover
   generico riportava al blu un pulsante gia' acceso, facendo sembrare
   spento cio' che era attivo. */
QPushButton#fissa_passaggio:checked {
    color: #182334;
    background-color: #E7BB67;
    border-color: #F1D08B;
    font-weight: 700;
}
QPushButton#fissa_passaggio:checked:hover {
    color: #182334;
    background-color: #F1D08B;
    border-color: #FBE4B4;
}
QPushButton#archivia_passaggio:hover {
    color: #FFFFFF;
    background-color: rgba(201, 90, 90, 78);
    border-color: #A85D64;
}

QDialog#storico_passaggio_modern_control_room,
QDialog#dettaglio_passaggio_modern_control_room {
    background-color: #0B1E35;
    color: #F2F2F2;
}
QDialog#storico_passaggio_modern_control_room QScrollArea,
QDialog#storico_passaggio_modern_control_room QScrollArea > QWidget > QWidget,
QWidget#contenuto_storico_passaggio {
    background: transparent;
    border: none;
}
QLabel#sezione_storico_passaggio {
    color: #9FC8F2;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding-top: 10px;
}
QLabel#nota_storico_passaggio,
QLabel#metadati_passaggio { color: #9FB3CE; font-size: 12px; }
QLabel#stato_vuoto_storico_passaggio {
    color: #AEBED2;
    padding: 12px;
}
QFrame#riga_storico_passaggio {
    background-color: rgba(8, 21, 39, 220);
    border: 1px solid rgba(87, 134, 182, 92);
    border-radius: 9px;
}
QFrame#riga_storico_passaggio:hover {
    background-color: rgba(31, 112, 206, 42);
    border-color: #527EAE;
}
QFrame#riga_storico_passaggio[fissato="true"] {
    background-color: rgba(26, 32, 43, 226);
    border: 1px solid rgba(231, 187, 103, 128);
    border-left: 3px solid #E7BB67;
}
QFrame#riga_storico_passaggio[fissato="true"]:hover {
    background-color: rgba(43, 50, 60, 234);
    border-color: rgba(241, 208, 139, 166);
    border-left: 3px solid #F1D08B;
}
QLabel#testo_storico_passaggio,
QLabel#testo_dettaglio_passaggio {
    color: #F2F2F2;
    font-size: 14px;
    font-weight: 600;
}
QDialog#storico_passaggio_modern_control_room QPushButton,
QDialog#dettaglio_passaggio_modern_control_room QPushButton {
    min-height: 32px;
    padding: 4px 14px;
    color: #FFFFFF;
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 8px;
    font-weight: 600;
}
QDialog#storico_passaggio_modern_control_room QPushButton:hover,
QDialog#dettaglio_passaggio_modern_control_room QPushButton:hover {
    background-color: #2C80DF;
}

QScrollBar:vertical {
    background: rgba(5, 16, 30, 122);
    width: 10px;
    margin: 2px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #365F89;
    min-height: 26px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover { background: #4D7EAE; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0px;
    background: transparent;
}
"""
