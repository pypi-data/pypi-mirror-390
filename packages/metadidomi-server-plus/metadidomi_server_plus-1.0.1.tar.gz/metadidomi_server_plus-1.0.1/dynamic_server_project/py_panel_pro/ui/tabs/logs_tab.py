from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton
from core import server_manager

class LogsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        btn_clear = QPushButton('Effacer')
        btn_clear.clicked.connect(lambda: self.log.clear())
        layout.addWidget(btn_clear)
        self.setLayout(layout)

    def poll_processes(self):
        # read outputs from running servers
        mgr = server_manager.manager
        for name, srv in mgr._servers.items():
            if srv and srv.proc and srv.proc.stdout:
                try:
                    for line in iter(srv.proc.stdout.readline, ''):
                        if line:
                            self.log.appendPlainText(f'[{name}] ' + line.rstrip())
                        else:
                            break
                except Exception:
                    pass
