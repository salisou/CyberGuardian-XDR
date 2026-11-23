from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QLabel, QStackedWidget
from ui.dashboard import Dashboard
from ui.process_monitor import ProcessMonitor
from ui.network_monitor import NetworkMonitor
from ui.threat_intel import ThreatIntelligencePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberGuardian XDR")
        self.resize(1440, 900)
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        side = QVBoxLayout(sidebar)
        brand = QLabel("CYBERGUARDIAN\nXDR")
        brand.setStyleSheet("font-size:17pt;font-weight:700;color:#58a6ff;padding:12px;")
        side.addWidget(brand)
        self.stack = QStackedWidget()
        self.pages = {}
        self.buttons = {}
        pages = [
            ("Dashboard", Dashboard()),
            ("Processes", ProcessMonitor()),
            ("Network", NetworkMonitor()),
            ("Threat Intelligence", ThreatIntelligencePage()),
        ]
        for name, page in pages:
            self.pages[name] = page
            self.stack.addWidget(page)
            button = QPushButton(name)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, n=name: self.navigate(n))
            side.addWidget(button)
            self.buttons[name] = button
        for name in ("System Monitor", "Event Viewer", "Vulnerability Scanner",
                     "Malware Analysis", "Forensics", "Reports", "AI Assistant", "Settings"):
            button = QPushButton(name + " · Not enabled yet")
            button.setEnabled(False)
            side.addWidget(button)
        side.addStretch()
        side.addWidget(QLabel("Defensive monitoring · Read-only"))
        root.addWidget(sidebar)
        content = QVBoxLayout()
        self.title = QLabel("Dashboard")
        self.title.setObjectName("PageTitle")
        content.addWidget(self.title)
        content.addWidget(self.stack)
        root.addLayout(content, 1)
        self.navigate("Dashboard")

    def navigate(self, name):
        self.stack.setCurrentWidget(self.pages[name])
        self.title.setText(name)
        for key, button in self.buttons.items():
            button.setChecked(key == name)
