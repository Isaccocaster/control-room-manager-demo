"""Documentazione della versione portfolio."""

BLU_NAVY = "#0B1E39"
BLU_NAVY_SCURO = "#081527"
GRIGIO_PANNELLO = "#3A3F47"
GRIGIO_PANNELLO_BORDO = "#4F5560"
AZZURRO_BOTTONE = "#1B3A63"
AZZURRO_BOTTONE_HOVER = "#274E82"
BORDO_BOTTONE = "#2C4F82"
TESTO_CHIARO = "#F2F2F2"
TESTO_ATTENUATO = "#B8C4D9"


COLORE_AVVISO = "#FF8A73"


HOME_OPACITA_VELO = 180
FOGLIO_DI_STILE_HOME = """
QWidget#home_control_room {
    font-family: "Segoe UI";
    color: #F2F2F2;
}
QScrollArea#area_home, QWidget#viewport_home, QWidget#contenuto_home,
QFrame#pannello_home {
    background: transparent;
    border: none;
}
QLabel#titolo_control_room {
    font-size: 36px;
    font-weight: 700;
    color: #F2F2F2;
}
QLabel#sottotitolo_control_room {
    font-size: 17px;
    color: #B8C4D9;
}
QFrame#card_modulo_home {
    background-color: rgba(11, 30, 53, 176);
    border: 1px solid rgba(87, 134, 182, 120);
    border-radius: 16px;
}
QFrame#card_modulo_home:hover {
    background-color: rgba(17, 42, 70, 205);
    border-color: #527EAE;
}
QWidget#testo_card_home, QWidget#azioni_card_home {
    background: transparent;
    border: none;
}
QLabel#nome_modulo_home {
    font-size: 20px;
    font-weight: 600;
    color: #F2F2F2;
}
QLabel#icona_modulo_home {
    background-color: rgba(22, 49, 78, 165);
    border: 1px solid #32577E;
    border-radius: 12px;
}
QLabel#descrizione_modulo_home {
    font-size: 15px;
    color: #C0CEE2;
}
/* Badge operativo della card: stesso linguaggio visivo di quello della
   sidebar (`QLabel#badge_voce_sidebar`) — stesso colore d'allarme, stesso
   significato "qualcosa richiede attenzione". Cambiano solo dimensioni e
   raggio, adattati alla card: un badge non deve voler dire due cose
   diverse a seconda di dove lo si guarda. */
QLabel#badge_modulo_home {
    background-color: rgba(255,138,115,40);
    color: #FF8A73;
    border: 1px solid rgba(255,138,115,140);
    border-radius: 13px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#apri_modulo_home {
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 10px;
    padding: 8px 14px;
    min-height: 24px;
    font-size: 15px;
    font-weight: 600;
    color: #FFFFFF;
}
QPushButton#apri_modulo_home:hover { background-color: #2C80DF; }
QPushButton#apri_modulo_home:pressed { background-color: #1958A4; }
QPushButton#apri_modulo_home:focus { border: 2px solid #C0E3FF; padding: 7px 13px; }
QScrollBar:vertical {
    background: rgba(8, 21, 39, 150);
    width: 10px;
    margin: 0;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #47698C;
    min-height: 36px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover { background: #6486A8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""


LARGHEZZA_SIDEBAR_ESTESA = 240
LARGHEZZA_SIDEBAR_COMPATTA = 56
FOGLIO_DI_STILE_SIDEBAR = """
QFrame#sidebar_moduli {
    background-color: #081527;
    border-right: 1px solid #32577E;
}
QScrollArea#area_sidebar, QWidget#viewport_sidebar, QWidget#contenuto_sidebar,
QWidget#fondo_sidebar {
    background: transparent;
    border: none;
}
/* Il bordo sinistro esiste sempre, trasparente: cambia solo colore quando
   la voce e' attiva, cosi' il contenuto non si sposta di 3 px. E' il segnale
   che sopravvive alla modalita' compatta, dove l'etichetta sparisce. */
QFrame#voce_sidebar {
    border-left: 3px solid transparent;
    border-top: 0; border-right: 0; border-bottom: 0;
    border-radius: 10px;
    background: transparent;
}
QFrame#voce_sidebar:hover { background-color: rgba(31,112,206,26); }
QFrame#voce_sidebar[attiva="true"] {
    background-color: rgba(31,112,206,41);
    border-left: 3px solid #1F70CE;
}
QLabel#etichetta_voce_sidebar { color: #B8C4D9; font-size: 14px; }
QFrame#voce_sidebar:hover QLabel#etichetta_voce_sidebar { color: #F2F2F2; }
QFrame#voce_sidebar[attiva="true"] QLabel#etichetta_voce_sidebar {
    color: #F2F2F2;
    font-weight: 600;
}
QLabel#badge_voce_sidebar {
    background-color: rgba(255,138,115,40);
    border: 1px solid rgba(255,138,115,140);
    border-radius: 11px;
    color: #FF8A73;
    font-size: 11px;
    font-weight: 600;
    padding: 1px 7px;
}
QLabel#titolo_gruppo_sidebar {
    color: #7E90AB;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 1px;
}
QFrame#separatore_sidebar { background-color: rgba(87,134,182,60); border: none; }
QScrollBar:vertical {
    background: transparent; width: 8px; margin: 0; border-radius: 4px;
}
QScrollBar::handle:vertical { background: #47698C; min-height: 30px; border-radius: 4px; }
QScrollBar::handle:vertical:hover { background: #6486A8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""


ACCENTO_CALENDARIO = "#C0E3FF"
SFONDO_GIORNO_CON_EVENTI = "#16314E"


SFONDO_CALENDARIO = "#0D2340"
TESTO_CALENDARIO = "#C6D3E6"
TESTO_CALENDARIO_SPENTO = "#5A6B85"
INTESTAZIONE_CALENDARIO = "#8299B5"
FOGLIO_DI_STILE_CALENDARIO = """
QWidget#calendario_modern_control_room,
QStackedWidget#pagine_calendario,
QWidget#pagina_calendario,
QWidget#pagina_giornata,
QWidget#barra_calendario,
QWidget#contenitore_anteprima_calendario,
QWidget#intestazione_giornata_calendario,
QScrollArea#elenco_eventi_calendario,
QScrollArea#elenco_eventi_calendario > QWidget > QWidget,
QWidget#contenuto_eventi_calendario {
    background: transparent;
    border: none;
}

QLabel#mese_calendario {
    font-size: 19px;
    font-weight: 600;
    letter-spacing: 1px;
    color: #F2F2F2;
}
QPushButton#freccia_calendario {
    min-width: 34px; max-width: 34px;
    min-height: 34px; max-height: 34px;
    padding: 0;
    font-size: 17px;
    font-weight: 600;
    color: #B8C4D9;
    background: transparent;
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#freccia_calendario:hover { background-color: rgba(31,112,206,36); color: #F2F2F2; }
/* Secondario per scelta: e' una comodita', non il comando della schermata. */
QPushButton#oggi_calendario {
    padding: 7px 14px;
    font-size: 12.5px;
    color: #B8C4D9;
    background: transparent;
    border: 1px solid #32577E;
    border-radius: 9px;
}
QPushButton#oggi_calendario:hover { background-color: rgba(31,112,206,36); color: #F2F2F2; }

/* Il riquadro di questa schermata usa la superficie Modern Control Room,
   non il grigio del pannello globale: la regola vale solo qui, perche' il
   foglio e' applicato alla sola SchermataCalendarioOperativo. */
QFrame#pannello_home {
    background-color: rgba(11, 30, 53, 176);
    border: 1px solid rgba(87, 134, 182, 120);
    border-radius: 16px;
}
/* Dimensione del testo e griglia: il resto (fondo, testo, selezione) passa
   dalla tavolozza, perche' le celle sono disegnate dalla vista interna e il
   foglio di stile non le raggiunge. */
QCalendarWidget#calendario_operativo QAbstractItemView {
    outline: none;
    font-size: 16px;
    gridline-color: rgba(87, 134, 182, 60);
}

QLabel#anteprima_data { font-size: 16px; font-weight: 600; color: #F2F2F2; }
QLabel#anteprima_conteggio { font-size: 13px; color: #C0E3FF; }
QLabel#riga_anteprima { font-size: 13px; color: #B8C4D9; }
QLabel#numero_anteprima {
    background-color: rgba(31,112,206,48);
    border: 1px solid rgba(95,166,242,72);
    border-radius: 11px;
    padding: 2px 9px;
    min-width: 28px;
    min-height: 22px;
    font-size: 12.5px;
    font-weight: 600;
    color: #F2F2F2;
}
QLabel#nota_anteprima { font-size: 11px; color: #7E90AB; }
QPushButton#apri_giornata {
    background-color: #1F70CE;
    border: 1px solid #3988E1;
    border-radius: 10px;
    padding: 11px 14px;
    font-size: 14px;
    font-weight: 600;
    color: #FFFFFF;
}
QPushButton#apri_giornata:hover { background-color: #2C80DF; }
QPushButton#apri_giornata:pressed { background-color: #1958A4; }

/* Ritorno discreto: un comando, non l'azione principale della pagina. */
QPushButton#torna_al_calendario {
    padding: 6px 13px;
    font-size: 13px;
    color: #B8C4D9;
    background: transparent;
    border: 1px solid rgba(87,134,182,90);
    border-radius: 8px;
}
QPushButton#torna_al_calendario:hover { background-color: rgba(31,112,206,36); color: #F2F2F2; }

QLabel#titolo_giornata { font-size: 20px; font-weight: 600; color: #F2F2F2; }
QLabel#titolo_modulo_giornata {
    font-size: 13px;
    font-weight: 600;
    color: #C0E3FF;
    padding-top: 6px;
}
"""

FOGLIO_DI_STILE = f"""
QMainWindow, QWidget {{
    background-color: {BLU_NAVY};
    color: {TESTO_CHIARO};
    font-size: 14px;
}}

QLabel {{
    background: transparent;
}}

QPushButton {{
    background-color: {AZZURRO_BOTTONE};
    color: {TESTO_CHIARO};
    border: 1px solid {BORDO_BOTTONE};
    border-radius: 6px;
    padding: 10px 16px;
}}

QPushButton:hover {{
    background-color: {AZZURRO_BOTTONE_HOVER};
}}

QPushButton:checked {{
    background-color: {AZZURRO_BOTTONE_HOVER};
    border: 1px solid {TESTO_CHIARO};
}}

QLineEdit {{
    background-color: {BLU_NAVY_SCURO};
    color: {TESTO_CHIARO};
    border: 1px solid {BORDO_BOTTONE};
    border-radius: 4px;
    padding: 5px;
}}

QFrame#intestazione {{
    background-color: {BLU_NAVY_SCURO};
    border-bottom: 1px solid {BORDO_BOTTONE};
}}

QFrame#fascia_inferiore {{
    background-color: {BLU_NAVY_SCURO};
    border: none;
}}

QWidget#alloggio_passaggio_inferiore {{
    background: transparent;
    border: none;
}}

QLabel#credito_powered_by_tony {{
    color: #718096;
    font-size: 10px;
    letter-spacing: 0.3px;
    background: transparent;
}}

QFrame#barra_passaggio_consegne {{
    background: transparent;
    border: none;
}}

/* Variante agganciata al fondo della sidebar estesa: non e' piu' una
   striscia a tutta larghezza ma un riquadro dentro una colonna, quindi
   perde il bordo superiore e prende gli angoli arrotondati delle altre
   superfici Modern Control Room. Stesso widget, stesso stato. */
QFrame#barra_passaggio_consegne[variante="sidebar"] {{
    background-color: rgba(31, 112, 206, 28);
    border: 1px solid #32577E;
    border-radius: 10px;
}}

QFrame#pannello_home {{
    background-color: {GRIGIO_PANNELLO};
    border: 1px solid {GRIGIO_PANNELLO_BORDO};
    border-radius: 18px;
}}

QFrame#notepad_passaggio_consegne {{
    background-color: {GRIGIO_PANNELLO};
    border: 1px solid {GRIGIO_PANNELLO_BORDO};
    border-radius: 10px;
}}

/* Badge del Passaggio di Consegne. La veste completa sta nel foglio del
   modulo (`ui/passaggio_consegne/stile.py`), che ha la precedenza: qui
   restano le sole regole che servono quando il pannello e' disegnato con
   il foglio globale — il contenitore trasparente e la forma a pillola,
   cosi' i badge non ricadono mai sul fondo navy pieno di `QWidget`. */
QWidget#indicatore_passaggio_consegne {{
    background: transparent;
    border: none;
}}
QLabel#badge_normali_passaggio {{
    color: #DCEBFF;
    background-color: rgba(31, 112, 206, 92);
    border: 1px solid #3988E1;
    border-radius: 11px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QFrame#badge_importanti_passaggio,
QFrame#chip_importante_passaggio {{
    background-color: #E7BB67;
    border: 1px solid #F1D08B;
    border-radius: 11px;
    padding: 3px 10px;
}}
QFrame#badge_importanti_passaggio QLabel#testo_priorita_passaggio,
QFrame#chip_importante_passaggio QLabel#testo_priorita_passaggio {{
    color: #10233C;
    background: transparent;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#icona_priorita_passaggio {{ background: transparent; border: none; }}

QPushButton#pulsante_home {{
    min-height: 46px;
    font-size: 15px;
}}

QFrame#riga_risultato_chiave {{
    background-color: rgba(255, 255, 255, 18);
    border-radius: 6px;
}}

/* Rapporto aperto dal Calendario Operativo: si consulta, non si modifica.
   Contrassegno sobrio, non un avviso di errore. */
QLabel#etichetta_sola_lettura {{
    background-color: rgba(31, 112, 206, 40);
    border: 1px solid #32577E;
    border-radius: 11px;
    padding: 3px 12px;
    font-size: 12px;
    color: #C0E3FF;
}}

QPushButton#torna_al_calendario {{
    padding: 6px 13px;
    font-size: 13px;
    color: {TESTO_ATTENUATO};
    background: transparent;
    border: 1px solid rgba(87, 134, 182, 90);
    border-radius: 8px;
}}
QPushButton#torna_al_calendario:hover {{
    background-color: rgba(31, 112, 206, 36);
    color: {TESTO_CHIARO};
}}
"""
