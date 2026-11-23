from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton
from modules.network_monitor.service import list_connections

class NetworkMonitor(QWidget):
    HEADERS = ['Proto', 'Local Address', 'Remote Address', 'Status', 'PID']
    def __init__(self):
        super().__init__(); layout = QVBoxLayout(self); bar = QHBoxLayout(); self.search = QLineEdit()
        self.search.setPlaceholderText('Filter connections…'); self.search.textChanged.connect(self.populate)
        refresh = QPushButton('Refresh'); refresh.clicked.connect(self.populate); bar.addWidget(self.search); bar.addWidget(refresh); layout.addLayout(bar)
        self.table = QTableWidget(0, len(self.HEADERS)); self.table.setHorizontalHeaderLabels(self.HEADERS); self.table.setAlternatingRowColors(True); layout.addWidget(self.table); self.populate()
    def populate(self):
        query = self.search.text().casefold(); self.table.setRowCount(0)
        for row in list_connections():
            values = [row['protocol'], row['local'], row['remote'], row['status'], row['pid'] or '']
            if query and query not in ' '.join(map(str, values)).casefold(): continue
            index = self.table.rowCount(); self.table.insertRow(index)
            for col, value in enumerate(values): self.table.setItem(index, col, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
