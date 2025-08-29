#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

import sys
import asyncio
from textual import on
from textual.binding import Binding
from textual.screen import Screen
from textual.command import CommandPalette
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Button, Label, Placeholder, Footer
from textual.containers import VerticalScroll, Horizontal

from arch_wiki_search import __icon__, PACKAGE_NAME, __version__, __logger__

class TXTIcon(App):
    """Will display a start bar and start button like icon in console mode to search and stop the proxy
    Textual runs on Linux, Windows and OS/X
    """
    
    CSS = '''
        Screen {
            layout: vertical;
            background: transparent;
        }
        #footer {
            height: 1;
            dock: bottom;
        }
        Footer {
            height: 1;
            background: transparent;
        }
    '''

    def on_mount(self) -> None:
        self.title = f'{PACKAGE_NAME.replace('_', '-')} {__version__}'

    def action_exit(self) -> None:
        #TODO: write stop flag
        self.exit(0)

    BINDINGS = [
        ('ctrl+x', 'exit', 'Exit'),
        ('ctrl+s', 'search', 'TODO: search'),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id='scroll'):
            pass
            # yield Placeholder(id='placeholder')
        with Horizontal(id='footer'):
            yield Label(f' {__icon__}', id='icon')
            with Horizontal(id='footer-inner'):
                yield Footer()

def main():
    TXTIcon().run()

if __name__ == '__main__':
    sys.exit(main())

