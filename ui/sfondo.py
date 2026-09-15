"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from ui.tema import BLU_NAVY

OPACITA_VELO_PREDEFINITA = 70


def colore_con_alpha(colore_esadecimale: str, alpha: int) -> QColor:
    colore = QColor(colore_esadecimale)
    colore.setAlpha(alpha)
    return colore


class PaginaConSfondo(QWidget):
    """Documentazione della versione portfolio."""

    def __init__(self, percorso_foto, opacita_velo: int = OPACITA_VELO_PREDEFINITA):
        super().__init__()
        self._foto_sfondo = QPixmap(str(percorso_foto))
        self._opacita_velo = opacita_velo

    def paintEvent(self, event):
        painter = QPainter(self)

        if not self._foto_sfondo.isNull():
            foto_scalata = self._foto_sfondo.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - foto_scalata.width()) // 2
            y = (self.height() - foto_scalata.height()) // 2
            painter.drawPixmap(x, y, foto_scalata)

        painter.fillRect(self.rect(), colore_con_alpha(BLU_NAVY, self._opacita_velo))
