import sys
from PyQt6.QtWidgets import QApplication
from core.database import initialize_database
from core.logger import configure_logging, get_logger
from ui.main_window import MainWindow
from ui.styles import load_stylesheet

def main() -> int:
    configure_logging()
    try:
        initialize_database()
        app = QApplication(sys.argv)
        app.setApplicationName('CyberGuardian XDR')
        app.setOrganizationName('CyberGuardian')
        app.setStyleSheet(load_stylesheet())
        window = MainWindow()
        window.show()
        get_logger(__name__).info('Application started')
        return app.exec()
    except Exception:
        get_logger(__name__).exception('Fatal startup error')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
