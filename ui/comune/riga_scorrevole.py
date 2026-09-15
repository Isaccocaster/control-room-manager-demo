"""Documentazione della versione portfolio."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QSizePolicy, QWidget


def riga_scorrevole(riga: QWidget) -> QScrollArea:
    """Documentazione della versione portfolio."""
    area = QScrollArea()
    area.setObjectName("riga_scorrevole")
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    area.setStyleSheet(
        "QScrollArea#riga_scorrevole, QScrollArea#riga_scorrevole > QWidget > QWidget"
        " { background: transparent; border: none; }"
    )
    area.setWidget(riga)

    altezza_barra = area.horizontalScrollBar().sizeHint().height()
    area.setFixedHeight(riga.sizeHint().height() + altezza_barra)


    area.setMinimumWidth(0)
    area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
    return area
