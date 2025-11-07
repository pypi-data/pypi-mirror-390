import os, json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                             QTextEdit, QLabel, QMessageBox)
from core import file_editor, server_manager
from PyQt5.QtCore import QTimer
import webbrowser

class EditorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_project = None
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        row = QHBoxLayout()
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.on_project_select)
        row.addWidget(self.project_list, 1)

        file_col = QVBoxLayout()
        self.files_list = QListWidget()
        self.files_list.itemClicked.connect(self.on_file_select)
        file_col.addWidget(QLabel('Fichiers'))
        file_col.addWidget(self.files_list, 1)

        self.editor = QTextEdit()
        file_col.addWidget(QLabel('Éditeur'))
        file_col.addWidget(self.editor, 3)

        ops = QHBoxLayout()
        btn_save = QPushButton('💾 Enregistrer')
        btn_save.clicked.connect(self.save_file)
        ops.addWidget(btn_save)
        btn_preview = QPushButton('Aperçu')
        btn_preview.clicked.connect(self.preview)
        ops.addWidget(btn_preview)

        file_col.addLayout(ops)
        row.addLayout(file_col, 3)
        layout.addLayout(row)
        self.setLayout(layout)
        self.refresh_projects_timer = QTimer()
        self.refresh_projects_timer.setInterval(800)
        self.refresh_projects_timer.timeout.connect(self.refresh_projects)
        self.refresh_projects_timer.start()

    def refresh_projects(self):
        self.project_list.clear()
        for p in server_manager.manager.list_projects():
            self.project_list.addItem(p)

    def on_project_select(self, item):
        self.current_project = item.text()
        self.refresh_files()

    def refresh_files(self):
        if not self.current_project:
            return
        self.files_list.clear()
        for f in file_editor.list_files(self.current_project):
            self.files_list.addItem(f)

    def on_file_select(self, item):
        self.current_file = item.text()
        try:
            content = file_editor.read_file(self.current_project, self.current_file)
            self.editor.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', str(e))

    def save_file(self):
        if not (self.current_project and self.current_file):
            QMessageBox.warning(self, 'Info', 'Sélectionne un fichier.')
            return
        try:
            file_editor.write_file(self.current_project, self.current_file, self.editor.toPlainText())
            QMessageBox.information(self, 'Sauvé', 'Fichier enregistré.')
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', str(e))

    def preview(self):
        if not self.current_project:
            QMessageBox.warning(self, 'Info', 'Sélectionne un projet.')
            return
        # ensure project server running
        port = server_manager.manager.config.get('projects', {}).get(self.current_project, {}).get('port')
        if not port:
            port = server_manager.manager.start_server(self.current_project)
        webbrowser.open(f'http://127.0.0.1:{port}/{self.current_file}')
