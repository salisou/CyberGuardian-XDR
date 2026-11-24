from collections import deque
from datetime import datetime
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from core.system_info import collect_system_metrics
from core.threat_score import ThreatInputs, calculate_threat_score
from core.alert_engine import count_open_alerts
from core.logger import get_logger


class MetricCard(QFrame):
    def __init__(self, title, description):
        super().__init__()
        self.setProperty("card", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("MetricTitle")
        layout.addWidget(title_label)
        self.value = QLabel("—")
        self.value.setObjectName("MetricValue")
        layout.addWidget(self.value)
        description_label = QLabel(description)
        description_label.setObjectName("MetricDescription")
        layout.addWidget(description_label)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.addStretch()
        self.update_status = QLabel("Waiting for first update")
        self.update_status.setObjectName("UpdateStatus")
        header.addWidget(self.update_status)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("RefreshButton")
        self.refresh_button.clicked.connect(self.refresh)
        header.addWidget(self.refresh_button)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.cards = {}
        metrics = (
            ("CPU", "Processor utilization"),
            ("RAM", "Memory in use"),
            ("Disk", "System disk used"),
            ("Threat Score", "Current risk assessment"),
            ("Processes", "Active processes"),
            ("Connections", "Open network connections"),
            ("Open Alerts", "Alerts requiring attention"),
        )
        for i, (name, description) in enumerate(metrics):
            card = MetricCard(name, description)
            self.cards[name] = card
            grid.addWidget(card, i // 4, i % 4)
        root.addLayout(grid)

        chart_card = QFrame()
        chart_card.setProperty("card", True)
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(16, 14, 16, 12)
        chart_layout.setSpacing(4)
        chart_title = QLabel("Resource utilization")
        chart_title.setObjectName("ChartTitle")
        chart_layout.addWidget(chart_title)
        chart_caption = QLabel("CPU and memory · recent samples")
        chart_caption.setObjectName("DashboardCaption")
        chart_layout.addWidget(chart_caption)
        self.figure = Figure(figsize=(8, 3.2), tight_layout=True)
        self.figure.patch.set_facecolor("#1e1e1e")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(250)
        self.ax = self.figure.add_subplot(111)
        chart_layout.addWidget(self.canvas)
        root.addWidget(chart_card, 1)

        self.cpu, self.ram = deque(maxlen=60), deque(maxlen=60)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    def refresh(self):
        try:
            metrics = collect_system_metrics()
            assessment = calculate_threat_score(ThreatInputs(
                cpu_percent=metrics["cpu_percent"],
                memory_percent=metrics["memory_percent"],
                open_connections=metrics["connection_count"]))
            open_alerts = count_open_alerts()
            values = {
                "CPU": f'{metrics["cpu_percent"]:.1f}%',
                "RAM": f'{metrics["memory_percent"]:.1f}%',
                "Disk": f'{metrics["disk_percent"]:.1f}%',
                "Processes": str(metrics["process_count"]),
                "Connections": str(metrics["connection_count"]),
                "Open Alerts": str(open_alerts),
            }
            for key, value in values.items():
                self.cards[key].value.setText(value)
            severity = assessment.level.lower()
            score_value = self.cards["Threat Score"].value
            score_value.setText(f'{assessment.score}/100 · {assessment.level}')
            score_value.setProperty("severity", severity)
            score_value.style().unpolish(score_value)
            score_value.style().polish(score_value)

            self.cpu.append(metrics["cpu_percent"])
            self.ram.append(metrics["memory_percent"])
            self.update_status.setText(
                f"Updated {datetime.now().astimezone().strftime('%H:%M:%S')}"
            )
            self.ax.clear()
            self.ax.set_facecolor("#1e1e1e")
            self.ax.plot(list(self.cpu), label="CPU", color="#58a6ff", linewidth=2)
            self.ax.plot(list(self.ram), label="Memory", color="#3fb950", linewidth=2)
            self.ax.set_ylim(0, 100)
            self.ax.set_ylabel("Utilization (%)", color="#8b949e")
            self.ax.set_xlabel("Recent samples", color="#8b949e")
            self.ax.tick_params(colors="#8b949e")
            self.ax.grid(axis="y", color="#30363d", linewidth=0.8)
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.ax.spines["bottom"].set_color("#30363d")
            self.ax.spines["left"].set_color("#30363d")
            self.ax.legend(
                facecolor="#1e1e1e",
                edgecolor="#30363d",
                labelcolor="#e6edf3",
                framealpha=1,
            )
            self.canvas.draw_idle()
        except Exception:
            self.update_status.setText("Update failed · see application logs")
            get_logger(__name__).exception("Dashboard refresh failed")
