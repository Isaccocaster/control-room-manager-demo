"""Documentazione della versione portfolio."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


SIMBOLI_MODULI = {
    "Rapporto Giornaliero": '<path d="M7 3h11l7 7v19H7z M18 3v8h7 M11 16h10 M11 21h10 M11 25h6"/>',
    "Bacheca Chiavi": '<circle cx="21" cy="10" r="7"/><circle cx="23" cy="8" r="1"/><path d="M16 15L3 28v2h5v-4h4v-4h4l4-5"/>',
    "Consegna Radio": '<rect x="8" y="10" width="16" height="20" rx="3"/><path d="M12 10V2 M20 10V6 M12 25h8"/><rect x="12" y="14" width="8" height="7" rx="1"/>',
    "Gestione Radio": '<rect x="12" y="10" width="14" height="20" rx="2"/><path d="M16 10V2 M22 10V6 M16 25h6 M8 7H4v19h4 M6 7V3"/><rect x="16" y="14" width="6" height="6" rx="1"/>',
    "Anagrafica Operatori": '<circle cx="16" cy="9" r="5"/><path d="M6 29v-5c0-5 4-9 10-9s10 4 10 9v5 M11 22h10 M16 19v6"/>',
    "Oggetti Smarriti": '<rect x="3" y="10" width="26" height="19" rx="2"/><path d="M11 10V5h10v5 M7 15h2 M12 15h2"/>',
    "Cassaforte": '<rect x="3" y="3" width="26" height="26" rx="3"/><path d="M7 7v18 M8 29v2 M24 29v2"/><circle cx="19" cy="16" r="7"/><circle cx="19" cy="16" r="2"/>',
    "Calendario Operativo": '<rect x="3" y="6" width="26" height="24" rx="3"/><path d="M9 2v8 M23 2v8 M3 13h26 M9 19h2 M16 19h2 M23 19h1 M9 25h2 M16 25h2"/>',
    "Impostazioni": '<path d="M13 2h6l1 4 3 2 4-1 3 5-3 3v3l3 3-3 5-4-1-3 2-1 4h-6l-1-4-3-2-4 1-3-5 3-3v-3l-3-3 3-5 4 1 3-2z"/><circle cx="16" cy="16" r="5"/>',
}

SIMBOLO_STORICO = '<path d="M7 3h11l7 7v19H7z M18 3v8h7 M11 15h10 M11 20h5"/><circle cx="20" cy="24" r="5"/><path d="M20 21v3l2 1"/>'
SIMBOLO_CICLI = '<path d="M25 11a10 10 0 0 0-17-3L5 11 M5 6v5h5 M7 21a10 10 0 0 0 17 3l3-3 M27 26v-5h-5"/>'


def pixmap_simbolo(simbolo: str, lato: int, colore: str = "#C6D3E6", punto: str | None = None) -> QPixmap:
    """Documentazione della versione portfolio."""
    segnale = f'<circle cx="27" cy="6" r="4.5" fill="{punto}" stroke="none"/>' if punto else ""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 34">'
        f'<g fill="none" stroke="{colore}" stroke-width="1.9" '
        f'stroke-linecap="round" stroke-linejoin="round">{simbolo}</g>{segnale}</svg>'
    )
    pixmap = QPixmap(lato * 2, lato * 2)
    pixmap.fill(Qt.transparent)
    pittore = QPainter(pixmap)
    pittore.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(svg.encode("utf-8")).render(pittore)
    pittore.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap


def icona_simbolo(simbolo: str, lato: int = 18, colore: str = "#C6D3E6") -> QIcon:
    return QIcon(pixmap_simbolo(simbolo, lato, colore))


def applica_icona_pulsante(pulsante, simbolo: str, lato: int = 17, colore: str = "#C6D3E6") -> None:
    """Documentazione della versione portfolio."""
    pulsante.setIcon(icona_simbolo(simbolo, lato, colore))
    pulsante.setIconSize(QSize(lato, lato))
