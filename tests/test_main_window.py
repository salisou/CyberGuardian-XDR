import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget

import ui.main_window as main_window
from ui.styles import load_stylesheet


def test_pages_load_on_first_navigation_and_are_reused(monkeypatch):
    class StubPage(QWidget):
        pass

    monkeypatch.setattr(
        main_window,
        "PAGE_GROUPS",
        (
            ("OVERVIEW", (("Dashboard", StubPage),)),
            ("MONITOR", (("Processes", StubPage),)),
        ),
    )
    monkeypatch.setattr(
        main_window,
        "PAGE_DESCRIPTIONS",
        {"Dashboard": "Overview", "Processes": "Process list"},
    )
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(load_stylesheet())

    window = main_window.MainWindow()
    assert set(window.pages) == {"Dashboard"}

    window.navigate("Processes")
    processes_page = window.pages["Processes"]
    assert window.stack.currentWidget() is processes_page
    assert window.buttons["Processes"].isChecked()

    window.navigate("Processes")
    assert window.pages["Processes"] is processes_page
    window.close()
    app.processEvents()
