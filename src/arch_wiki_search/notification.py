#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QFont
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLineEdit, QWidget, QVBoxLayout

try:
    from __init__ import __name__, __version__, __icon__
except ModuleNotFoundError:
    from arch_wiki_search import __name__, __version__, __icon__

class NotifIcon(QSystemTrayIcon):
    """Portable notification area icon that opens a menu with 1 entry per wiki and a
    search function
    PyQT6 so runs on Windows (Intel and ARM), macOS (Intel and Apple Silicon) and Linux (Intel and ARM)
    """

    def __init__(self):
        # generate icon from utf-8 character
        pixmap = QPixmap(64, 64) #TODO: see how portable that looks
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setFont(QFont('Arial', 50))
        painter.drawText(pixmap.rect(), 0, __icon__)
        painter.end()
        self.icon = QIcon(pixmap)

        super().__init__(self.icon)
        self.setToolTip(f'{__name__} {__version__}')
        self.menu = QMenu()
        self.search_action = QAction('Search')
        self.search_action.triggered.connect(self.show_search_box)
        self.menu.addAction(self.search_action)
        self.exit_action = QAction('Exit')
        self.exit_action.triggered.connect(QApplication.quit)
        self.menu.addAction(self.exit_action)
        self.setContextMenu(self.menu)

    def show_search_box(self):
        self.search_widget = QWidget()
        self.search_widget.setWindowTitle('Search')
        layout = QVBoxLayout()
        self.search_box = QLineEdit()
        layout.addWidget(self.search_box)
        self.search_widget.setLayout(layout)
        self.search_widget.show()

    @staticmethod
    def start(stopFlag):
        qt6app = QApplication(sys.argv)
        notificon = NotifIcon()
        notificon.show()
        qt6app.exec()
        stopFlag = True
