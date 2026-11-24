from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QStackedWidget, QVBoxLayout, QWidget,
)

from ui.ai_assistant import AIAssistantPage
from ui.alert_center import AlertCenterPage
from ui.dashboard import Dashboard
from ui.event_viewer import EventViewerPage
from ui.forensics import ForensicsPage
from ui.malware_analysis import MalwareAnalysisPage
from ui.network_monitor import NetworkMonitor
from ui.process_monitor import ProcessMonitor
from ui.reports import ReportsPage
from ui.threat_intel import ThreatIntelligencePage
from ui.vulnerability_scanner import VulnerabilityScannerPage


PAGE_GROUPS = (
    ("OVERVIEW", (("Dashboard", Dashboard),)),
    ("MONITOR", (
        ("Alert Center", AlertCenterPage),
        ("Processes", ProcessMonitor),
        ("Network", NetworkMonitor),
        ("Event Viewer", EventViewerPage),
    )),
    ("INVESTIGATE", (
        ("Threat Intelligence", ThreatIntelligencePage),
        ("Vulnerability Scanner", VulnerabilityScannerPage),
        ("Malware Analysis", MalwareAnalysisPage),
        ("Forensics", ForensicsPage),
    )),
    ("REPORTS & TOOLS", (
        ("Reports", ReportsPage),
        ("AI Assistant", AIAssistantPage),
    )),
)

PAGE_DESCRIPTIONS = {
    "Dashboard": "Host health and live telemetry.",
    "Alert Center": "Security event correlation and triage.",
    "Processes": "Process inventory and resource usage.",
    "Network": "Current connection inventory.",
    "Event Viewer": "Windows event log review.",
    "Threat Intelligence": "Indicator reputation lookups.",
    "Vulnerability Scanner": "Authorized TCP service assessment.",
    "Malware Analysis": "File hashes and optional YARA analysis.",
    "Forensics": "File metadata and integrity inventory.",
    "Reports": "Local security event exports.",
    "AI Assistant": "Local inference with Ollama.",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberGuardian XDR")
        self.setMinimumSize(1080, 700)
        self.resize(1440, 900)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(248)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 20, 16, 16)
        side.setSpacing(0)

        brand = QHBoxLayout()
        brand.setSpacing(10)
        brand_mark = QLabel("CG")
        brand_mark.setObjectName("BrandMark")
        brand_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_mark.setFixedSize(38, 38)
        brand.addWidget(brand_mark)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(1)
        brand_name = QLabel("CyberGuardian")
        brand_name.setObjectName("BrandName")
        brand_text.addWidget(brand_name)
        brand_subtitle = QLabel("XDR CONSOLE")
        brand_subtitle.setObjectName("BrandSubtitle")
        brand_text.addWidget(brand_subtitle)
        brand.addLayout(brand_text)
        brand.addStretch()
        side.addLayout(brand)
        side.addSpacing(18)

        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("NavScroll")
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_content = QWidget()
        nav_content.setObjectName("NavContent")
        nav_layout = QVBoxLayout(nav_content)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)

        self.stack = QStackedWidget()
        self.stack.setObjectName("PageStack")
        self.pages = {}
        self.page_factories = {}
        self.buttons = {}

        for group_name, entries in PAGE_GROUPS:
            group_label = QLabel(group_name)
            group_label.setObjectName("NavGroup")
            nav_layout.addWidget(group_label)
            for name, page_factory in entries:
                self.page_factories[name] = page_factory
                button = QPushButton(name)
                button.setObjectName("NavButton")
                button.setCheckable(True)
                button.setMinimumHeight(40)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.clicked.connect(lambda checked=False, page=name: self.navigate(page))
                nav_layout.addWidget(button)
                self.buttons[name] = button
            nav_layout.addSpacing(10)
        nav_layout.addStretch()
        nav_scroll.setWidget(nav_content)
        side.addWidget(nav_scroll, 1)

        footer_rule = QFrame()
        footer_rule.setObjectName("SidebarRule")
        footer_rule.setFrameShape(QFrame.Shape.HLine)
        side.addWidget(footer_rule)
        footer_label = QLabel("Defensive security workspace")
        footer_label.setObjectName("SidebarFooter")
        footer_label.setWordWrap(True)
        side.addWidget(footer_label)
        root.addWidget(sidebar)

        content_frame = QFrame()
        content_frame.setObjectName("Content")
        content = QVBoxLayout(content_frame)
        content.setContentsMargins(28, 22, 28, 24)
        content.setSpacing(18)

        page_header = QHBoxLayout()
        page_heading = QVBoxLayout()
        page_heading.setSpacing(4)
        self.title = QLabel("Dashboard")
        self.title.setObjectName("PageTitle")
        page_heading.addWidget(self.title)
        self.description = QLabel(PAGE_DESCRIPTIONS["Dashboard"])
        self.description.setObjectName("PageDescription")
        page_heading.addWidget(self.description)
        page_header.addLayout(page_heading)
        page_header.addStretch()
        workspace_badge = QLabel("LOCAL CONSOLE")
        workspace_badge.setObjectName("WorkspaceBadge")
        workspace_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_header.addWidget(workspace_badge, 0, Qt.AlignmentFlag.AlignVCenter)
        content.addLayout(page_header)

        divider = QFrame()
        divider.setObjectName("ContentDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        content.addWidget(divider)
        content.addWidget(self.stack, 1)
        root.addWidget(content_frame, 1)

        self.navigate("Dashboard")

    def navigate(self, name):
        if name not in self.pages:
            page = self.page_factories[name]()
            page_layout = page.layout()
            if page_layout is not None:
                page_layout.setContentsMargins(0, 0, 0, 0)
                page_layout.setSpacing(14)
            self.pages[name] = page
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.pages[name])
        self.title.setText(name)
        self.description.setText(PAGE_DESCRIPTIONS[name])
        for key, button in self.buttons.items():
            button.setChecked(key == name)
