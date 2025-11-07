"""
Main Textual application for aidex.

This module contains the main TUI application built with Textual.
"""

import click
from textual.app import App, ComposeResult

"""
An App to show the current time.
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Digits


class AidexApp(App):
    CSS = """
    Screen { align: center middle; }
    Digits { width: auto; }
    """

    def compose(self) -> ComposeResult:
        yield Digits("")

    def on_ready(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")


@click.command()
@click.version_option(package_name="aidex")
def main() -> None:
    """Aidex - A terminal UI application."""
    app = AidexApp()
    app.run()


if __name__ == "__main__":
    main()
