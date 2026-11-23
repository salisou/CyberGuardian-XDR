from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt
from modules.process_monitor.service import list_processes

class ProcessMonitor(QWidget):
    HEADERS = ["PID", "Name", "Path", "User", "CPU %", "RAM %", "Status"]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search processes…")
        self.search.textChanged.connect(self.populate)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.populate)
        bar.addWidget(self.search)
        bar.addWidget(refresh)
        layout.addLayout(bar)
        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        self.populate()

    def populate(self):
        query = self.search.text().casefold()
        rows = list_processes()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for row in rows:
            values = [row["pid"], row["name"], row["path"], row["user"],
                      f'{row["cpu"]:.1f}', f'{row["memory"]:.2f}', row["status"]]
            if query and query not in " ".join(map(str, values)).casefold():
                continue
            index = self.table.rowCount()
            self.table.insertRow(index)
            for col, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                if col in (0, 4, 5):
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(index, col, cell)
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
