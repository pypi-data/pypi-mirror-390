import os, webbrowser, json, threading, time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QListWidget, QStackedWidget, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer
import qtawesome as qta
from core import server_manager, file_editor, db_manager, autostart

from ui.tabs.projects_tab import ProjectsTab
from ui.tabs.editor_tab import EditorTab
from ui.tabs.database_tab import DatabaseTab
from ui.tabs.logs_tab import LogsTab

class PyPanelMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyPanel Pro')
        self.setGeometry(80, 60, 1100, 700)
        self.init_ui()
        # restore running servers state
        self.server_manager = server_manager.manager
        self.poll_timer = QTimer()
        self.poll_timer.setInterval(500)
        self.poll_timer.timeout.connect(self.refresh_status)
        self.poll_timer.start()

    def init_ui(self):
        layout = QVBoxLayout()
        top = QHBoxLayout()
        title = QLabel('<h2>PyPanel Pro</h2>')
        top.addWidget(title)
        top.addStretch()

        btn_quit = QPushButton(qta.icon('fa.sign-out'), 'Quitter')
        btn_quit.clicked.connect(self.close)
        top.addWidget(btn_quit)
        layout.addLayout(top)

        main_split = QSplitter(Qt.Horizontal)
        left = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left)
        # sidebar buttons
        self.btn_projects = QPushButton(qta.icon('fa.folder'), 'Projets')
        self.btn_editor = QPushButton(qta.icon('fa.code'), 'Éditeur')
        self.btn_db = QPushButton(qta.icon('fa.database'), 'Bases de données')
        self.btn_logs = QPushButton(qta.icon('fa.terminal'), 'Logs')

        for b in (self.btn_projects, self.btn_editor, self.btn_db, self.btn_logs):
            b.setCheckable(True)
            left.addWidget(b)

        left.addStretch()

        main_split.addWidget(left_widget)

        # content stack
        self.stack = QStackedWidget()
        self.projects_tab = ProjectsTab(self)
        self.editor_tab = EditorTab(self)
        self.db_tab = DatabaseTab(self)
        self.logs_tab = LogsTab(self)

        self.stack.addWidget(self.projects_tab)
        self.stack.addWidget(self.editor_tab)
        self.stack.addWidget(self.db_tab)
        self.stack.addWidget(self.logs_tab)

        main_split.addWidget(self.stack)
        main_split.setStretchFactor(1, 4)
        layout.addWidget(main_split)
        self.setLayout(layout)

        # connect buttons
        self.btn_projects.clicked.connect(lambda: self.switch_tab(0))
        self.btn_editor.clicked.connect(lambda: self.switch_tab(1))
        self.btn_db.clicked.connect(lambda: self.switch_tab(2))
        self.btn_logs.clicked.connect(lambda: self.switch_tab(3))
        # default
        self.btn_projects.setChecked(True)
        self.switch_tab(0)

    def switch_tab(self, idx):
        for b in (self.btn_projects, self.btn_editor, self.btn_db, self.btn_logs):
            b.setChecked(False)
        (self.btn_projects, self.btn_editor, self.btn_db, self.btn_logs)[idx].setChecked(True)
        self.stack.setCurrentIndex(idx)

    def refresh_status(self):
        # refresh project list, ports and running state
        try:
            self.projects_tab.refresh_list()
            # update logs tab process output
            self.logs_tab.poll_processes()
        except Exception:
            pass

    def closeEvent(self, event):
        # stop servers on close
        self.server_manager.stop_all()
        event.accept()
