"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QLabel


def crea_etichetta_logo(altezza_px: int, colore) -> QLabel:
    """Documentazione della versione portfolio."""
    larghezza = max(altezza_px * 2, 72)
    pixmap = QPixmap(larghezza, altezza_px)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    font = QFont("Arial")
    font.setPixelSize(max(16, int(altezza_px * 0.56)))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(colore))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "CR")
    painter.end()
    etichetta = QLabel()
    etichetta.setPixmap(pixmap)
    etichetta.resize(pixmap.size())
    etichetta.setAccessibleName("Control Room Manager Demo")
    return etichetta
