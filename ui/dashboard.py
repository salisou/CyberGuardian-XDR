from collections import deque
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from core.system_info import collect_system_metrics
from core.threat_score import ThreatInputs, calculate_threat_score
from core.logger import get_logger

class MetricCard(QFrame):
    def __init__(self, title):
        super().__init__(); self.setProperty('card', True); layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title)); self.value = QLabel('—')
        self.value.setStyleSheet('font-size:22pt;font-weight:600;'); layout.addWidget(self.value)

class Dashboard(QWidget):
    def __init__(self):
        super().__init__(); root = QVBoxLayout(self); grid = QGridLayout(); self.cards = {}
        for i, title in enumerate(('CPU', 'RAM', 'Disk', 'Threat Score', 'Processes', 'Connections')):
            card = MetricCard(title); self.cards[title] = card; grid.addWidget(card, i // 3, i % 3)
        root.addLayout(grid); self.figure = Figure(figsize=(8, 3), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure); self.ax = self.figure.add_subplot(111)
        self.cpu, self.ram = deque(maxlen=60), deque(maxlen=60); root.addWidget(self.canvas)
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(1000); self.refresh()
    def refresh(self):
        try:
            m = collect_system_metrics(); score = calculate_threat_score(ThreatInputs(cpu_percent=m['cpu_percent'], memory_percent=m['memory_percent'], open_connections=m['connection_count']))
            values = {'CPU': f\"{m['cpu_percent']:.1f}%\", 'RAM': f\"{m['memory_percent']:.1f}%\", 'Disk': f\"{m['disk_percent']:.1f}%\", 'Threat Score': f'{score.score}/100 · {score.level}', 'Processes': str(m['process_count']), 'Connections': str(m['connection_count'])}
            for key, value in values.items(): self.cards[key].value.setText(value)
            self.cpu.append(m['cpu_percent']); self.ram.append(m['memory_percent']); self.ax.clear(); self.ax.set_facecolor('#1e1e1e')
            self.ax.plot(list(self.cpu), label='CPU'); self.ax.plot(list(self.ram), label='RAM'); self.ax.set_ylim(0, 100)
            self.ax.tick_params(colors='#c9d1d9'); self.ax.legend(facecolor='#1e1e1e', labelcolor='#e6edf3')
            self.ax.set_title('Live CPU / RAM utilization', color='#e6edf3'); self.figure.patch.set_facecolor('#121212'); self.canvas.draw_idle()
        except Exception: get_logger(__name__).exception('Dashboard refresh failed')
